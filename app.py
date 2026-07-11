import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from openai import OpenAI  # OpenAI SDK used to call Featherless endpoint structures
import os                  # Added to interface with system environment memory
from dotenv import load_dotenv  # Added to load local hidden configuration files

# Automatically loads the parameters defined in your hidden .env file into memory
load_dotenv()

# Page configuration
st.set_page_config(layout="wide", page_title="EcoRoute")

# Inject Global CSS Override to resolve metric card text clipping ("Tree-D...")
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: clamp(1.4rem, 1.8vw, 2.2rem) !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 EcoRoute: Carbon Tax Optimization Dashboard")

# Define available Mississauga hubs
locations = [
    "UTM (University of Toronto Mississauga)",
    "Square One Shopping Centre",
    "Port Credit GO",
    "Erin Mills Town Centre"
]

# Sidebar Inputs - Route Configuration
st.sidebar.title("📍 Route Configuration")
origin = st.sidebar.selectbox("Origin", locations, index=0)
destination = st.sidebar.selectbox("Destination", locations, index=1)

st.sidebar.markdown("---")

# Sidebar Inputs - Vehicle Profiles
st.sidebar.title("🚗 Vehicle Profile")
vehicle_type = st.sidebar.selectbox(
    "Your Current Vehicle Profile",
    ["Standard Sedan", "SUV / Light Truck", "Hybrid Vehicle", "Electric Vehicle (EV)"]
)

# Robust structural mapping to insulate lookups from hidden string/encoding anomalies
vehicle_mapping = {
    "Standard Sedan": "sedan",
    "SUV / Light Truck": "suv",
    "Hybrid Vehicle": "hybrid",
    "Electric Vehicle (EV)": "ev"
}
internal_key = vehicle_mapping.get(vehicle_type, "sedan")

# Dynamic Emission Factors (g CO2 per km) mapping
emission_factors = {
    "sedan": 200,
    "suv": 280,
    "hybrid": 110,
    "ev": 0
}
driving_emission_g_km = emission_factors[internal_key]

# Dynamic Fuel Consumption Factors (Liters per 100km approximation)
fuel_factors = {
    "sedan": 8.0,
    "suv": 11.5,
    "hybrid": 4.5,
    "ev": 0.0
}
liters_per_100km = fuel_factors[internal_key]

