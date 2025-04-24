import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sqlite3

# Set page configuration
st.set_page_config(
    page_title="Weather App",
    page_icon="🌤️",
    layout="wide"
)

# Cache API call to avoid unnecessary requests
@st.cache_data(ttl=300) # Caching for 5 minutes
def get_current_weather(city):
    """
    Fetch the current weather data for the city
    """
    api_key = st.secrets["openweathermap"]["api_key"]
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    try:
        response = requests.get(url)
        response.raise_for_status() # Raising exception for http errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching weather data: {e}")
        return None

# Caching the forecast API call
@st.cache_data(ttl=300) # once again, 5 minutes caching
def get_weather_forecast(city):
    """
    Fetch 5-day weather forecast data for the city
    """
    api_key = st.secrets["openweathermap"]["api_key"]  # Accessing the API key from secrets.toml
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching forecast data: {e}")
        return None

# Create tje DB and table
def create_db():
    conn = sqlite3.connect('weather_search_stats.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            humidity INTEGER,
            wind_speed REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# log the search to the database
def log_search(city, temp, humidity, wind_speed):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('weather_search_stats.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO searches (city, temperature, humidity, wind_speed, timestamp) VALUES (?, ?, ?, ?, ?)",
        (city, temp, humidity, wind_speed, timestamp)
    )
    conn.commit()
    conn.close()

# Create the database and table
create_db()

# App header
st.title("Robot Dreams Python - Weather Map & Data Visualization App")

# Use form for search to control the search-submit action
with st.form(key='search_form'):
    city = st.text_input("Enter city name")
    submit_button = st.form_submit_button(label='Search')

# Process weather data when a city is entered and Form is submitted
if submit_button and city:
    # Get current weather data
    weather_data = get_current_weather(city)

    if weather_data and weather_data.get("cod") != "404":
        # Extract required data
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]

        # Log search in DB
        log_search(city, temp, humidity, wind_speed)

        # Display current weather information
        st.subheader(f"Current Weather in {city}")

        # Create three columns for displaying the metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Temperature (°C)", value=f"{temp:.2f} °C")

        with col2:
            st.metric(label="Humidity (%)", value=f"{humidity}%")

        with col3:
            st.metric(label="Wind Speed (m/s)", value=f"{wind_speed} m/s")

        # Get Coordinates for the map visualization
        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]

        # Create a DataFrame for the map
        map_data = pd.DataFrame({
            'lat': [lat],
            'lon': [lon]
        })

        # Displaying the Map:
        st.subheader("Weather Map")
        st.map(map_data)

        # Get forecast data for temperature trends
        forecast_data = get_weather_forecast(city)

        if forecast_data and forecast_data.get("cod") != "404":
            # Extract temperature data for 6 AM and 6 PM for the next 5 days
            forecast_temps = []
            forecast_times = []

            for item in forecast_data["list"]:
                dt_txt = item["dt_txt"]
                date_part, time_part = dt_txt.split(" ")

                # Format date to shorter version
                month, day = date_part.split("-")[1:]
                short_date = f"{month}/{day}"

                # Filter for 6 AM and 6 PM forecasts
                if time_part in ["06:00:00", "18:00:00"]:
                    temp = item["main"]["temp"]

                    # Format the time for display (06 AM or 06 PM)
                    hour = int(time_part.split(":")[0])
                    am_pm = "AM" if hour < 12 else "PM"
                    display_time = f"{short_date} {hour:02d}{am_pm}"
                    
                    # Add to lists for plotting
                    forecast_temps.append(temp)
                    forecast_times.append(display_time)

                    # Limit to 10 data points (5 days with 2 points per day)
                    if len(forecast_temps) >= 10:
                        break
            
            # Create a DataFrame for the chart
            chart_data = pd.DataFrame({
                'Time': forecast_times,
                'Temperature (°C)': forecast_temps
            })

            # Display the temperature trends chart
            st.subheader("Temperature Trends for Next 5 Days")
            
            # Using Line Chart with the data structure
            st.line_chart(chart_data.set_index('Time')['Temperature (°C)'])

    else:
        st.warning(f"City '{city}' not found. Please try another one.")

# Check logged searches
st.subheader("Search History")
if st.button("Show Search History"):
    try:
        conn = sqlite3.connect('weather_search_stats.db')
        query = "SELECT * FROM searches"
        search_history = pd.read_sql_query(query, conn)
        conn.close()

        if not search_history.empty:
            st.dataframe(search_history)
        else:
            st.info("Nothing has been logged so far.")
    except Exception as e:
        st.error(f"Error retrieving search history: {e}")
