import time
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from inky.auto import auto

from weather_gov import RemoteWeather
from openweatheraqi import RemoteAQI
from bme import BME688Sensor
from sgp30_sensor import SGP30Sensor

BACKGROUND_IMAGE = "background_imgs/tree2.jpg"

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
        # --- Center: Current Weather (smaller font) ---
        x_c, y_c = 320, 60  # Move center block right
        self.draw.text((x_c, y_c), f"{weather['current_temp']}°F", self.display.BLACK, font=self.font_large)
        self.draw.text((x_c, y_c+60), f"{weather['current_desc']}", self.display.BLACK, font=self.font_med)
        self.draw.text((x_c, y_c+110), "Indoor Sensors", self.display.BLACK, font=self.font_small)
        bme_temp_f = (bme['temperature'] * 9 / 5) + 32
        self.draw.text((x_c, y_c+140), f"Temp: {bme_temp_f:.1f}°F", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c, y_c+170), f"Humidity: {bme['humidity']:.0f}%", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c, y_c+200), f"Pressure: {bme['pressure']:.0f} hPa", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c, y_c+230), f"eCO2: {sgp30['eCO2']} ppm", self.display.BLACK, font=self.font_small)
        self.draw.text((x_c, y_c+260), f"TVOC: {sgp30['TVOC']} ppb", self.display.BLACK, font=self.font_small)
        timestamp = datetime.now().strftime("Updated: %Y-%m-%d %H:%M")
        self.draw.text((x_c, y_c+290), timestamp, self.display.BLACK, font=self.font_small)

        # --- Right: 6-day Forecast ---
        x_r, y_r = 600, 40
        self.draw.text((x_r, y_r), "Next 6 Days", self.display.BLACK, font=self.font_med)
        y_r += 50
        for day in weather['daily'][1:7]:
            try:
                day_label = datetime.strptime(day['date'], "%Y-%m-%d").strftime("%a")
            except Exception:
                day_label = day['date']
            self.draw.text((x_r, y_r), f"{day_label}", self.display.BLACK, font=self.font_small)
            self.draw.text((x_r+60, y_r), f"H:{day['high_temp']}° L:{day['low_temp']}°", self.display.BLACK, font=self.font_small)
            self.draw.text((x_r+220, y_r), f"Precip:{day.get('precip', '--')}%", self.display.BLACK, font=self.font_small)
            y_r += 45

        # --- Left: 12-hour Hourly Forecast (smaller font, fits vertically) ---
        x_l, y_l = 20, 40
        self.draw.text((x_l, y_l), "Next 12 Hours", self.display.BLACK, font=self.font_small)
        y_l += 28
        for hour in weather['hourly'][:12]:
            self.draw.text((x_l, y_l), f"{hour['time']}", self.display.BLACK, font=self.font_small)
            self.draw.text((x_l+70, y_l), f"{hour['temp']}°", self.display.BLACK, font=self.font_small)
            self.draw.text((x_l+130, y_l), f"P:{hour.get('precip', '--')}%", self.display.BLACK, font=self.font_small)
            y_l += 28

        # --- Bottom: Sunrise/Sunset ---
        sunrise = weather.get('sunrise', '--:--')
        sunset = weather.get('sunset', '--:--')
        self.draw.text((self.width//2-200, self.height-60), f"Sunrise: {sunrise}   Sunset: {sunset}", self.display.BLACK, font=self.font_med)

        self.display.set_image(self.image)
        self.display.show()

def fetch_all_data():
    # --- Weather ---
    weather_api = RemoteWeather(47.697, -122.3222)
    daily = weather_api.get_daily_forecast()
    hourly = weather_api.get_hourly_forecast()
    current = weather_api.get_current_weather()
    sunrise = weather_api.get_sunrise()
    sunset = weather_api.get_sunset()
    # --- AQI ---
    # aqi_api = RemoteAQI(47.697, -122.3222, open('/private/keys/openweather.txt').read().strip())
    # aqi_now = aqi_api.get_detailed_current_aqi()
    # --- BME688 ---
    bme = BME688Sensor().read_data()
    # --- SGP30 ---
    sgp30 = SGP30Sensor().read_data()
    # --- Compose data dicts for rendering ---
    weather = {
        'current_temp': int(current['temperature']),
        'current_desc': current['short_forecast'],
        'daily': daily,
        'hourly': hourly,
        'sunrise': sunrise,
        'sunset': sunset,
    }
    return weather, None, bme, sgp30

def main():
    inky = InkyDisplay()
    while True:
        weather, aqi, bme, sgp30 = fetch_all_data()
        inky.render(weather, aqi, bme, sgp30)
        # Update every hour
        time.sleep(3600)

if __name__ == "__main__":
    main()