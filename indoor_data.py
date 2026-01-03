from weather_gov import RemoteWeather
from openweatheraqi import RemoteAQI
from bme import BME688Sensor
from sgp30_sensor import SGP30Sensor
from location import Location

class DataAggregator:

    def fetch_all_data(self):
        # --- BME688 ---
        bme = BME688Sensor().read_data()
        # --- SGP30 ---
        sgp30 = SGP30Sensor().read_data()
        # --- Compose data dicts for rendering ---
    
        return bme, sgp30
    

def main():
    data_aggregator = DataAggregator()
    bme, sgp30 = data_aggregator.fetch_all_data()
    print("Indoor Dat a Data:")
    print("BME688 Data:", bme)
    print("SGP30 Data:", sgp30)

if __name__ == "__main__":
    main()