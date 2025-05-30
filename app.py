import streamlit as st
import requests
from datetime import datetime
import googlemaps
from config import GOOGLE_MAPS_API_KEY
import folium
from streamlit_folium import folium_static
import json

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

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
    .location-input {
        margin-bottom: 1rem;
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

    # Location inputs with autocomplete
    pickup_address = st.text_input("Pickup Location", placeholder="Enter pickup address", key="pickup")
    dropoff_address = st.text_input("Dropoff Location", placeholder="Enter dropoff address", key="dropoff")

    # Autocomplete suggestions
    if pickup_address:
        try:
            pickup_autocomplete = gmaps.places_autocomplete(pickup_address)
            if pickup_autocomplete:
                st.write("Suggestions:")
                for place in pickup_autocomplete[:3]:
                    if st.button(f"📍 {place['description']}", key=f"pickup_{place['place_id']}"):
                        pickup_address = place['description']
                        st.session_state.pickup = pickup_address
        except Exception as e:
            st.error(f"Error getting suggestions: {e}")

    if dropoff_address:
        try:
            dropoff_autocomplete = gmaps.places_autocomplete(dropoff_address)
            if dropoff_autocomplete:
                st.write("Suggestions:")
                for place in dropoff_autocomplete[:3]:
                    if st.button(f"📍 {place['description']}", key=f"dropoff_{place['place_id']}"):
                        dropoff_address = place['description']
                        st.session_state.dropoff = dropoff_address
        except Exception as e:
            st.error(f"Error getting suggestions: {e}")

    # Recent locations
    if st.session_state.recent_locations:
        st.subheader("Recent Locations")
        for loc in st.session_state.recent_locations:
            if st.button(f"📍 {loc}", key=f"recent_{loc}"):
                pickup_address = loc
                st.session_state.pickup = pickup_address

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
    # Map visualization
    st.subheader("Route Map")
    if pickup_address and dropoff_address:
        try:
            # Geocode addresses
            pickup_location = gmaps.geocode(pickup_address)[0]['geometry']['location']
            dropoff_location = gmaps.geocode(dropoff_address)[0]['geometry']['location']

            # Get directions
            directions = gmaps.directions(
                pickup_address,
                dropoff_address,
                mode="driving",
                departure_time=datetime.now()
            )

            if directions:
                # Create map
                m = folium.Map(
                    location=[(pickup_location['lat'] + dropoff_location['lat'])/2,
                            (pickup_location['lng'] + dropoff_location['lng'])/2],
                    zoom_start=12
                )

                # Add markers
                folium.Marker(
                    [pickup_location['lat'], pickup_location['lng']],
                    popup="Pickup",
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)

                folium.Marker(
                    [dropoff_location['lat'], dropoff_location['lng']],
                    popup="Dropoff",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)

                # Add route
                route = directions[0]['overview_polyline']['points']
                folium.PolyLine(
                    locations=folium.util.decode_polyline(route),
                    color='blue',
                    weight=2,
                    opacity=0.8
                ).add_to(m)

                # Display map
                folium_static(m)

                # Store in session state
                if pickup_address not in st.session_state.recent_locations:
                    st.session_state.recent_locations.append(pickup_address)
                if dropoff_address not in st.session_state.recent_locations:
                    st.session_state.recent_locations.append(dropoff_address)

                # Keep only last 5 locations
                st.session_state.recent_locations = st.session_state.recent_locations[-5:]
        except Exception as e:
            st.error(f"Error displaying map: {e}")
    else:
        st.info("Enter pickup and dropoff locations to see the route map")

with col2:
    # Fare estimate
    st.subheader("Fare Estimate")
    if st.button("Get Fare Estimate"):
        if pickup_address and dropoff_address:
            try:
                # Get directions for distance and duration
                directions = gmaps.directions(
                    pickup_address,
                    dropoff_address,
                    mode="driving",
                    departure_time=datetime.now()
                )

                if directions:
                    # Extract distance and duration
                    distance = directions[0]['legs'][0]['distance']['value'] / 1000  # Convert to km
                    duration = directions[0]['legs'][0]['duration']['value'] / 60  # Convert to minutes

                    # Calculate base fare (example formula)
                    base_fare = 2.50 + (distance * 1.50) + (duration * 0.25)

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
                    st.write(f"- Distance: {distance:.1f} km")
                    st.write(f"- Estimated duration: {int(duration)} minutes")

                    # Book ride button
                    if st.button("Book Ride"):
                        st.balloons()
                        st.success("Ride booked successfully! 🎉")
                else:
                    st.error("Could not calculate route. Please check the addresses.")
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
