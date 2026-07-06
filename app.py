import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from io import BytesIO

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Mosquito Control Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F3F4F6; } 
    .header-banner {
        background-color: #374151;
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-bottom: 5px solid #F97316;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #F97316;
        margin-bottom: 15px;
    }
    .metric-val {
        font-size: 36px;
        font-weight: 800;
        color: #1F2937;
    }
    .metric-lbl {
        font-size: 12px;
        color: #6B7280;
        text-transform: uppercase;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- BRANDED COLOR DICTIONARY MAP ---
# Exact match request: No Larvae (Green), Culex (Yellow), Anopheles (Purple), Aedes (Red)
color_map = {
    "No Larvae": "#22C55E",          # Clean Green
    "Aedes": "#EF4444",              # Warning Red
    "Culex": "#EAB308",              # Bright Yellow
    "Anopheles": "#A855F7",          # Deep Purple
    "Culex, Aedes": "#F97316",       # Blend Orange
    "Culex, Anopheles": "#6B21A8"    # Blend Dark Purple
}

# --- SPREADSHEET MANAGER (Live File Upload & Memory) ---
st.sidebar.header("📁 Base Spreadsheet Manager")
uploaded_file = st.sidebar.file_uploader("Upload or reset base Excel sheet", type=["xlsx"])

# Set initial data if a file is dropped into the portal sidebar
if uploaded_file is not None:
    try:
        uploaded_df = pd.read_excel(uploaded_file, sheet_name='Sheet1', skiprows=1)
        uploaded_df.columns = [c.strip() for c in uploaded_df.columns]
        uploaded_df['Latitude'] = uploaded_df['Latitude'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        uploaded_df['Longitude'] = uploaded_df['Longitude'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        st.session_state.db = uploaded_df
        st.sidebar.success("New Excel data loaded successfully!")
    except Exception as e:
        st.sidebar.error("Error reading file layout. Verify sheet format.")

# Global state fallback pipeline
if "db" not in st.session_state:
    try:
        initial_df = pd.read_excel("MOSQUITO CONTOL - SUMMARY REPORT JUNE 2026.xlsx", sheet_name='Sheet1', skiprows=1)
        initial_df.columns = [c.strip() for c in initial_df.columns]
        initial_df['Latitude'] = initial_df['Latitude'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        initial_df['Longitude'] = initial_df['Longitude'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        st.session_state.db = initial_df
    except:
        st.session_state.db = pd.DataFrame(columns=['Date', 'Larvae Name', 'Description', 'Found Area', 'Area', 'Latitude', 'Longitude'])

df = st.session_state.db

# --- MAIN HEADER BANNER ---
st.markdown("""
    <div class="header-banner">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div>
                <h1 style='margin:0; font-size: 34px;'>Mosquito Control Data</h1>
                <p style='margin:0; opacity: 0.85;'>Overall Environmental Operations • Emirate of Ras Al Khaimah</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR RECORD ENTRY FORM ---
st.sidebar.markdown("---")
st.sidebar.header("➕ Add Field Inspection Record")

with st.sidebar.form(key="inspection_form", clear_on_submit=True):
    new_date = st.date_input("Inspection Date", datetime.date(2026, 6, 2))
    
    # Extended list values requested
    new_larvae = st.selectbox("Larvae Name Found", ["No Larvae", "Aedes", "Culex", "Anopheles", "Culex, Aedes", "Culex, Anopheles"])
    new_desc = st.selectbox("Action Description", ["Inspected", "Inspected & Treated"])
    
    # Found options with "Other" trigger flag
    new_found_dropdown = st.selectbox("Breeding Ground / Found Area", ["-", "Buckets", "Water Tank", "Stagnant water", "Tire", "Drum", "Fountain", "Other"])
    
    # Smart conditional display happens inside form natively
    other_text = st.text_input("If 'Other', please specify below:", placeholder="Type location details here...")
    
    new_area = st.text_input("Area / Sector Name", placeholder="e.g. Al Araibi")
    new_lat = st.number_input("Latitude", value=25.7594, format="%.6f")
    new_lon = st.number_input("Longitude", value=55.9358, format="%.6f")
    
    submit_button = st.form_submit_button(label="Submit to Live Dashboard")

if submit_button:
    # Set final field based on whether custom value was keyed in
    final_found_area = other_text if new_found_dropdown == "Other" and other_text.strip() != "" else new_found_dropdown
    
    new_row = {
        'Date': pd.to_datetime(new_date),
        'Larvae Name': new_larvae,
        'Description': new_desc,
        'Found Area': final_found_area,
        'Area': new_area,
        'Latitude': float(new_lat),
        'Longitude': float(new_lon)
    }
    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
    st.rerun()

# --- METRIC RE-AGGREGATION ---
total_inspections = len(df)
positive_cases = len(df[df['Larvae Name'] != 'No Larvae'])
treated_sites = len(df[df['Description'].str.contains('Treated', case=False, na=False)])

# --- KPI METRIC CARDS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card" style="border-left-color: #9CA3AF;"><div class="metric-lbl">Total Field Inspections</div><div class="metric-val">{total_inspections}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card" style="border-left-color: #F97316;"><div class="metric-lbl">Positive Larval Detections</div><div class="metric-val">{positive_cases}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card" style="border-left-color: #4B5563;"><div class="metric-lbl">Active Treatments Completed</div><div class="metric-val">{treated_sites}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# --- VISUAL CHARTS & MAPS ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📊 Larvae Species Split")
    if not df.empty:
        fig_pie = px.pie(df, names='Larvae Name', color='Larvae Name', color_discrete_map=color_map, hole=0.4)
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("No data available yet.")

with right_col:
    st.subheader("📍 Geospatial Vector Map")
    if not df.empty:
        fig_map = px.scatter_mapbox(
            df, lat="Latitude", lon="Longitude", 
            color="Larvae Name", size=[10]*len(df),
            color_discrete_map=color_map,
            hover_name="Area", hover_data=["Description", "Found Area"],
            zoom=10, height=350
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        fig_map.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("No geographic coordinates logged yet.")

# --- RAW ACTIVITY LOG SHEET ---
st.markdown("---")
st.markdown("### 🛠️ Data Management Center")

edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor_grid")

if not edited_df.equals(df):
    st.session_state.db = edited_df
    st.rerun()

buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    edited_df.to_excel(writer, sheet_name='Sheet1', index=False)

st.download_button(
    label="📥 Download Updated Summary Report (.xlsx)",
    data=buffer.getvalue(),
    file_name="MOSQUITO_CONTROL_SUMMARY_REPORT_UPDATED.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
