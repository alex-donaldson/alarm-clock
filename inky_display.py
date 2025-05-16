import time
from bme import BME688Sensor
from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw

class InkyDisplay:
    """
    A class to interface with the Pimoroni Inky e-ink display.
    """

    def __init__(self):
        """
        Initialize the Inky display.
        """
        self.display = auto()  # Automatically detect the Inky display
        self.display.set_border(self.display.WHITE)
        self.width = self.display.WIDTH
        self.height = self.display.HEIGHT
        self.image = Image.new("P", (self.width, self.height), self.display.WHITE)
        self.draw = ImageDraw.Draw(self.image)

    def clear(self):
        """
        Clear the display by filling it with a white background.
        """
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.display.WHITE)
        self.display.set_image(self.image)
        self.display.show()

    def print_message(self, message, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size=22):
        """
        Print a message to the Inky display.
        :param message: The message to display.
        :param font_path: Path to the font file.
        :param font_size: Font size for the message.
        """
        self.clear()
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_width, text_height = font.getbbox(message)
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        self.draw.text((x, y), message, fill=self.display.BLACK, font=font)
        self.display.set_image(self.image)
        self.display.show()

def main():
    """
    Main function to test the Inky display.
    """
    print("Initializing Inky display...")
    inky = InkyDisplay()
    print("Initializing BME688 sensor...")
    bme688 = BME688Sensor()

    while True:
        data = bme688.read_data()
        
        message = (f"Temperature C: {data['temperature']:.2f} °C")
        temperature_f = (data['temperature'] * 9 / 5) + 32
        message = message + (f"\nTemperature F: {temperature_f:.2f} °F")
        message = message + (f"\nHumidity: {data['humidity']:.2f} %")
        message = message + (f"\nPressure: {data['pressure']:.2f} hPa")
        message = message + (f"\nGas Resistance: {data['gas_resistance']:.2f} Ohms")
        message = message + (f"\nRelative Humidity: {data['relative_humidity']:.2f} %")
        message = message + (f"\nAltitude: {data['altitude']:.2f} m")
        inky.print_message(message)
        time.sleep(3600)  # Wait for 2 seconds before reading again
    # Example message
    # message = "Hello, Inky!"
    # print(f"Displaying message: {message}")
    # inky.print_message(message)

if __name__ == "__main__":
    main()