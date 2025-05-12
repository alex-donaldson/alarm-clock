import time
import board
import busio
from adafruit_bme680 import Adafruit_BME680_I2C

class BME688Sensor:
    """
    A class to interface with the BME688 sensor using CircuitPython.
    """

    def __init__(self, i2c=None, sea_level_pressure=1013.25):
        """
        Initialize the BME688 sensor.
        :param i2c: Optional I2C bus object. If None, a default I2C bus is created.
        :param sea_level_pressure: Sea level pressure in hPa for altitude calculations.
        """
        if i2c is None:
            i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = Adafruit_BME680_I2C(i2c)
        self.sensor.sea_level_pressure = sea_level_pressure

    def read_data(self):
        """
        Read data from the BME688 sensor.
        :return: A dictionary containing temperature, humidity, pressure, and gas resistance.
        """
        return {
            "temperature": self.sensor.temperature,  # Celsius
            "humidity": self.sensor.humidity,        # Percentage
            "pressure": self.sensor.pressure,        # hPa
            "gas_resistance": self.sensor.gas        # Ohms
        }

def main():
    """
    Main function to test the BME688 sensor.
    """
    print("Initializing BME688 sensor...")
    bme688 = BME688Sensor()

    while True:
        data = bme688.read_data()
        print(f"Temperature: {data['temperature']:.2f} °C")
        print(f"Humidity: {data['humidity']:.2f} %")
        print(f"Pressure: {data['pressure']:.2f} hPa")
        print(f"Gas Resistance: {data['gas_resistance']:.2f} Ohms")
        print()
        time.sleep(2)  # Wait for 2 seconds before reading again

if __name__ == "__main__":
    main()