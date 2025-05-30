import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Taxi Fare Comparator", page_icon="🚕", layout="centered")

st.title("🚕 Taxi Fare Comparator")
st.markdown(
    """
    Welcome! Enter your ride details to get a fare estimate and compare taxi fares.
    """
)

with st.sidebar:
    st.header("Ride Details")
    pickup_datetime = st.datetime_input("Pickup Date & Time", value=datetime.now())
    pickup_longitude = st.number_input("Pickup Longitude", value=-73.985428, format="%.6f")
    pickup_latitude = st.number_input("Pickup Latitude", value=40.748817, format="%.6f")
    dropoff_longitude = st.number_input("Dropoff Longitude", value=-73.985428, format="%.6f")
    dropoff_latitude = st.number_input("Dropoff Latitude", value=40.758896, format="%.6f")
    passenger_count = st.slider("Passenger Count", 1, 8, 1)

st.markdown("### Your Ride Summary")
st.write(
    f"**Pickup:** ({pickup_latitude}, {pickup_longitude})  \n"
    f"**Dropoff:** ({dropoff_latitude}, {dropoff_longitude})  \n"
    f"**Date & Time:** {pickup_datetime.strftime('%Y-%m-%d %H:%M:%S')}  \n"
    f"**Passengers:** {passenger_count}"
)

if st.button("Compare Fares"):
    params = {
        "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count,
    }
    api_url = "https://taxifare.lewagon.ai/predict"
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        fare = response.json().get("fare", "N/A")
        st.success(f"Estimated Fare: **${fare:.2f}**")
    except Exception as e:
        st.error(f"Error fetching fare: {e}")

st.info("Tip: Adjust the ride details in the sidebar and click 'Compare Fares' to get a new estimate.")
