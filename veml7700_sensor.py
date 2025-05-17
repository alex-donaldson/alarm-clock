import time
import board
import busio
from adafruit_veml7700 import VEML7700

class VEML7700Sensor:
    """
    A class to interface with the VEML7700 ambient light sensor using CircuitPython.
    """

    def __init__(self, i2c=None):
        """
        Initialize the VEML7700 sensor.
        :param i2c: Optional I2C bus object. If None, a default I2C bus is created.
        """
        if i2c is None:
            i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = VEML7700(i2c, address=0x16)

    def read_data(self):
        """
        Read data from the VEML7700 sensor.
        :return: A dictionary containing ambient light and white light levels.
        """
        return {
            "ambient_light": self.sensor.lux,  # Ambient light in lux
            "white_light": self.sensor.white  # White light level (raw value)
        }

def main():
    """
    Main function to test the VEML7700 sensor.
    """
    print("Initializing VEML7700 sensor...")
    veml7700 = VEML7700Sensor()

    while True:
        data = veml7700.read_data()
        print(f"Ambient Light: {data['ambient_light']:.2f} lux")
        print(f"White Light: {data['white_light']}")
        print()
        time.sleep(2)  # Wait for 2 seconds before reading again

if __name__ == "__main__":
    main()