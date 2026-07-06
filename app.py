import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Mosquito Control Dashboard", layout="wide")

# Custom CSS styling to mimic the beautiful rounded cards and colors of image_c3a3fe.png
st.markdown("""
    <style>
    .main { background-color: #F7F5EB; }
    .header-banner {
        background-color: #112D32;
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #257F73;
        margin-bottom: 15px;
    }
    .metric-val {
        font-size: 36px;
        font-weight: 800;
        color: #112D32;
    }
    .metric-lbl {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- LIVE DATAFRAME STORAGE (Real-time memory) ---
# This initializes your dashboard with your existing file data
if "db" not in st.session_state:
    try:
        # Load your historical data from MOSQUITO CONTOL - SUMMARY REPORT JUNE 2026.xlsx
        initial_df = pd.read_excel("MOSQUITO CONTOL - SUMMARY REPORT JUNE 2026.xlsx", sheet_name='Sheet1', skiprows=1)
        initial_df.columns = [c.strip() for c in initial_df.columns]
        # Quick clean up of text coordinate symbols
        initial_df['Latitude'] = initial_df['Latitude'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        initial_df['Longitude'] = initial_df['Longitude'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        st.session_state.db = initial_df
    except:
        # Fallback if file isn't found locally
        st.session_state.db = pd.DataFrame(columns=['Date', 'Larvae Name', 'Description', 'Found Area', 'Area', 'Latitude', 'Longitude'])

df = st.session_state.db

# --- MAIN HEADER BANNER (Matches image_c3a3fe.png style) ---
st.markdown("""
    <div class="header-banner">
        <div>
            <h1 style='margin:0; font-size: 32px;'>Monthly Report</h1>
            <p style='margin:0; opacity: 0.8;'>Mosquito Control & Environmental Operations • Emirate of Ras Al Khaimah</p>
        </div>
        <div style='background-color: #257F73; padding: 15px 25px; border-radius: 10px; text-align: center;'>
            <span style='display:block; font-size:24px; font-weight:bold;'>June</span>
            <span style='font-size:12px;'>2026</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- DATA ENTRY PANEL (Collapsible Form Sidebar) ---
st.sidebar.header("➕ Add Field Inspection Record")
with st.sidebar.form(key="inspection_form", clear_on_submit=True):
    new_date = st.date_input("Inspection Date", datetime.date(2026, 6, 2))
    new_larvae = st.selectbox("Larvae Name Found", ["No Larvae", "Aedes", "Culex, Aedes", "Culex, Anopheles"])
    new_desc = st.selectbox("Action Description", ["Inspected", "Inspected & Treated"])
    new_found = st.selectbox("Breeding Ground / Found Area", ["-", "Buckets", "Water Tank", "Stagnant water", "Tire", "Drum", "Fountain"])
    new_area = st.text_input("Area / Sector Name", placeholder="e.g. Al Araibi")
    new_lat = st.number_input("Latitude", value=25.7594, format="%.6f")
    new_lon = st.number_input("Longitude", value=55.9358, format="%.6f")
    
    submit_button = st.form_submit_form_button = st.form_submit_button(label="Submit to Live Dashboard")

# Append new data instantly on submit
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

# --- RE-AGGREGATE METRICS FROM LIVE DB ---
total_inspections = len(df)
positive_cases = len(df[df['Larvae Name'] != 'No Larvae'])
treated_sites = len(df[df['Description'].str.contains('Treated', case=False, na=False)])

# --- KPI METRIC CARDS (Top row of widgets) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Field Inspections</div><div class="metric-val">{total_inspections}</div></div>', unsafe_with_html=True)
with col2:
    st.markdown(f'<div class="metric-card" style="border-left-color: #E05638;"><div class="metric-lbl">Positive Larval Detections</div><div class="metric-val">{positive_cases}</div></div>', unsafe_with_html=True)
with col3:
    st.markdown(f'<div class="metric-card" style="border-left-color: #38A3A5;"><div class="metric-lbl">Active Treatments Completed</div><div class="metric-val">{treated_sites}</div></div>', unsafe_with_html=True)

st.markdown("---")

# --- VISUAL CHARTS & MAPS SECTION ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📊 Larvae Species Split")
    fig_pie = px.pie(df, names='Larvae Name', color_discrete_sequence=px.colors.sequential.Teal_r, hole=0.4)
    fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

with right_col:
    st.subheader("📍 Geospatial Vector Map")
    # Interactive Mapbox map zooming right to your locations
    fig_map = px.scatter_mapbox(
        df, lat="Latitude", lon="Longitude", 
        color="Larvae Name", size=[10]*len(df),
        hover_name="Area", hover_data=["Description", "Found Area"],
        zoom=10, height=350
    )
    fig_map.update_layout(mapbox_style="carto-positron")
    fig_map.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_map, use_container_width=True)

# --- RAW ACTIVITY LOG SHEET (Bottom of screen) ---
st.markdown("### 📋 Live Operational Inspection Stream Log")
st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
