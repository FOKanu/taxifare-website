# Taxi Fare Comparator

A Streamlit app that compares taxi fares using Google Maps integration.

## Setup

1. Get a Google Maps API key:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the following APIs:
     - Maps JavaScript API
     - Places API
     - Directions API
     - Geocoding API
   - Create credentials (API key)

2. Set up the API key in Streamlit Cloud:
   - Go to your app on Streamlit Cloud
   - Click on the three dots (⋮) in the top right corner
   - Select "Settings"
   - Go to the "Secrets" section
   - Add your API key in this format:
     ```toml
     GOOGLE_MAPS_API_KEY = "your-actual-api-key-here"
     ```

3. Run the app locally:
   - Create a `.streamlit/secrets.toml` file
   - Add your API key in the same format as above
   - Run `streamlit run app.py`

## Features

- Location search with autocomplete
- Interactive map visualization
- Fare estimation
- Multiple ride types
- Payment method selection
- Route visualization
- Nearby taxi display
