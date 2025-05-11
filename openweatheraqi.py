#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime, timezone

# Constants
AQI_URL = 'http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={key}'
KEY_FILE = '/private/keys/openweather.txt'
OUT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# AQI Categories
AQI_GOOD = 1
AQI_FAIR = 2
AQI_MODERATE = 3
AQI_POOR = 4
AQI_VERY_POOR = 5

AQI_CATEGORY_MAP = {
    AQI_GOOD: "Good",
    AQI_FAIR: "Fair",
    AQI_MODERATE: "Moderate",
    AQI_POOR: "Poor",
    AQI_VERY_POOR: "Very Poor"
}

class RemoteAQI:
    """
    A class to fetch and process AQI data from the OpenWeatherMap API.
    """

    def __init__(self, lat, lon, key):
        """
        Initialize the RemoteAQI class with latitude, longitude, and API key.
        """
        self.lat = lat
        self.lon = lon
        self.key = key
        self.forecast_url = AQI_URL.format(lat=self.lat, lon=self.lon, key=self.key)

    def get_raw_forecast_data(self):
        """
        Fetch raw AQI forecast data from the API.
        """
        response = urllib.request.urlopen(self.forecast_url)
        return json.loads(response.read().decode('utf8'))

    def get_forecast(self):
        """
        Get a detailed AQI forecast including local timestamps, AQI values, and categories.
        """
        raw_data = self.get_raw_forecast_data()
        forecast = []

        for entry in raw_data['list']:
            timestamp = entry['dt']
            # Convert UTC timestamp to local time
            date_time = convert_timestamp_to_local(timestamp)

            aqi = entry['main']['aqi']
            category = AQI_CATEGORY_MAP.get(aqi, "Unknown")
            components = entry['components']

            forecast.append({
                "timestamp": date_time,
                "aqi": aqi,
                "category": category,
                "components": components
            })

        return forecast

    def get_hourly_aqi_forecast(self):
        """
        Get the hourly AQI forecast for the next 24 hours.
        """
        forecast = self.get_forecast()
        hourly_aqi = []

        for entry in forecast[:24]:
            timestamp = entry["timestamp"]
            aqi = entry["aqi"]
            category = entry["category"]
            components = entry["components"]

            hourly_aqi.append({
                "timestamp": timestamp,
                "aqi": aqi,
                "category": category
            })
        return hourly_aqi
    
    def get_detailed_current_aqi(self):
        """
        Get the current AQI and its components.
        """
        forecast = self.get_forecast()
        current_aqi = forecast[0]
        timestamp = current_aqi["timestamp"]
        aqi = current_aqi["aqi"]
        category = current_aqi["category"]
        components = current_aqi["components"]
        # Convert components to a human-readable format
        components = {k: f"{v} μg/m³" for k, v in components.items()}
        
        return {
            "timestamp": timestamp,
            "aqi": aqi,
            "category": category,
            "components": components
        }
    
    def get_daily_aqi_forecast(self):
        """
        Get the daily AQI forecast by calculating the maximum AQI for each day.
        """
        forecast = self.get_forecast()
        daily_aqi = {}

        for entry in forecast:
            date = entry["timestamp"].split(" ")[0]  # Extract the date (YYYY-MM-DD)
            aqi = entry["aqi"]
            category = entry["category"]

            if date not in daily_aqi or aqi > daily_aqi[date]["aqi"]:
                daily_aqi[date] = {
                    "date": date,
                    "aqi": aqi,
                    "category": category
                }

        # Convert the dictionary to a sorted list of daily AQI forecasts
        return [daily_aqi[date] for date in sorted(daily_aqi.keys())]

def convert_timestamp_to_local(timestamp): 
    """
    Convert a UTC timestamp to local time.
    """
    utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
    local_time = utc_time.astimezone()  # Converts to local time zone
    return local_time.strftime(OUT_TIME_FORMAT)

def main():
    """
    Main function to fetch and display AQI data.
    """
    with open(KEY_FILE, encoding="utf-8") as f:
        key = f.read().strip()

    # Example coordinates for testing
    lat, lon = 47.697, -122.3222
    ra = RemoteAQI(lat, lon, key)
    daily_aqi_forecast = ra.get_daily_aqi_forecast()

    # Print the current AQI
    current_aqi = ra.get_detailed_current_aqi()
    print(f"[Current AQI] {current_aqi['timestamp']}")
    print(f"  AQI: {current_aqi['aqi']} ({current_aqi['category']})")
    print(f"  Components: {current_aqi['components']}")
    print()
    # Print the hourly AQI forecast
    hourly_aqi_forecast = ra.get_hourly_aqi_forecast()
    print("[Hourly AQI Forecast]")
    for hour in hourly_aqi_forecast:
        print(f"Timestamp: {hour['timestamp']}")
        print(f"  AQI: {hour['aqi']} ({hour['category']})")
        print()   
    print("[7-Day AQI Forecast]")
    for day in daily_aqi_forecast:
        print(f"Date: {day['date']}")
        print(f"  AQI: {day['aqi']} ({day['category']})")
        print()

if __name__ == '__main__':
    main()