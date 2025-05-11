#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime

# Constants
DAILY_FORECAST_URL = "https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast"
WEATHER_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

class RemoteWeather:
    """
    A class to fetch and process weather data from the National Weather Service API.
    """

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.grid_id = None
        self.grid_x = None
        self.grid_y = None
        self.daily_forecast_url = None
        self.initialize_grid_data()

    def initialize_grid_data(self):
        """
        Fetch grid data for the given latitude and longitude to construct the forecast URL.
        """
        points_url = f"https://api.weather.gov/points/{self.lat},{self.lon}"
        response = urllib.request.urlopen(points_url)
        data = json.loads(response.read().decode("utf8"))
        properties = data["properties"]
        self.grid_id = properties["gridId"]
        self.grid_x = properties["gridX"]
        self.grid_y = properties["gridY"]
        self.daily_forecast_url = DAILY_FORECAST_URL.format(
            gridId=self.grid_id, gridX=self.grid_x, gridY=self.grid_y
        )

    def get_raw_daily_forecast_data(self):
        """
        Fetch raw daily forecast data from the API.
        """
        response = urllib.request.urlopen(self.daily_forecast_url)
        return json.loads(response.read().decode("utf8"))

    def get_daily_forecast(self):
        """
        Get the daily weather forecast for the next 7 days.
        """
        raw_data = self.get_raw_daily_forecast_data()
        periods = raw_data["properties"]["periods"]
        daily_forecast = []

        for period in periods:
            if "day" in period["name"].lower():  # Filter for daytime periods
                daily_forecast.append({
                    "date": datetime.strptime(period["startTime"], WEATHER_TIME_FORMAT).strftime("%Y-%m-%d"),
                    "high_temp": period["temperature"] if period["isDaytime"] else None,
                    "low_temp": None if period["isDaytime"] else period["temperature"],
                    "wind_speed": period["windSpeed"],
                    "short_forecast": period["shortForecast"]
                })

        return daily_forecast

def main():
    """
    Main function to test the RemoteWeather class.
    """
    lat, lon = 47.697, -122.3222  # Example coordinates
    weather = RemoteWeather(lat, lon)
    daily_forecast = weather.get_daily_forecast()

    print("[7-Day Weather Forecast]")
    for day in daily_forecast:
        print(f"Date: {day['date']}")
        print(f"  High Temp: {day['high_temp']}°F")
        print(f"  Low Temp: {day['low_temp']}°F")
        print(f"  Wind Speed: {day['wind_speed']}")
        print(f"  Forecast: {day['short_forecast']}")
        print()

if __name__ == "__main__":
    main()