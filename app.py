import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Mosquito Control Dashboard", layout="wide")

# Custom CSS styling updated to match your Orange, White, and Grey corporate identity
st.markdown("""
    <style>
    /* Light Grey Background for the whole website */
    .main { background-color: #F3F4F6; } 
    
    /* Dark Slate Grey Banner with an Orange accent border */
    .header-banner {
        background-color: #374151;
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-bottom: 5px solid #F97316;
    }
    
    /* Pure White Cards with an Orange indicator bar */
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

# --- LIVE DATAFRAME STORAGE (Real-time memory) ---
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

# --- MAIN HEADER BANNER (Branded Orange & Grey, No Month Block) ---
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

# --- DATA ENTRY PANEL ---
# Automatically display your logo file at the top of the sidebar panel if it exists
try:
    st.sidebar.image("logo.png", use_container_width=True)
except:
    pass

st.sidebar.header("➕ Add Field Inspection Record")
with st.sidebar.form(key="inspection_form", clear_on_submit=True):
    new_date = st.date_input("Inspection Date", datetime.date(2026, 6, 2))
    new_larvae = st.selectbox("Larvae Name Found", ["No Larvae", "Aedes", "Culex, Aedes", "Culex, Anopheles"])
    new_desc = st.selectbox("Action Description", ["Inspected", "Inspected & Treated"])
    new_found = st.selectbox("Breeding Ground / Found Area", ["-", "Buckets", "Water Tank", "Stagnant water", "Tire", "Drum", "Fountain"])
    new_area = st.text_input("Area / Sector Name", placeholder="e.g. Al Araibi")
    new_lat = st.number_input("Latitude", value=25.7594, format="%.6f")
    new_lon = st.number_input("Longitude", value=55.9358, format="%.6f")
    
    submit_button = st.form_submit_button(label="Submit to Live Dashboard")

if submit_button:
    new_row = {
        'Date': pd.to_datetime(new_date),
        'Larvae Name': new_larvae,
        'Description': new_desc,
        'Found Area': new_found,
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
        # Pie chart updated to match an Orange and Grey sequence
        orange_grey_palette = ['#9CA3AF', '#F97316', '#4B5563', '#D1D5DB']
        fig_pie = px.pie(df, names='Larvae Name', color_discrete_sequence=orange_grey_palette, hole=0.4)
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
            color_discrete_sequence=['#9CA3AF', '#F97316', '#4B5563', '#374151'],
            hover_name="Area", hover_data=["Description", "Found Area"],
            zoom=10, height=350
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        fig_map.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("No geographic coordinates logged yet.")

# --- RAW ACTIVITY LOG SHEET ---
st.markdown("### 📋 Live Operational Inspection Stream Log")
st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
