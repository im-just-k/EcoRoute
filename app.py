import streamlit as st

st.set_page_config(layout="wide", page_title="EcoRoute")
st.title("🌿 EcoRoute: Carbon Tax Optimization Dashboard")

# Define our list of available Mississauga hubs
locations = ["UTM (University of Toronto Mississauga)", "Square One Shopping Centre", "Port Credit GO", "Erin Mills Town Centre"]

# Sidebar Inputs - Both now use the full list!
st.sidebar.title("📍 Route Configuration")
origin = st.sidebar.selectbox("Origin", locations, index=0)
destination = st.sidebar.selectbox("Destination", locations, index=1)

# Create 3 Layout Columns
col1, col2, col3 = st.columns([1, 2, 1])

# Check if Origin and Destination are identical
if origin == destination:
    with col2:
        st.warning("⚠️ Please select a different destination. Origin and destination cannot be the same!")
else:
    # Matrix Data Engine (Simulating real-world routing distance data between all hubs)
    # This structure calculates a baseline distance based on the alphabetical order pair to simulate real routing
    pair_key = "-".join(sorted([origin.split(" (")[0], destination.split(" (")[0]]))
    
    # Pre-calculated mock distances/times for all possible combinations
    matrix_data = {
        "Erin Mills Town Centre-Square One": [8.5, 14, 25],
        "Erin Mills Town Centre-UTM": [6.8, 10, 18],
        "Erin Mills Town Centre-Port Credit GO": [15.2, 22, 45],
        "Port Credit GO-Square One": [7.8, 15, 28],
        "Port Credit GO-UTM": [11.5, 18, 35],
        "Square One-UTM": [7.2, 12, 22]
    }
    
    # Fetch metrics safely
    distance_km, drive_time, transit_time = matrix_data.get(pair_key, [5.0, 10, 20])

    # Carbon Tax Calculation Logic
    car_emissions_kg = (distance_km * 200) / 1000
    transit_emissions_kg = (distance_km * 40) / 1000
    co2_saved_kg = car_emissions_kg - transit_emissions_kg
    tax_saved_dollars = distance_km * 0.15

    with col1:
        st.subheader("📊 Trip Metrics")
        st.metric(label="Total Distance", value=f"{distance_km} km")
        st.metric(label="🚗 Driving Duration", value=f"{drive_time} mins")
        st.metric(label="🚌 Transit Duration", value=f"{transit_time} mins")

    with col2:
        st.subheader("🗺️ Mississauga Transit Map")
        
        # 📌 Coordinates dictionary for our hubs
        coordinates = {
            "UTM (University of Toronto Mississauga)": [43.5479, -79.6612],
            "Square One Shopping Centre": [43.5931, -79.6425],
            "Port Credit GO": [43.5557, -79.5869],
            "Erin Mills Town Centre": [43.5413, -79.7180]
        }
        
        # Pull coordinates for our selected endpoints
        start_coords = coordinates[origin]
        end_coords = coordinates[destination]
        
        # Initialize an interactive map centered right between your two points
        import folium
        from streamlit_folium import st_folium
        
        center_lat = (start_coords[0] + end_coords[0]) / 2
        center_lon = (start_coords[1] + end_coords[1]) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB dark_matter")
        
        # Add markers for Origin and Destination
        folium.Marker(location=start_coords, popup=f"Origin: {origin}", icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(location=end_coords, popup=f"Destination: {destination}", icon=folium.Icon(color="red", icon="stop")).add_to(m)
        
        # Draw a straight connecting route line for visualization
        folium.PolyLine(locations=[start_coords, end_coords], color="#39FF14", weight=4, opacity=0.8).add_to(m)
        
        # Render the map into Streamlit!
        st_folium(m, width=None, height=450, key=f"map_{origin}_{destination}")

    with col3:
        st.subheader("💰 Optimization Wallet")
        st.metric(label="Carbon Tax Saved", value=f"${tax_saved_dollars:.2f}", delta="🏆 Financial Win")
        st.metric(label="CO2 Kept Out of Atmosphere", value=f"{co2_saved_kg:.2f} kg", delta="📉 Carbon Reduced", delta_color="inverse")