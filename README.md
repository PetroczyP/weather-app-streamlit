# Weather Map & Data Visualization App

A Streamlit web application that provides real-time weather information and forecasts using the OpenWeatherMap API.

## Features

- Current weather conditions display (temperature, humidity, wind speed)
- Interactive map showing the location of the searched city
- 5-day temperature forecast visualization
- Search history logging with SQLite database

## Technologies Used

- Python
- Streamlit
- OpenWeatherMap API
- Pandas for data manipulation
- SQLite for data storage

## Setup and Installation

1. Clone this repository
2. Install the required packages:
   pip install -r requirements.txt
3. Create a `.streamlit/secrets.toml` file with your OpenWeatherMap API key:
   [openweathermap]
   api_key = "your_api_key_here"
4. Run the application:
   streamlit run app.py

## Usage

1. Enter a city name in the search box
2. View current weather conditions, location map, and temperature forecast
3. Check search history to see previous searches

## Live Demo

The application is deployed on Streamlit Community Cloud and can be accessed: [<to-be-added>](https://weather-app-rbtdreams-pp.streamlit.app/)

## Created By

PetroczyP - As part of a Python Course
