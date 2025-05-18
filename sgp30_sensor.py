import time
import board
import busio
from adafruit_sgp30 import Adafruit_SGP30

class SGP30Sensor:
    """
    A class to interface with the SGP30 air quality sensor using CircuitPython.
    """

    def __init__(self, i2c=None):
        """
        Initialize the SGP30 sensor.
        :param i2c: Optional I2C bus object. If None, a default I2C bus is created.
        """
        if i2c is None:
            i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = Adafruit_SGP30(i2c, address=0x58)

        # Initialize the sensor
        self.sensor.iaq_init()
        print("SGP30 sensor initialized.")
        print(f"Serial Number: {self.sensor.serial}")

    def read_data(self):
        """
        Read data from the SGP30 sensor.
        :return: A dictionary containing eCO2 and TVOC levels.
        """
        return {
            "eCO2": self.sensor.eCO2,  # Equivalent CO2 in ppm
            "TVOC": self.sensor.TVOC   # Total Volatile Organic Compounds in ppb
        }

    def get_baseline(self):
        """
        Get the current baseline values from the sensor.
        :return: A tuple containing the eCO2 and TVOC baseline values.
        """
        return self.sensor.baseline_eCO2, self.sensor.baseline_TVOC

def main():
    """
    Main function to test the SGP30 sensor.
    """
    print("Initializing SGP30 sensor...")
    sgp30 = SGP30Sensor()

    # Wait for the sensor to stabilize (15 seconds recommended)
    print("Allowing the sensor to stabilize...")
    for i in range(15):
        print(f"Stabilizing... {15 - i} seconds remaining")
        time.sleep(1)

    while True:
        data = sgp30.read_data()
        print(f"eCO2: {data['eCO2']} ppm")
        print(f"TVOC: {data['TVOC']} ppb")
        print()
        time.sleep(2)  # Wait for 2 seconds before reading again

if __name__ == "__main__":
    main()