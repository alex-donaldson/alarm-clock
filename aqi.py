
#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime

# https://www.airnowapi.org/aq/forecast/zipCode/?format=json&zipCode=98115&API_KEY=
AQI_URL =  'https://www.airnowapi.org/aq/forecast/zipCode/?format=json&zipCode={zip}&API_KEY={key}'
FORECAST_PROPERTY = 'forecastHourly'
KEY_FILE = '/private/keys/aqi.txt'
        
# 2025-03-23T21:00:00-07:00
AQI_DATE_FORMAT = "%Y-%m-%d"

OUT_TIME_FORMAT = '%A %m/%d'


class AqiDay(object):

    def __init__(self, date, aqi, human_readable):
        self.date = date
        self.aqi = aqi
        self.human_readable = human_readable

    def __str__(self):
        return f'{self.date.strftime(OUT_TIME_FORMAT)}\nAQI: {self.aqi} ({self.human_readable})'

class RemoteAQI(object):

    def __init__(self, zip, key):
        self.zip = zip
        self.key = key
        self.forecast_url = AQI_URL.format(zip=self.zip, key=key)
        self.forecast_date = None
        self.generate_forecasts()
        
    
    def get_raw_forecast_data(self):
        return json.loads(urllib.request.urlopen(self.forecast_url).read().decode('utf8'))
    

    def generate_forecasts(self):
        today = datetime.today().date()
        # only grab forecast data 1/day 
        if not self.forecast_date or today > self.forecast_date:
            print('grabbing new forecast data')
            forecasts = {}
            for p in self.get_raw_forecast_data():
                date = self.get_date(p['DateForecast'])
                forecasts[date] = AqiDay(date=date, aqi=p['AQI'], human_readable=p['Category']['Name'])

            self.forecasts = forecasts
            self.forecast_date = today

    def get_forecasts(self):
        # Checks to see if new forecast data is available before returning
        self.generate_forecasts()
        return self.forecasts
    
    def get_date(self, time_str):
        return datetime.strptime(time_str, AQI_DATE_FORMAT)
    
    def get_day(self, time_str):
        start_time = self.get_date(time_str)
        return start_time.strftime("%A")
    
    def get_aqi_string(self, period):
        return f'AQI: {period['AQI']} {period['Category']['Name']}'

def main():
    with open(KEY_FILE, encoding="utf-8") as f:
        key = f.read()
    f.close()
    ra = RemoteAQI(98115, key)
    # print(json.dumps(ra.get_raw_forecast_data(), indent=4))
    data = ra.get_forecasts()
    for p in data:
        print(data[p])


if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    main()
