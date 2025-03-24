#!/usr/bin/python3

import urllib.request
import json
DEFAULT_DATA = {'zip' : '98115', 'city': 'Seattle', 'state': 'WA', 'lat': '47.697029', 'lon': '-122.322217'}
REAUIRED_FIELDS = ['zip', 'city', 'region', 'lat', 'lon']

class Location(object):

    def __init__(self):
        try:
            ip = self.get_ip()
            data = self.get_ip_data(ip)
            if self.validate_data(data):
                self.data = data
            else:
                print("data was invalid, using default")
                self.data = DEFAULT_DATA
        except:
            print('lookup failed, using defaults')
            self.data = DEFAULT_DATA

    def get_ip(self):

        return urllib.request.urlopen('https://ident.me').read().decode('utf8')

    def get_ip_data(self, ipaddr):
        return json.loads(urllib.request.urlopen('http://ip-api.com/json/%s' % (ipaddr)).read().decode('utf8'))

    def get_zip(self):
        print(self)
        return self.data['zip']
    
    def get_city(self):
        return self.data['city']
    
    def get_state(self):
        return self.data['state']
    
    def get_lat(self):
        return self.data['lat']

    def get_long(self):
        return self.data['long']
    
    def validate_data(self, ip_data):
        status = ip_data.get('status')
        if status is None or status != "success":
            return False
        for field in REAUIRED_FIELDS:
            if ip_data.get(field) is None:
                print('field %s is missing' % (field))
                return False
        return True


def main():
    w = Location()
    ip = w.get_ip()
    print(ip)
    print(w.data)
    ip_data = w.get_ip_data(ip)
    print(json.dumps(ip_data, indent=4))
    print(w.get_zip())

if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    main()