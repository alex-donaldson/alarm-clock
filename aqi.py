#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime

# Constants
AQI_URL = 'https://www.airnowapi.org/aq/forecast/zipCode/?format=json&zipCode={zip}&API_KEY={key}'
KEY_FILE = '/private/keys/aqi.txt'
AQI_DATE_FORMAT = "%Y-%m-%d"
OUT_TIME_FORMAT = '%A %m/%d'

class AqiDay:
    """
    Represents a single day's AQI data.
    """

    def __init__(self, date, aqi, human_readable):
        self.date = date
        self.aqi = aqi
        self.human_readable = human_readable

    def __str__(self):
        return f'{self.date.strftime(OUT_TIME_FORMAT)}\nAQI: {self.aqi} ({self.human_readable})'

class RemoteAQI:
    """
    A class to fetch and process AQI data from the AirNow API.
    """

    def __init__(self, zip_code, key):
        self.zip_code = zip_code
        self.key = key
        self.forecast_url = AQI_URL.format(zip=self.zip_code, key=self.key)
        self.forecast_date = None
        self.forecasts = {}
        self.generate_forecasts()

    def get_raw_forecast_data(self):
        """
        Fetch raw AQI forecast data from the API.
        """
        response = urllib.request.urlopen(self.forecast_url)
        return json.loads(response.read().decode('utf8'))

    def generate_forecasts(self):
        """
        Generate AQI forecasts, ensuring data is refreshed daily.
        """
        today = datetime.today().date()
        if not self.forecast_date or today > self.forecast_date:
            print('Fetching new AQI forecast data...')
            forecasts = {}
            for p in self.get_raw_forecast_data():
                date = self.get_date(p['DateForecast'])
                forecasts[date] = AqiDay(
                    date=date,
                    aqi=p['AQI'],
                    human_readable=p['Category']['Name']
                )
            self.forecasts = forecasts
            self.forecast_date = today

    def get_forecasts(self):
        """
        Return the AQI forecasts, refreshing data if necessary.
        """
        self.generate_forecasts()
        return self.forecasts

    def get_date(self, time_str):
        """
        Convert a time string to a datetime object.
        """
        return datetime.strptime(time_str, AQI_DATE_FORMAT)

    def get_day(self, time_str):
        """
        Convert a time string to a day of the week.
        """
        start_time = self.get_date(time_str)
        return start_time.strftime("%A")

    def get_aqi_string(self, period):
        """
        Generate a formatted AQI string for a forecast period.
        """
        return f"AQI: {period['AQI']} ({period['Category']['Name']})"

def main():
    """
    Main function to fetch and display AQI data.
    """
    with open(KEY_FILE, encoding="utf-8") as f:
        key = f.read().strip()

    ra = RemoteAQI(98115, key)
    forecasts = ra.get_forecasts()

    for date, forecast in forecasts.items():
        print(forecast)

if __name__ == '__main__':
    main()