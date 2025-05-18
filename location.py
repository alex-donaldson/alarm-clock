#!/usr/bin/python3

import urllib.request
import json

# Default location data
DEFAULT_DATA = {
    'zip': '98115',
    'city': 'Seattle',
    'region': 'WA',
    'lat': '47.697029',
    'lon': '-122.322217'
}
REQUIRED_FIELDS = ['zip', 'city', 'region', 'lat', 'lon']

class Location:
    """
    A class to fetch and validate location data based on the user's IP address.
    """

    def __init__(self):
        try:
            ip = self.get_ip()
            data = self.get_ip_data(ip)
            print("IP Data:", data)
            if self.validate_data(data):
                self.data = data
            else:
                print("Data was invalid, using default location.")
                self.data = DEFAULT_DATA
        except Exception as e:
            print(f"Lookup failed ({e}), using default location.")
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

    def get_zip(self):
        """
        Get the ZIP code from the location data.
        """
        return self.data['zip']

    def get_city(self):
        """
        Get the city from the location data.
        """
        return self.data['city']

    def get_state(self):
        """
        Get the state from the location data.
        """
        return self.data['state']

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
                print(f"Field '{field}' is missing.")
                return False
        return True


def main():
    """
    Main function to test the Location class.
    """
    location = Location()
    print("Public IP:", location.get_ip())
    print("Location Data:", location.data)
    print("City:", location.get_city())
    print("State:", location.get_state())
    print("ZIP Code:", location.get_zip())
    print("Latitude:", location.get_lat())
    print("Longitude:", location.get_lon())


if __name__ == '__main__':
    main()