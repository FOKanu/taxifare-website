import os
import streamlit as st

# Google Maps API Configuration
try:
    GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == "your-actual-api-key-here":
        st.error("API key not found in secrets. Please check your secrets.toml file.")
except Exception as e:
    st.error(f"Error loading API key: {str(e)}")
    GOOGLE_MAPS_API_KEY = None
