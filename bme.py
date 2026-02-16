import time
import board
import busio
from adafruit_bme680 import Adafruit_BME680_I2C
# from log_config import get_logger

# logger = get_logger('bme', 'bme.log')

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
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
            except Exception as e:
                # logger.exception("Failed to initialize I2C: %s", e)
                raise

        # Try common I2C addresses for BME sensors
        addresses = [None, 0x77, 0x76]
        self.sensor = None
        for addr in addresses:
            try:
                if addr is None:
                    # logger.debug("Attempting to create BME sensor without explicit address")
                    self.sensor = Adafruit_BME680_I2C(i2c)
                else:
                    # logger.debug("Attempting to create BME sensor with address 0x%02X", addr)
                    self.sensor = Adafruit_BME680_I2C(i2c, address=addr)
                # If creation succeeded, break
                # logger.info("BME sensor initialized (address=%s)", hex(addr) if addr else 'auto')
                break
            except Exception as e:
                # logger.debug("Could not initialize sensor at %s: %s", hex(addr) if addr else 'auto', e)
                self.sensor = None
                continue

        if self.sensor is None:
            # logger.error("Failed to initialize BME sensor on any known address")
            raise RuntimeError("BME sensor not found on I2C bus")

        self.sensor.sea_level_pressure = sea_level_pressure

    def read_data(self):
        """
        Read data from the BME688 sensor.
        Returns both Celsius and Fahrenheit for temperature to remain backward-compatible:
        - "temperature" (Celsius)
        - "temperature_f" (Fahrenheit)
        """
        try:
            temp_c = self.sensor.temperature
            temp_f = (temp_c * 9 / 5) + 32 if temp_c is not None else None
            data = {
                "temperature": temp_c,
                "temperature_f": temp_f,
                "humidity": getattr(self.sensor, 'humidity', None),
                "pressure": getattr(self.sensor, 'pressure', None),
                "gas_resistance": getattr(self.sensor, 'gas', None),
                "relative_humidity": getattr(self.sensor, 'relative_humidity', None),
                "altitude": getattr(self.sensor, 'altitude', None),
            }
            # logger.debug("Read BME data: %s", data)
            return data
        except Exception as e:
            # logger.exception("Error reading BME sensor data: %s", e)
            return {
                "temperature": None,
                "temperature_f": None,
                "humidity": None,
                "pressure": None,
                "gas_resistance": None,
                "relative_humidity": None,
                "altitude": None,
            }

def main():
    """
    Main function to test the BME688 sensor.
    """
    print("Initializing BME688 sensor...")
    bme688 = BME688Sensor()

    while True:
        data = bme688.read_data()
        # Use safe formatting if values are None
        def fmt(v, fmt_str="{:.2f}"):
            return fmt_str.format(v) if v is not None else "N/A"

        print("Temperature C: %s °C", fmt(data['temperature']))
        print("Temperature F: %s °F", fmt(data['temperature_f']))
        print("Humidity: %s %", fmt(data['humidity']))
        print("Pressure: %s hPa", fmt(data['pressure']))
        print("Gas Resistance: %s Ohms", fmt(data['gas_resistance']))
        print("Relative Humidity: %s %", fmt(data['relative_humidity']))
        print("Altitude: %s m", fmt(data['altitude']))
        print("")
        time.sleep(2)  # Wait for 2 seconds before reading again

if __name__ == "__main__":
    main()