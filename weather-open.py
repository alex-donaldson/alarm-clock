import urllib.request
import json
from datetime import datetime

OWM_ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={key}"
KEY_FILE = '/private/keys/openweather.txt'

class RemoteWeatherOpen:
    """
    Fetch and process weather data from OpenWeatherMap One Call API.
    """

    def __init__(self, lat, lon, key=None):
        self.lat = lat
        self.lon = lon
        if key is None:
            with open(KEY_FILE, encoding="utf-8") as f:
                key = f.read().strip()
        self.key = key
        self.url = OWM_ONECALL_URL.format(lat=self.lat, lon=self.lon, key=self.key)
        self.data = self._fetch_data()

    def _fetch_data(self):
        response = urllib.request.urlopen(self.url)
        return json.loads(response.read().decode('utf8'))

    def get_current_weather(self):
        """
        Return current weather as a dictionary.
        """
        current = self.data['current']
        return {
            "datetime": datetime.fromtimestamp(current['dt']),
            "temperature": current['temp'],
            "humidity": current['humidity'],
            "pressure": current['pressure'],
            "wind_speed": current['wind_speed'],
            "weather": current['weather'][0]['description'].capitalize(),
            "icon": current['weather'][0]['icon']
        }

    def get_daily_forecast(self, days=7):
        """
        Return a list of daily forecasts (default 7 days).
        """
        daily = self.data['daily'][:days]
        forecast = []
        for day in daily:
            forecast.append({
                "date": datetime.fromtimestamp(day['dt']).strftime("%Y-%m-%d"),
                "high_temp": day['temp']['max'],
                "low_temp": day['temp']['min'],
                "humidity": day['humidity'],
                "pressure": day['pressure'],
                "wind_speed": day['wind_speed'],
                "weather": day['weather'][0]['description'].capitalize(),
                "icon": day['weather'][0]['icon']
            })
        return forecast

def main():
    lat, lon = 47.697, -122.3222  # Example coordinates
    weather = RemoteWeatherOpen(lat, lon)
    print("Current Weather:")
    print(weather.get_current_weather())
    print("\n7-Day Forecast:")
    for day in weather.get_daily_forecast():
        print(day)

if __name__ == "__main__":
    main()