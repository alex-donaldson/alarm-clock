import time
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from data_agg import DataAggregator
from inky.auto import auto



BACKGROUND_IMAGE = "background_imgs/tree2.jpg"
SMALL_FONT_SPACE = 30
SLEEP_TIME = 900

class InkyDisplay:
    def __init__(self):
        self.display = auto()
        self.display.set_border(self.display.WHITE)
        self.width = self.display.WIDTH
        self.height = self.display.HEIGHT
        # Load background image and convert to palette
        self.background = Image.open(BACKGROUND_IMAGE).resize((self.width, self.height)).convert("P")
        # self.image = self.background.copy()
        self.image = Image.new("P", (self.display.width, self.display.height))
        self.draw = ImageDraw.Draw(self.image)
        # Adjust font paths/sizes as needed for your system
        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        self.font_med2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        self.font_xsmall = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)

    def clear(self):
        pass
        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)

    def render(self, weather, aqi, bme, sgp30):
        self.clear()
        # --- Center: Current Weather (smaller font) ---
        x_c, y_c = 280, 60
        self.draw.text((x_c, y_c), f"{weather['current_temp']}°F", self.display.BLACK, font=self.font_large)
        self.draw.text((x_c, y_c+60), f"{weather['current_desc']}", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c, y_c+110), "Indoor Sensors", self.display.BLACK, font=self.font_med2)
        bme_temp_f = (bme['temperature'] * 9 / 5) + 32
        self.draw.text((x_c + 5, y_c+140), f"Temp: {bme_temp_f:.1f}°F", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c + 5, y_c+170), f"Humidity: {bme['humidity']:.0f}%", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c + 5, y_c+200), f"Pressure: {bme['pressure']:.0f} hPa", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c + 5, y_c+230), f"eCO2: {sgp30['eCO2']} ppm", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c + 5, y_c+260), f"TVOC: {sgp30['TVOC']} ppb", self.display.BLACK, font=self.font_small)
        

        # --- Right: 6-day Forecast ---
        x_r, y_r = 550, 20
        self.draw.text((x_r, y_r), "Daily", self.display.BLACK, font=self.font_med)
        y_r += 50
        for day in weather['daily'][:4]:
            day_label = day['name']
            self.draw.text((x_r, y_r), f"{day_label}", self.display.BLACK, font=self.font_small)
            self.draw.text((x_r+5, y_r + SMALL_FONT_SPACE), f"{day['low_temp']} / {day['high_temp']}°", self.display.BLACK, font=self.font_small)
            self.draw.text((x_r+5, y_r + 2 * SMALL_FONT_SPACE), f"Precip:{day.get('percentageOfPrecipitation', '--')}%", self.display.BLACK, font=self.font_small)
            y_r += 90

        # --- Left: 12-hour Hourly Forecast (smaller font, fits vertically) ---
        x_l, y_l = 20, 40
        self.draw.text((x_l, y_l), "Next 12 Hours", self.display.BLACK, font=self.font_med2)
        y_l += 28
        print("Hourly forecast data:", weather['hourly'])
        for hour in weather['hourly'][:12]:
            self.draw.text((x_l, y_l), f"{hour['hour']}:00", self.display.BLACK, font=self.font_small)
            self.draw.text((x_l+70, y_l), f"{hour['temperature']}°", self.display.BLACK, font=self.font_small)
            self.draw.text((x_l+130, y_l), f"P:{hour.get('probabilityOfPrecipitation', '--')}%", self.display.BLACK, font=self.font_small)
            y_l += 28

        # --- Bottom: Sunrise/Sunset ---
        sunrise = weather.get('sunrise', '--:--')
        sunset = weather.get('sunset', '--:--')
        self.draw.text((self.width//2-250, self.height-50), f"Sunrise: {sunrise}   Sunset: {sunset}", self.display.BLACK, font=self.font_small)
        timestamp = datetime.now().strftime("Updated: %Y-%m-%d %H:%M")
        self.draw.text((self.width//2-250, self.height-20), timestamp, self.display.BLACK, font=self.font_xsmall)    
        self.display.set_image(self.image)
        self.display.show()



def main():
    inky = InkyDisplay()
    data = DataAggregator()
    while True:
        weather, aqi, bme, sgp30 = data.fetch_all_data()
        inky.render(weather, aqi, bme, sgp30)
        # Update every hour
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()