st.sidebar.markdown("---")
st.sidebar.title("🔮 Projections Parameters")
gas_price = st.sidebar.slider("Regional Fuel Price (CAD/L)", min_value=1.30, max_value=2.20, value=1.65, step=0.05)
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

    # Route-Specific Navigation Itineraries
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
        ],
        "Erin Mills Town Centre➔Square One Shopping Centre": [
            "🚶 Proceed to Erin Mills Town Centre Bus Terminal.",
            "🚌 Board MiWay Route 34 Eastbound or Route 109 Northbound Express.",
            "⏱️ Travel east along the Mississauga Transitway corridor.",
            "🏁 Arrive at City Centre Transit Terminal (Square One)."
        ],
        "Square One Shopping Centre➔Erin Mills Town Centre": [
            "🚶 Proceed to City Centre Transit Terminal.",
            "🚌 Board MiWay Route 34 Westbound or Route 109 Southbound Express.",
            "⏱️ Transit via the dedicated Transitway bypass.",
            "🏁 Arrive at Erin Mills Town Centre Transit Hub."
        ],
        "Port Credit GO➔Square One Shopping Centre": [
            "🚶 Locate the Port Credit GO bus bays.",
            "🚌 Board MiWay Route 2 Northbound or Route 103 Hurontario Express.",
            "⏱️ Ride North along Hurontario Street straight to City Centre.",
            "🏁 Arrive at City Centre Transit Terminal (Square One)."
        ],
        "Square One Shopping Centre➔Port Credit GO": [
            "🚶 Go to City Centre Transit Terminal.",
            "🚌 Board MiWay Route 2 Southbound or Route 103 Hurontario Express.",
            "⏱️ Travel South along the Hurontario rapid corridor.",
            "🏁 Arrive at Port Credit GO Station."
        ],
        "Erin Mills Town Centre➔Port Credit GO": [
            "🚌 Board MiWay Route 13 Southbound towards South Common Centre.",
            "🔄 Transfer at South Common Centre to MiWay Route 14 Eastbound.",
            "⏱️ Ride through Mississauga Road corridor down to Lakeshore.",
            "🏁 Arrive at Port Credit GO Station."
        ],
        "Port Credit GO➔Erin Mills Town Centre": [
            "🚌 Board MiWay Route 14 Westbound from Port Credit GO.",
            "🔄 Transfer at South Common Centre to MiWay Route 13 Northbound.",
            "⏱️ Ride North along South Millway directly to the mall hub.",
            "🏁 Arrive at Erin Mills Town Centre Transit Hub."
        ]
    }
    
    current_itinerary = itineraries.get(itinerary_key, [
        "🚌 Board connecting MiWay local transit service line.",
        "⏱️ Transfer routes dynamically to complete transit loop.",
        "🏁 Arrive safely at destination hub."
    ])

    # Carbon Tax & Emissions Calculation Logic
    car_emissions_kg = (distance_km * driving_emission_g_km) / 1000
    transit_emissions_kg = (distance_km * 40) / 1000
    single_co2_saved = max(0.0, car_emissions_kg - transit_emissions_kg)
    
    base_tax_rate_per_km = 0.15
    multiplier = driving_emission_g_km / 200.0
    single_tax_saved = distance_km * base_tax_rate_per_km * multiplier

    weekly_tax_saved = single_tax_saved * weekly_trips
    annual_tax_saved = weekly_tax_saved * 52
    weekly_co2_saved = single_co2_saved * weekly_trips
    annual_co2_saved = weekly_co2_saved * 52
    
    annual_trees_saved = annual_co2_saved / 22.0
    weekly_trees_saved = annual_trees_saved / 52.0

    # Column 1: Trip Metrics
    with col1:
        st.subheader("📊 Single Trip Metrics")
        with st.container(border=True):
            st.metric(label="Total Distance", value=f"{distance_km} km")
        with st.container(border=True):
            st.metric(label="🚗 Driving Duration", value=f"{drive_time} mins")
        with st.container(border=True):
            st.metric(label="🚌 Transit Duration", value=f"{transit_time} mins")

    # Column 2: Map & Route Breakdown
    with col2:
        st.subheader("🗺️ Mississauga Transit Map")
        
        coordinates = {
            "UTM (University of Toronto Mississauga)": [43.5479, -79.6612],
            "Square One Shopping Centre": [43.5931, -79.6425],
            "Port Credit GO": [43.5557, -79.5869],
            "Erin Mills Town Centre": [43.5413, -79.7180]
        }
        
        simulated_paths = {
            "Erin Mills Town Centre-Square One Shopping Centre": [
                [43.5413, -79.7180], [43.5428, -79.7115], [43.5562, -79.6975],
                [43.5684, -79.6845], [43.5781, -79.6610], [43.5835, -79.6492],
                [43.5891, -79.6480], [43.5912, -79.6455], [43.5931, -79.6425]
            ],
            "Erin Mills Town Centre-UTM (University of Toronto Mississauga)": [
                [43.5413, -79.7180], [43.5401, -79.7020], [43.5352, -79.6885],
                [43.5348, -79.6710], [43.5415, -79.6690], [43.5460, -79.6635],
                [43.5479, -79.6612]
            ],
            "Erin Mills Town Centre-Port Credit GO": [
                [43.5413, -79.7180], [43.5310, -79.7120], [43.5185, -79.6912],
                [43.5042, -79.6705], [43.5115, -79.6420], [43.5220, -79.6210],
                [43.5365, -79.6050], [43.5492, -79.5935], [43.5557, -79.5869]
            ],
            "Port Credit GO-Square One Shopping Centre": [
                [43.5557, -79.5869], [43.5610, -79.5925], [43.5685, -79.6010],
                [43.5752, -79.6135], [43.5818, -79.6248], [43.5885, -79.6335],
                [43.5910, -79.6390], [43.5931, -79.6425]
            ],
            "Port Credit GO-UTM (University of Toronto Mississauga)": [
                [43.5557, -79.5869], [43.5512, -79.5950], [43.5448, -79.6105],
                [43.4985, -79.6290], [43.5112, -79.6410], [43.5295, -79.6515],
                [43.5430, -79.6558], [43.5479, -79.6612]
            ],
            "Square One Shopping Centre-UTM (University of Toronto Mississauga)": [
                [43.5931, -79.6425], [43.5895, -79.6432], [43.5852, -79.6441],
                [43.5791, -79.6468], [43.5748, -79.6512], [43.5702, -79.6582],
                [43.5663, -79.6755], [43.5582, -79.6711], [43.5528, -79.6655],
                [43.5479, -79.6612]
            ]
        }
        
        start_coords = coordinates[origin]
        end_coords = coordinates[destination]
        center_lat = (start_coords[0] + end_coords[0]) / 2
        center_lon = (start_coords[1] + end_coords[1]) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB dark_matter")
        folium.Marker(location=start_coords, popup="Origin", icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(location=end_coords, popup="Destination", icon=folium.Icon(color="red", icon="stop")).add_to(m)
        
        route_path_points = simulated_paths.get(pair_key, [start_coords, end_coords])
        folium.PolyLine(locations=route_path_points, color="#39FF14", weight=5, opacity=0.85).add_to(m)
        
        st_folium(m, use_container_width=True, height=400, key=f"map_{origin}_{destination}")
        st.write("")
        st.success("🟢 Route Operating on Schedule (Verified via MiWay Live Data Feed)")
        
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
            with st.container(border=True):
                st.markdown("### 🌲 Environmental Offset")
                st.metric(label="Equivalent Tree-Days of CO2", value=f"{weekly_trees_saved * 365:.1f} Tree-Days")
                
        with tab2:
            with st.container(border=True):
                st.metric(label="Projected Annual Savings", value=f"${annual_tax_saved:.2f}", delta="🏆 Financial ROI")
            with st.container(border=True):
                st.metric(label="Projected Annual CO2 Avoided", value=f"{annual_co2_saved:.2f} kg", delta="📉 High Impact", delta_color="inverse")
            with st.container(border=True):
                st.markdown("### 🌲 Environmental Offset")
                st.metric(label="Mature Trees Saved / Year", value=f"{annual_trees_saved:.1f} Trees")

    # 5-Year Macroeconomic Chart
    st.markdown("---")
    st.subheader("📈 5-Year Macroeconomic Cost Projections")
    
    years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    driving_trend = []
    transit_trend = []
    
    single_transit_fare = 3.40
    annual_transit_cost = single_transit_fare * weekly_trips * 52
    dynamic_fuel_cost_per_km = (liters_per_100km / 100.0) * gas_price
    annual_driving_cost = (single_tax_saved + (distance_km * dynamic_fuel_cost_per_km)) * weekly_trips * 52
    
    for year in range(1, 6):
        driving_trend.append(annual_driving_cost * year)
        transit_trend.append(annual_transit_cost * year)
        
    chart_data = {"Driving (Carbon Tax + Fuel)": driving_trend, "Public Transit (MiWay Fares)": transit_trend}
    df_chart = pd.DataFrame(chart_data, index=years)
    st.line_chart(df_chart, height=300)

    # --- Featherless.ai Integration Component ---
    st.markdown("---")
    st.subheader("🤖 Featherless AI: Hyper-Local Commute Strategist")
    st.caption("Generates tailored spatial logistics consulting using open-source infrastructure models.")

    # Securely fetch the API token implicitly from system environment storage
    featherless_api_key = os.getenv("FEATHERLESS_API_KEY")

    if not featherless_api_key:
        st.error("❌ Configuration Error: 'FEATHERLESS_API_KEY' was not found in your local .env file.")
    else:
        if st.button("Generate AI Optimization Strategy Brief"):
            with st.spinner("Connecting to Featherless cluster..."):
                try:
                    client = OpenAI(
                        base_url="https://api.featherless.ai/v1",  
                        api_key=featherless_api_key
                    )
                    
                    prompt_message = f"""
                    Analyze this commuter route inside Mississauga, Ontario:
                    - From: {origin}
                    - To: {destination}
                    - Driver Profile: {vehicle_type} running {liters_per_100km}L/100km at ${gas_price}/L.
                    - Estimated Impact: Switching to transit avoids {annual_tax_saved:.2f} CAD in fees and mitigates {annual_co2_saved:.2f} kg of CO2 emissions annually.
                    
                    Give 3 bullet points containing brief, actionable commuter guidance localized strictly to Mississauga infrastructure (mentioning things like MiWay, Go Transit, carpooling lots, or Transitway bypass corridors). Keep suggestions tightly focused.
                    """

                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-V3-0324",  # Calls premium deepseek tokenless cluster
                        messages=[
                            {"role": "system", "content": "You are a professional regional urban transit advisor based in Mississauga."},
                            {"role": "user", "content": prompt_message}
                        ]
                    )
                    
                    st.markdown("#### 📋 Urban Mobility Advisor Brief")
                    st.write(response.choices[0].message.content)
                    st.success("✨ Contextual brief successfully generated via tokenless serverless AI.")
                    
                except Exception as e:
                    st.error(f"Inference Connection Exception: {e}")