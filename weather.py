
#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime
# https://api.weather.gov/points/47.697,-122.3222
# then pull the url for properties": {
        # "@id": "https://api.weather.gov/points/47.697,-122.3222",
        # "@type": "wx:Point",
        # "cwa": "SEW",
        # "forecastOffice": "https://api.weather.gov/offices/SEW",
        # "gridId": "SEW",
        # "gridX": 126,
        # "gridY": 72,
        # "forecast": "https://api.weather.gov/gridpoints/SEW/126,72/forecast",
        # "forecastHourly": "https://api.weather.gov/gridpoints/SEW/126,72/forecast/hourly",
        # "forecastGridData": "https://api.weather.gov/gridpoints/SEW/126,72",

# {
#     "number": 4,
#     "name": "",
#     "startTime": "2025-03-24T00:00:00-07:00",
#     "endTime": "2025-03-24T01:00:00-07:00",
#     "isDaytime": false,
#     "temperature": 53,
#     "temperatureUnit": "F",
#     "temperatureTrend": "",
#     "probabilityOfPrecipitation": {
#         "unitCode": "wmoUnit:percent",
#         "value": 79
#     },
#     "dewpoint": {
#         "unitCode": "wmoUnit:degC",
#         "value": 10
#     },
#     "relativeHumidity": {
#         "unitCode": "wmoUnit:percent",
#         "value": 88
#     },
#     "windSpeed": "15 mph",
#     "windDirection": "SSW",
#     "icon": "https://api.weather.gov/icons/land/night/rain,80?size=small",
#     "shortForecast": "Light Rain",
#     "detailedForecast": ""
# }

# https://www.airnowapi.org/aq/forecast/zipCode/?format=json&zipCode=98115&API_KEY=C67164FA-919E-4490-A652-137696EF7357
WEATHER_URL =  "https://api.weather.gov/points/{lat},{lon}"
FORECAST_PROPERTY = 'forecastHourly'
        
# 2025-03-23T21:00:00-07:00
WEATHER_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

OUT_TIME_FORMAT = '%I:%M %p'

class RemoteWeather(object):

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.forecast_url = self.get_forecast_url()

    def get_forecast_url(self):
        return json.loads(urllib.request.urlopen(WEATHER_URL.format(lat=self.lat, lon=self.lon)).read().decode('utf8'))['properties'][FORECAST_PROPERTY]
    
    def get_raw_forecast_data(self):
        return json.loads(urllib.request.urlopen(self.forecast_url).read().decode('utf8'))
    
    def get_forecast_data(self):
        return self.get_raw_forecast_data()['properties']['periods']
    
    def get_day(self, time_str):
        start_time = datetime.strptime(time_str, WEATHER_TIME_FORMAT)
        return start_time.strftime("%A")

    def get_time_string(self, time_str):
        start_time = datetime.strptime(time_str, WEATHER_TIME_FORMAT).time()
        return start_time.strftime(OUT_TIME_FORMAT)
    
    def get_dur_string(self, start_time, end_time):
        return f'{self.get_day(start_time)} {self.get_time_string(start_time)} - {self.get_time_string(end_time)}'
    
    def get_temp_string(self, period):
        return f'{period['temperature']} {period['temperatureUnit']}'

def main():
    w = RemoteWeather(47.54,-122.3032)
    forecast = w.get_forecast_data()
    current = True
    count = 0
    for p in forecast:
        prefix = ''
        if current:
            prefix = 'Current '
            current = False
        else:
            print(w.get_dur_string(p['startTime'], p['endTime']))
        print(f'{prefix}Temperature: {w.get_temp_string(p)}')
        print(f'{prefix}Wind Speed: {p['windSpeed']}')
        print(f'{prefix}Probability of Precipitation: {p['probabilityOfPrecipitation']['value']}')
        print(f'{prefix}Relative Humidity: {p['relativeHumidity']['value']}\n')
        # print(json.dumps(p, indent=4))
        count += 1
        if count > 3:
            break
        



if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    main()
