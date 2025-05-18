import time
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from inky.auto import auto

from weather import RemoteWeather
from openweatheraqi import RemoteAQI
from bme import BME688Sensor
from sgp30_sensor import SGP30Sensor

BACKGROUND_IMAGE = "background_imgs/tree.jpg"

class InkyDisplay:
    def __init__(self):
        self.display = auto()
        self.display.set_border(self.display.WHITE)
        self.width = self.display.WIDTH
        self.height = self.display.HEIGHT
        # Load background image and convert to palette
        self.background = Image.open(BACKGROUND_IMAGE).resize((self.width, self.height)).convert("P")
        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)
        # Adjust font paths/sizes as needed for your system
        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)

    def clear(self):
        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)

    def render(self, weather, aqi, bme, sgp30):
        self.clear()
        # --- Current Weather (center, largest area) ---
        x_c, y_c = 350, 60
        self.draw.text((x_c, y_c), f"{weather['current_temp']}°F", self.display.RED, font=self.font_large)
        self.draw.text((x_c, y_c+80), f"{weather['current_desc']}", self.display.BLACK, font=self.font_med)
        self.draw.text((x_c, y_c+130), f"Humidity: {bme['humidity']:.0f}%", self.display.BLACK, font=self.font_med)
        self.draw.text((x_c, y_c+180), f"Pressure: {bme['pressure']:.0f} hPa", self.display.BLACK, font=self.font_med)
        self.draw.text((x_c, y_c+230), f"eCO2: {sgp30['eCO2']} ppm", self.display.BLACK, font=self.font_med)
        self.draw.text((x_c, y_c+270), f"TVOC: {sgp30['TVOC']} ppb", self.display.BLACK, font=self.font_med)
        self.draw.text((x_c, y_c+320), f"AQI: {aqi['aqi']} ({aqi['category']})", self.display.RED, font=self.font_med)

        # --- Right: 6-day Forecast ---
        x_r, y_r = 900, 40
        self.draw.text((x_r, y_r), "Next 6 Days", self.display.RED, font=self.font_med)
        y_r += 50
        for day in weather['daily'][1:7]:
            self.draw.text((x_r, y_r), f"{day['date']}", self.display.BLACK, font=self.font_small)
            self.draw.text((x_r+120, y_r), f"H:{day['high_temp']}° L:{day['low_temp']}°", self.display.RED, font=self.font_small)
            self.draw.text((x_r+320, y_r), f"Precip:{day.get('precip', '--')}%", self.display.BLACK, font=self.font_small)
            self.draw.text((x_r+480, y_r), f"AQI:{day.get('aqi', '--')}", self.display.RED, font=self.font_small)
            y_r += 45

        # --- Left: 24-hour Hourly Forecast ---
        x_l, y_l = 20, 40
        self.draw.text((x_l, y_l), "Next 24 Hours", self.display.RED, font=self.font_med)
        y_l += 50
        for hour in weather['hourly'][:24]:
            self.draw.text((x_l, y_l), f"{hour['time']}", self.display.BLACK, font=self.font_small)
            self.draw.text((x_l+90, y_l), f"{hour['temp']}°", self.display.RED, font=self.font_small)
            self.draw.text((x_l+160, y_l), f"P:{hour.get('precip', '--')}%", self.display.BLACK, font=self.font_small)
            self.draw.text((x_l+240, y_l), f"AQI:{hour.get('aqi', '--')}", self.display.RED, font=self.font_small)
            y_l += 32
            if y_l > self.height - 100:
                break  # Prevent overflow

        # --- Bottom: Sunrise/Sunset ---
        sunrise = weather.get('sunrise', '--:--')
        sunset = weather.get('sunset', '--:--')
        self.draw.text((self.width//2-200, self.height-60), f"Sunrise: {sunrise}   Sunset: {sunset}", self.display.YELLOW, font=self.font_med)

        self.display.set_image(self.image)
        self.display.show()

def fetch_all_data():
    # --- Weather ---
    weather_api = RemoteWeather(47.697, -122.3222)
    daily = weather_api.get_daily_forecast()
    hourly = weather_api.get_hourly_forecast()
    current = weather_api.get_current_weather()
    sunrise = current.get('sunrise', '--:--')
    sunset = current.get('sunset', '--:--')
    # --- AQI ---
    aqi_api = RemoteAQI(47.697, -122.3222, open('/private/keys/openweather.txt').read().strip())
    aqi_now = aqi_api.get_detailed_current_aqi()
    # --- BME688 ---
    bme = BME688Sensor().read_data()
    # --- SGP30 ---
    sgp30 = SGP30Sensor().read_data()
    # --- Compose data dicts for rendering ---
    weather = {
        'current_temp': int(current['temperature']),
        'current_desc': current['weather'],
        'daily': daily,
        'hourly': hourly,
        'sunrise': sunrise,
        'sunset': sunset,
    }
    return weather, aqi_now, bme, sgp30

def main():
    inky = InkyDisplay()
    while True:
        weather, aqi, bme, sgp30 = fetch_all_data()
        inky.render(weather, aqi, bme, sgp30)
        # Update every hour
        time.sleep(3600)

if __name__ == "__main__":
    main()