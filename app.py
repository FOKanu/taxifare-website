import streamlit as st
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Initialize geocoder
geolocator = Nominatim(user_agent="taxi_fare_app")

# Page config
st.set_page_config(
    page_title="Taxi Fare Comparator",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .ride-option {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🚕 Taxi Fare Comparator")
st.markdown("""
    Welcome! Enter your ride details to get a fare estimate and compare taxi fares.
    Choose your preferred ride type and payment method.
""")

# Initialize session state for recent locations
if 'recent_locations' not in st.session_state:
    st.session_state.recent_locations = []

# Sidebar
with st.sidebar:
    st.header("Ride Details")

    # Location inputs
    pickup_address = st.text_input("Pickup Location", placeholder="Enter pickup address")
    dropoff_address = st.text_input("Dropoff Location", placeholder="Enter dropoff address")

    # Recent locations
    if st.session_state.recent_locations:
        st.subheader("Recent Locations")
        for loc in st.session_state.recent_locations:
            if st.button(f"📍 {loc}", key=f"recent_{loc}"):
                pickup_address = loc

    # Date and time
    pickup_date = st.date_input("Pickup Date", value=datetime.now().date())
    pickup_time = st.time_input("Pickup Time", value=datetime.now().time())
    pickup_datetime = datetime.combine(pickup_date, pickup_time)

    # Ride type selection
    st.subheader("Ride Type")
    ride_type = st.radio(
        "Select your ride type",
        ["Economy", "Comfort", "Premium"],
        horizontal=True
    )

    # Passenger count
    passenger_count = st.slider("Passenger Count", 1, 8, 1)

    # Payment method
    st.subheader("Payment Method")
    payment_method = st.radio(
        "Select payment method",
        ["Cash", "Credit Card", "PayPal"],
        horizontal=True
    )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Map placeholder (you can integrate actual map here)
    st.subheader("Route Map")
    st.info("Map view will be displayed here")

    # Ride summary
    st.subheader("Ride Summary")
    if pickup_address and dropoff_address:
        try:
            # Geocode addresses
            pickup_location = geolocator.geocode(pickup_address)
            dropoff_location = geolocator.geocode(dropoff_address)

            if pickup_location and dropoff_location:
                # Calculate distance
                distance = geodesic(
                    (pickup_location.latitude, pickup_location.longitude),
                    (dropoff_location.latitude, dropoff_location.longitude)
                ).kilometers

                # Estimate time (assuming average speed of 30 km/h)
                estimated_time = distance / 30 * 60  # in minutes

                st.write(f"**Distance:** {distance:.1f} km")
                st.write(f"**Estimated Time:** {int(estimated_time)} minutes")

                # Store in session state
                if pickup_address not in st.session_state.recent_locations:
                    st.session_state.recent_locations.append(pickup_address)
                if dropoff_address not in st.session_state.recent_locations:
                    st.session_state.recent_locations.append(dropoff_address)

                # Keep only last 5 locations
                st.session_state.recent_locations = st.session_state.recent_locations[-5:]
        except Exception as e:
            st.error(f"Error geocoding addresses: {e}")

with col2:
    # Fare estimate
    st.subheader("Fare Estimate")
    if st.button("Get Fare Estimate"):
        if pickup_address and dropoff_address:
            try:
                # Geocode addresses
                pickup_location = geolocator.geocode(pickup_address)
                dropoff_location = geolocator.geocode(dropoff_address)

                if pickup_location and dropoff_location:
                    params = {
                        "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "pickup_longitude": pickup_location.longitude,
                        "pickup_latitude": pickup_location.latitude,
                        "dropoff_longitude": dropoff_location.longitude,
                        "dropoff_latitude": dropoff_location.latitude,
                        "passenger_count": passenger_count,
                    }

                    api_url = "https://taxifare.lewagon.ai/predict"
                    response = requests.get(api_url, params=params)
                    response.raise_for_status()
                    base_fare = response.json().get("fare", 0)

                    # Apply ride type multiplier
                    multipliers = {
                        "Economy": 1.0,
                        "Comfort": 1.3,
                        "Premium": 1.8
                    }

                    final_fare = base_fare * multipliers[ride_type]

                    # Display fare breakdown
                    st.success(f"Estimated Fare: **${final_fare:.2f}**")
                    st.write("Fare Breakdown:")
                    st.write(f"- Base fare: ${base_fare:.2f}")
                    st.write(f"- {ride_type} multiplier: x{multipliers[ride_type]}")
                    st.write(f"- Payment method: {payment_method}")

                    # Book ride button
                    if st.button("Book Ride"):
                        st.balloons()
                        st.success("Ride booked successfully! 🎉")
                else:
                    st.error("Could not find the specified locations. Please check the addresses.")
            except Exception as e:
                st.error(f"Error calculating fare: {e}")
        else:
            st.warning("Please enter both pickup and dropoff locations")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Need help? Contact support at support@taxifare.com</p>
        <p>© 2024 TaxiFare. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
