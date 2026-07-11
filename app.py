import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="EcoRoute")
st.title("🌿 EcoRoute: Carbon Tax Optimization Dashboard")

# Defines the exact list of available Mississauga hubs
locations = [
    "UTM (University of Toronto Mississauga)",
    "Square One Shopping Centre",
    "Port Credit GO",
    "Erin Mills Town Centre"
]

# Sidebar Inputs
st.sidebar.title("📍 Route Configuration")
origin = st.sidebar.selectbox("Origin", locations, index=0)
destination = st.sidebar.selectbox("Destination", locations, index=1)

st.sidebar.markdown("---")
st.sidebar.title("🔮 Projections Parameter")
# 🎚️ What-If Parameter Slider (Default to 5 trips/week, max 20)
weekly_trips = st.sidebar.slider("Expected Weekly Trips", min_value=1, max_value=20, value=5)

# Create 3 Layout Columns
col1, col2, col3 = st.columns([1.1, 1.8, 1.1], gap="medium")

if origin == destination:
    with col2:
        st.warning("⚠️ Please select a different destination. Origin and destination cannot be the same!")
else:
    # Matrix Data Engine
    pair_key = "-".join(sorted([origin, destination]))
    
    matrix_data = {
        "Erin Mills Town Centre-Square One Shopping Centre": [8.5, 14, 25],
        "Erin Mills Town Centre-UTM (University of Toronto Mississauga)": [6.8, 10, 18],
        "Erin Mills Town Centre-Port Credit GO": [15.2, 22, 45],
        "Port Credit GO-Square One Shopping Centre": [7.8, 15, 28],
        "Port Credit GO-UTM (University of Toronto Mississauga)": [11.5, 18, 35],
        "Square One Shopping Centre-UTM (University of Toronto Mississauga)": [7.2, 12, 22]
    }
    
    distance_km, drive_time, transit_time = matrix_data.get(pair_key, [5.0, 10, 20])

    # 🌿 Carbon Tax Calculation Logic (Single Trip)
    car_emissions_kg = (distance_km * 200) / 1000
    transit_emissions_kg = (distance_km * 40) / 1000
    single_co2_saved = car_emissions_kg - transit_emissions_kg
    single_tax_saved = distance_km * 0.15

    # 📈 Scaled Projections Logic (Using the slider input)
    weekly_tax_saved = single_tax_saved * weekly_trips
    annual_tax_saved = weekly_tax_saved * 52
    
    weekly_co2_saved = single_co2_saved * weekly_trips
    annual_co2_saved = weekly_co2_saved * 52

    # Column 1: Trip Metrics
    with col1:
        st.subheader("📊 Single Trip Metrics")
        with st.container(border=True):
            st.metric(label="Total Distance", value=f"{distance_km} km")
        with st.container(border=True):
            st.metric(label="🚗 Driving Duration", value=f"{drive_time} mins")
        with st.container(border=True):
            st.metric(label="🚌 Transit Duration", value=f"{transit_time} mins")

    # Column 2: Map Integration
    with col2:
        st.subheader("🗺️ Mississauga Transit Map")
        
        coordinates = {
            "UTM (University of Toronto Mississauga)": [43.5479, -79.6612],
            "Square One Shopping Centre": [43.5931, -79.6425],
            "Port Credit GO": [43.5557, -79.5869],
            "Erin Mills Town Centre": [43.5413, -79.7180]
        }
        
        start_coords = coordinates[origin]
        end_coords = coordinates[destination]
        
        center_lat = (start_coords[0] + end_coords[0]) / 2
        center_lon = (start_coords[1] + end_coords[1]) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB dark_matter")
        
        folium.Marker(location=start_coords, popup="Origin", icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(location=end_coords, popup="Destination", icon=folium.Icon(color="red", icon="stop")).add_to(m)
        folium.PolyLine(locations=[start_coords, end_coords], color="#39FF14", weight=4, opacity=0.8).add_to(m)
        
        st_folium(m, use_container_width=True, height=480, key=f"map_{origin}_{destination}")

    # Column 3: Optimization Wallet (With New Dynamic Projections!)
    with col3:
        st.subheader("💰 Optimization Wallet")
        
        # Tabs let us split single trip metrics from long-term forecasts smoothly
        tab1, tab2 = st.tabs(["📅 Weekly Outlook", "🏢 Annual Forecast"])
        
        with tab1:
            with st.container(border=True):
                st.metric(label="Weekly Tax Saved", value=f"${weekly_tax_saved:.2f}", delta=f"{weekly_trips} trips/wk")
            with st.container(border=True):
                st.metric(label="Weekly CO2 Avoided", value=f"{weekly_co2_saved:.2f} kg", delta="📉 Mitigated", delta_color="inverse")
                
        with tab2:
            with st.container(border=True):
                st.metric(label="Projected Annual Savings", value=f"${annual_tax_saved:.2f}", delta="🏆 Financial ROI")
            with st.container(border=True):
                st.metric(label="Projected Annual CO2 Avoided", value=f"{annual_co2_saved:.2f} kg", delta="🌲 High Impact", delta_color="inverse")