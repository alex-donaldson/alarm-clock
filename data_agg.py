from weather_gov import RemoteWeather
from openweatheraqi import RemoteAQI
from bme import BME688Sensor
from sgp30_sensor import SGP30Sensor
from location import Location

class DataAggregator:

    def fetch_all_data(self):

        location = Location()
        lat = location.get_lat()
        lon = location.get_lon()
        # --- Weather ---
        weather_api = RemoteWeather(lat, lon)
        daily = weather_api.get_daily_forecast()
        hourly = weather_api.get_hourly_forecast()
        current = weather_api.get_current_weather()
        print("Current Weather:", current)
        sunrise = weather_api.get_sunrise()
        sunset = weather_api.get_sunset()
        # --- AQI ---
        # aqi_api = RemoteAQI(47.697, -122.3222, open('/private/keys/openweather.txt').read().strip())
        # aqi_now = aqi_api.get_detailed_current_aqi()
        # --- BME688 ---
        bme = BME688Sensor().read_data()
        # --- SGP30 ---
        sgp30 = SGP30Sensor().read_data()
        # --- Compose data dicts for rendering ---
        weather = {
            'current_temp': int(current['temperature']),
            'current_desc': current['short_forecast'],
            'daily': daily,
            'hourly': hourly,
            'sunrise': sunrise,
            'sunset': sunset,
        }
        return weather, None, bme, sgp30
    

def main():
    data_aggregator = DataAggregator()
    weather, aqi, bme, sgp30 = data_aggregator.fetch_all_data()
    print("Weather Data:", weather)
    print("\n\nCurrent Weather:", weather['current_temp'], weather['current_desc'])
    print("\nDaily Forecast:", weather['daily'])
    print("\nHourly Forecast:", weather['hourly'])
    print("AQI Data:", aqi)
    print("BME688 Data:", bme)
    print("SGP30 Data:", sgp30)

if __name__ == "__main__":
    main()