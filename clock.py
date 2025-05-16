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
        self.time_message = self.get_time()
        self.weather_message = self.get_weather()
        self.hourly_forecast = self.get_hourly_forecast()
        self.daily_forecast = self.get_daily_summary_forecast()
        self.aqi_forecast = self.get_hourly_aqi_forecast()

    def get_time(self):
        """
        Print the current time to the screen.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (f"[Time] {now}")

    def get_weather(self):
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

        return (f"[Weather] Temperature: {temperature}, Wind Speed: {wind_speed}",
                f"\n[AQI] {aqi} ({category})")


    def get_hourly_forecast(self):
        """
        Print the hourly weather forecast for the next 24 hours.
        """
        forecast = self.weather.get_forecast_data()[:24]  # Get the next 24 periods
        hourly_forecast = ("[Hourly Weather Forecast]")
        for period in forecast:
            time_range = self.weather.get_dur_string(period["startTime"], period["endTime"])
            temperature = self.weather.get_temp_string(period)
            wind_speed = period["windSpeed"]
            hourly_forecast = hourly_forecast + (f"\n{time_range} | Temperature: {temperature}, Wind Speed: {wind_speed}")
        return hourly_forecast

    def get_hourly_aqi_forecast(self):
        """
        Print the hourly AQI forecast for the next 24 hours.
        """
        forecast = self.aqi.get_hourly_aqi_forecast()

        message = ("[Hourly AQI Forecast]")
        for entry in forecast:
            timestamp = entry["timestamp"]
            aqi = entry["aqi"]
            category = entry["category"]

            message = message + (f"\nTimestamp: {timestamp} | AQI: {aqi} ({category})\n")

    def get_daily_summary_forecast(self):
        """
        Print the daily summary weather and AQI forecast for the next 7 days.
        """
        daily_forecast = ("[7-Day Weather and AQI Summary Forecast]")
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

            daily_forecast = daily_forecast + (f"\nDate: {date}\n High Temp: {high_temp}, Low Temp: {low_temp}, Wind Speed: {wind_speed}")
            daily_forecast = daily_forecast + (f"\n AQI: {aqi_value} ({aqi_category})")


    def print_output(self):
        """
        Print the current time, weather, and forecast to the screen.
        """
        print(self.time_message)
        print(self.weather_message)
        print(self.hourly_forecast)
        print(self.daily_forecast)


    def run(self):
        """
        Run the alarm clock, printing updates at specified intervals.
        """
        short_counter = 0
        long_counter = 0

        while True:
            self.time_message = self.get_time()
            short_counter += 1
            long_counter += 1

            if short_counter % WEATHER_FREQUENCY == 0:
                self.weather_message = self.get_weather()

            if long_counter == FORECAST_FREQUENCY:
                self.hourly_forecast = self.get_hourly_forecast()
                self.aqi_forecast = self.get_hourly_aqi_forecast()
                self.daily_forecast = self.get_daily_summary_forecast()
                long_counter = 0

            self.print_output()
            time.sleep(CLOCK_FREQUENCY)  # Wait for 1 minute

if __name__ == "__main__":
    alarm_clock = AlarmClock()
    alarm_clock.run()