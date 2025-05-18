#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime, timezone, timedelta

# Constants
DAILY_FORECAST_URL = "https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast"
HOURLY_FORECAST_URL = "https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast/hourly"
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
        print(self.daily_forecast_url)

    def get_raw_daily_forecast_data(self):
        """
        Fetch raw daily forecast data from the API.
        """
        daily_forecast_url = DAILY_FORECAST_URL.format(
            gridId=self.grid_id, gridX=self.grid_x, gridY=self.grid_y
        )
        return self.get_raw_forecast_data(daily_forecast_url)
    
    def get_raw_forecast_data(self, url):
        """
        Fetch raw forecast data from the API.
        """
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode("utf8"))
    
    def get_raw_hourly_forecast_data(self):
        """
        Fetch raw hourly forecast data from the API.
        """
        hourly_forecast_url = HOURLY_FORECAST_URL.format(
            gridId=self.grid_id, gridX=self.grid_x, gridY=self.grid_y
        )
        return self.get_raw_forecast_data(hourly_forecast_url)
    

    def get_daily_forecast(self):
        """
        Get the daily weather forecast for the next 7 days.
        """
        raw_data = self.get_raw_daily_forecast_data()
        periods = raw_data["properties"]["periods"]
        daily_forecast = []

        for period in periods:
            daily_forecast.append({
                "name": period["name"],
                "temperature": period["temperature"],
                "percentageOfPrecipitation": period["probabilityOfPrecipitation"]["value"],
                "wind_speed": period["windSpeed"],
                "short_forecast": period["shortForecast"]
            })

        return daily_forecast

    def get_hourly_forecast(self):
        """
        Get the hourly weather forecast for the next 24 hours.
        """
        raw_data = self.get_raw_hourly_forecast_data()
        periods = raw_data["properties"]["periods"]
        hourly_forecast = []

        for period in periods:
            hourly_forecast.append({
                "hour": datetime.strptime(period["startTime"], WEATHER_TIME_FORMAT).strftime("%H"),
                "temperature": period["temperature"],
                "wind_speed": period["windSpeed"],
                "wind_direction": period["windDirection"],
                "short_forecast": period["shortForecast"],
                "probabilityOfPrecipitation": period["probabilityOfPrecipitation"]["value"]
            })
        return hourly_forecast


    def get_current_weather(self):
        """
        Get the current weather conditions.
        """
        current_conditions = self.get_raw_daily_forecast_data()["properties"]["periods"][0]
        return {
            "temperature": current_conditions["temperature"],
            "wind_speed": current_conditions["windSpeed"],
            "short_forecast": current_conditions["shortForecast"],
            "temp_unit": current_conditions["temperatureUnit"],
        }

    def get_sunrise(self):
        """
        Get the local sunrise time for the current lat/lon.
        """
        url = f"https://api.sunrise-sunset.org/json?lat={self.lat}&lng={self.lon}&formatted=0"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf8"))
        sunrise_utc = datetime.fromisoformat(data["results"]["sunrise"]).replace(tzinfo=timezone.utc)
        # Convert to local time (system local time)
        local_sunrise = sunrise_utc.astimezone()
        return local_sunrise.strftime("%I:%M %p")

    def get_sunset(self):
        """
        Get the local sunset time for the current lat/lon.
        """
        url = f"https://api.sunrise-sunset.org/json?lat={self.lat}&lng={self.lon}&formatted=0"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf8"))
        sunset_utc = datetime.fromisoformat(data["results"]["sunset"]).replace(tzinfo=timezone.utc)
        # Convert to local time (system local time)
        local_sunset = sunset_utc.astimezone()
        return local_sunset.strftime("%I:%M %p")
    
def main():
    """
    Main function to test the RemoteWeather class.
    """
    lat, lon = 47.697, -122.3222  # Example coordinates
    weather = RemoteWeather(lat, lon)
    daily_forecast = weather.get_daily_forecast()
    print(weather.get_current_weather())

    print("\nHourly Forecast:")
    hourly_forecast = weather.get_hourly_forecast()
    for hour in hourly_forecast:
        print(f"Time: {hour['hour']}:00")
        print(f"  Temp: {hour['temperature']}°F")
        print(f"  Wind Speed: {hour['wind_speed']}")
        print(f"  Wind Direction: {hour['wind_direction']}")
        print(f"  Forecast: {hour['short_forecast']}")
        print()

    
    # print("[7-Day Weather Forecast]")
    # for day in daily_forecast:
    #     print(f"Date: {day['date']}")
    #     print(f"  High Temp: {day['high_temp']}°F")
    #     print(f"  Low Temp: {day['low_temp']}°F")
    #     print(f"  Wind Speed: {day['wind_speed']}")
    #     print(f"  Forecast: {day['short_forecast']}")
    #     print()

if __name__ == "__main__":
    main()