import time
from datetime import datetime
from weather import RemoteWeather
from openweatheraqi import RemoteAQI, COMPONENT_NAMES
from location import Location

# Constants
CLOCK_FREQUENCY = 60  # seconds
WEATHER_FREQUENCY = 1  # minutes
FORECAST_FREQUENCY = 1  # minutes

class AlarmClock:
    """
    A class to run an alarm clock that prints time, weather, and forecast at specified intervals.
    """

    def __init__(self):
        """
        Initialize the AlarmClock with location, weather, and AQI data.
        """
        self.location = Location()
        self.weather = RemoteWeather(self.location.get_lat(), self.location.get_lon())
        with open('/private/keys/openweather.txt', encoding="utf-8") as f:
            api_key = f.read().strip()
        self.aqi = RemoteAQI(self.location.get_lat(), self.location.get_lon(), api_key)

    def print_time(self):
        """
        Print the current time to the screen.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[Time] {now}")

    def print_weather(self):
        """
        Print the current temperature, wind speed, and AQI.
        """
        # Fetch weather data
        forecast = self.weather.get_current_weather()  # Get the current period
        temperature = self.weather.get_temp_string(forecast)
        wind_speed = forecast["windSpeed"]

        # Fetch AQI data
        aqi_forecast = self.aqi.get_forecast()[0]  # Get the first AQI forecast
        aqi = aqi_forecast["aqi"]
        category = aqi_forecast["category"]

        print(f"[Weather] Temperature: {temperature}, Wind Speed: {wind_speed}")
        print(f"[AQI] {aqi} ({category})")

    def print_hourly_forecast(self):
        """
        Print the hourly weather forecast for the next 24 hours.
        """
        forecast = self.weather.get_forecast_data()[:24]  # Get the next 24 periods
        print("[Hourly Weather Forecast]")
        for period in forecast:
            time_range = self.weather.get_dur_string(period["startTime"], period["endTime"])
            temperature = self.weather.get_temp_string(period)
            wind_speed = period["windSpeed"]
            print(f"{time_range} | Temperature: {temperature}, Wind Speed: {wind_speed}")

    def print_hourly_aqi_forecast(self):
        """
        Print the hourly AQI forecast for the next 24 hours.
        """
        forecast = self.aqi.get_hourly_aqi_forecast()
        print("[Hourly AQI Forecast]")
        for entry in forecast:
            timestamp = entry["timestamp"]
            aqi = entry["aqi"]
            category = entry["category"]

            print(f"Timestamp: {timestamp} | AQI: {aqi} ({category})")
            print()

    def print_daily_summary_forecast(self):
        """
        Print the daily summary weather and AQI forecast for the next 7 days.
        """
        print("[7-Day Weather and AQI Summary Forecast]")
        # Fetch daily weather forecast
        daily_weather = self.weather.get_daily_forecast()[:7]  # Get the next 7 days
        daily_aqi = self.aqi.get_daily_aqi_forecast()[:7]  # Get the next 7 days of AQI

        for i in range(len(daily_weather)):
            weather = daily_weather[i]
            aqi = daily_aqi[i]

            date = weather["date"]
            high_temp = weather["high_temp"]
            low_temp = weather["low_temp"]
            wind_speed = weather["wind_speed"]

            aqi_value = aqi["aqi"]
            aqi_category = aqi["category"]

            print(f"Date: {date}")
            print(f"  Weather: High {high_temp}, Low {low_temp}, Wind Speed: {wind_speed}")
            print(f"  AQI: {aqi_value} ({aqi_category})")
            print()

    def run(self):
        """
        Run the alarm clock, printing updates at specified intervals.
        """
        short_counter = 0
        long_counter = 0

        while True:
            self.print_time()
            short_counter += 1
            long_counter += 1

            if short_counter % WEATHER_FREQUENCY == 0:
                self.print_weather()

            if long_counter == FORECAST_FREQUENCY:
                self.print_hourly_forecast()
                self.print_hourly_aqi_forecast()
                self.print_daily_summary_forecast()
                long_counter = 0

            time.sleep(CLOCK_FREQUENCY)  # Wait for 1 minute

if __name__ == "__main__":
    alarm_clock = AlarmClock()
    alarm_clock.run()