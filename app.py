import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="EcoRoute")
st.title("🌿 EcoRoute: Carbon Tax Optimization Dashboard")

# Define our exact list of available Mississauga hubs
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
weekly_trips = st.sidebar.slider("Expected Weekly Trips", min_value=1, max_value=20, value=5)

# Creates 3 Layout Columns
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

    # Route-Specific Navigation Itineraries (Dynamic Text matching directional pairs)
    # Key format is directional: "From-To"
    itinerary_key = f"{origin.split(' (')[0]}➔{destination.split(' (')[0]}"
    
    itineraries = {
        "UTM➔Square One Shopping Centre": [
            "🚶 Walk 3 mins to UTM Transit Terminal (Platform 1).",
            "🚌 Board MiWay Express Route 110 Northbound.",
            "⏱️ Ride 6 stops (approx 16 mins).",
            "🏁 Arrive at City Centre Transit Terminal (Square One)."
        ],
        "Square One Shopping Centre➔UTM": [
            "🚶 Walk 2 mins to City Centre Transit Terminal (Platform O).",
            "🚌 Board MiWay Express Route 110 Southbound.",
            "⏱️ Ride 6 stops (approx 17 mins).",
            "🏁 Arrive at UTM Transit Terminal."
        ],
        "Port Credit GO➔UTM": [
            "🚶 Head to Port Credit GO Bus Terminal.",
            "🚌 Take MiWay Route 14 Westbound toward Clarkson.",
            "🔄 Transfer at South Common Centre to MiWay Route 101 East.",
            "🏁 Arrive at UTM Transit Terminal."
        ],
        "UTM➔Port Credit GO": [
            "🚌 Take MiWay Route 101 West from UTM to South Common Centre.",
            "🔄 Transfer to MiWay Route 14 Eastbound.",
            "⏱️ Ride down to Mississauga Rd / Lakeshore Rd.",
            "🏁 Arrive at Port Credit GO Station."
        ],
        "Erin Mills Town Centre➔UTM": [
            "🚌 Board MiWay Route 13 Southbound from Erin Mills Town Centre.",
            "⏱️ Ride for approx 12 mins down South Millway.",
            "🏁 Arrive directly at UTM Campus Loop."
        ],
        "UTM➔Erin Mills Town Centre": [
            "🚌 Board MiWay Route 13 Northbound from UTM Campus Loop.",
            "⏱️ Ride for approx 14 mins.",
            "🏁 Arrive at Erin Mills Town Centre Transit Hub."
        ]
    }
    
    # Fallback default directions if the inverse pair sequence isn't fully written out
    current_itinerary = itineraries.get(itinerary_key, [
        "🚌 Board connecting MiWay local transit service line.",
        "⏱️ Transfer routes dynamically to complete transit loop.",
        "🏁 Arrive safely at destination hub."
    ])

    # Carbon Tax Calculation Logic
    car_emissions_kg = (distance_km * 200) / 1000
    transit_emissions_kg = (distance_km * 40) / 1000
    single_co2_saved = car_emissions_kg - transit_emissions_kg
    single_tax_saved = distance_km * 0.15

    # Scales Projections Logic
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

    # Column 2: Map & Custom Expander Route Breakdown
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
        
        st_folium(m, use_container_width=True, height=400, key=f"map_{origin}_{destination}")
        
        # 🚌 Dynamic Expandable Dropdown Tray right beneath the map
        st.write("")
        with st.expander("🚌 View Live MiWay Transit Route Details", expanded=True):
            for step in current_itinerary:
                st.write(step)

    # Column 3: Optimization Wallet
    with col3:
        st.subheader("💰 Optimization Wallet")
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