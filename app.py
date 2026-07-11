import streamlit as st

st.set_page_config(layout="wide", page_title="EcoRoute")
st.title("🌿 EcoRoute: Carbon Tax Optimization Dashboard")

# These are the Sidebar Inputs
st.sidebar.title("📍 Route Configuration")
origin = st.sidebar.selectbox("Origin", ["UTM"])
destination = st.sidebar.selectbox("Destination", ["Square One", "Port Credit GO", "Erin Mills"])

# Creates 3 Layout Columns
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("📊 Trip Metrics")
    # Distance logic will go here
    st.metric(label="Driving Distance", value="7.2 km")

with col2:
    st.subheader("🗺️ Mississauga Transit Map")
    st.info("Map rendering area (Folium map will go here next)")

with col3:
    st.subheader("💰 Optimization Wallet")
    # Carbon tax calculation will display here
    st.metric(label="Carbon Tax Evaded", value="$1.45", delta="🏆 Saved")