#!/usr/bin/python3

import urllib.request
import json
from log_config import get_logger

logger = get_logger('latlong', 'latlong.log')

# Default location data
DEFAULT_DATA = {
    'lat': '47.697029',
    'lon': '-122.322217'
}
REQUIRED_FIELDS = ['lat', 'lon']

class LatLong:
    """
    A class to fetch and validate Lat/Long data based on the user's IP address.
    """

    def __init__(self):
        try:
            ip = self.get_ip()
            data = self.get_ip_data(ip)
            logger.debug("IP Data: %s", data)
            if self.validate_data(data):
                self.data = data
            else:
                logger.warning("Data was invalid, using default location.")
                self.data = DEFAULT_DATA
        except Exception as e:
            logger.exception("Lookup failed, using default location: %s", e)
            self.data = DEFAULT_DATA

    def get_ip(self):
        """
        Fetch the user's public IP address.
        """
        return urllib.request.urlopen('https://ident.me').read().decode('utf8')

    def get_ip_data(self, ipaddr):
        """
        Fetch location data based on the user's IP address.
        """
        url = f'http://ip-api.com/json/{ipaddr}'
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode('utf8'))

    def get_lat(self):
        """
        Get the latitude from the location data.
        """
        return self.data['lat']

    def get_lon(self):
        """
        Get the longitude from the location data.
        """
        return self.data['lon']

    def validate_data(self, ip_data):
        """
        Validate the fetched location data to ensure all required fields are present.
        """
        if ip_data.get('status') != "success":
            return False
        for field in REQUIRED_FIELDS:
            if ip_data.get(field) is None:
                logger.warning("Field '%s' is missing.", field)
                return False
        return True


def main():
    """
    Main function to test the Location class.
    """
    location = LatLong()
    print("Public IP:", location.get_ip())
    print("Location Data:", location.data)
    print("Latitude:", location.get_lat())
    print("Longitude:", location.get_lon())

if __name__ == '__main__':
    main()