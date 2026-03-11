#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "Adafruit_seesaw.h"
#include <seesaw_neopixel.h>
#include "RTClib.h"
#include "Adafruit_ThinkInk.h"
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include <Adafruit_AW9523.h>
#include "Button.h"

#define SRAM_CS     6
#define EPD_CS      9
#define EPD_DC      10

#define EPD_SPI &SPI  // primary SPI
#define EPD_RESET -1  // can set to -1 and share with microcontroller Reset!
#define EPD_BUSY -1   // can set to -1 to not use a pin (will wait a fixed delay)

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BME680 bme(&Wire);

// 4.2" Grayscale/Monochrome displays with 416x240 pixels and SSD1683 chipset
ThinkInk_370_Mono_BAAMFGN eink(EPD_DC, EPD_RESET, EPD_CS, SRAM_CS, EPD_BUSY, EPD_SPI);

RTC_PCF8523 rtc;
char daysOfTheWeek[7][12] = { "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" };


#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library.
// On an arduino UNO:       A4(SDA), A5(SCL)
// On an arduino MEGA 2560: 20(SDA), 21(SCL)
// On an arduino LEONARDO:   2(SDA),  3(SCL), ...
#define OLED_RESET -1        // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3D  ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define SS_SWITCH 24
#define SS_NEOPIX 6

#define SEESAW_ADDR 0x36

Adafruit_seesaw ss;
seesaw_NeoPixel sspixel = seesaw_NeoPixel(1, SS_NEOPIX, NEO_GRB + NEO_KHZ800);

Adafruit_AW9523 aw;

bool alarmOn = false;
bool inAlarm = false;
bool isSnoozed = false;
bool isNapping = false;
uint8_t alarmHour = 0;
uint8_t alarmMin = 0;
uint8_t napHour = 0;
uint8_t napMin = 0;
uint8_t snoozeHour = 0;
uint8_t snoozeMin = 0;
TimeSpan napDuration(0, 0, 45, 0); // 45 min
TimeSpan snoozeDuration(0, 0, 9, 0); // 9 min
bool adjustingTime = false;
bool adjustingAlarm = false;
bool adjustingDate = false;
bool adjustingMonth = false;
bool adjustingDay = false;
bool adjustingYear = false;
bool adjustingHour = false;
bool adjustingMin = false;
bool isScreenOn = true;
bool isAdjusting = false;

int encoder_position = 0;
uint8_t prevAdjustHour = 0;
uint8_t prevAdjustMin = 0;
uint8_t prevAdjustMonth = 1;
uint8_t prevAdjustDay = 1;
uint16_t prevAdjustYear = 2024;
bool prevEncoderButtonState = false;

uint8_t prevTimeMin = 0;
int prevDate = 0;
int prevMMHG = 0;
int pressureTrend = 0;

int glowStart = 0;
int glowDuration = 20000;  // light stays on for 20 seconds
bool isGlowing = false;

// Button pins (adjust to your wiring)
const uint8_t alarmPin = 9;
const uint8_t timePin = 6;
const uint8_t snoozePin = 5;
const uint8_t glowPin = 1;

// Button helpers (active-low wiring assumed)
Button alarmButton(alarmPin, true, 1000);
Button timeButton(timePin, true, 1000);
Button snoozeButton(snoozePin, true, 1000);

void setup() {
  Serial.begin(115200);
  Serial.flush();
  initGlow();
  glowOff();
  while (!Serial) delay(10);
  initRTC();
  initSeesaw();
  initOled();
  initEink();
  initBME();
  // initialize buttons
  alarmButton.begin();
  timeButton.begin();
  snoozeButton.begin();
  prevTimeMin = rtc.now().minute();
  prevDate = rtc.now().day();
  drawEink();
}
//

void loop() {
  handleButtonPress();
  handleAlarmButton();
  handleTimeButton();
  handleSnoozeButton();
  handleAdjusting();
  handleGlow();
  uint8_t currMin = rtc.now().minute();
  if (currMin != prevTimeMin) {
    drawEink();
    prevTimeMin = currMin;
  }
  checkPressureTrend();
  // don't overwhelm serial port
  delay(10);
}

int getTemp() {
  return (bme.temperature * 9 / 5) + 32;
}

int getPressure() {
  return bme.pressure * 0.750062 / 100.0;
}

void drawEink() {
  eink.flush();
  eink.clearBuffer();
  eink.setTextSize(4);
  eink.setTextColor(EPD_BLACK);
  eink.setTextWrap(true);

  if (!bme.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }

  DateTime now = rtc.now();
  String timeStr = getTimeString(now.hour(), now.minute());
  
  // Center the time text
  int16_t x1, y1;
  uint16_t w, h;
  eink.getTextBounds(timeStr, 0, 0, &x1, &y1, &w, &h);
  int timeX = (eink.width() - w) / 2;
  int timeY = (eink.height() / 2) - (h / 2);
  
  eink.setCursor(timeX, timeY);
  eink.print(timeStr);
  Serial.println(timeStr);

  eink.setTextSize(2);
  eink.setCursor(10, timeY + 80);
  eink.print("Temp: " + String(getTemp()) + "F");
  eink.println("  Hum: " + String(bme.humidity) + "%");
  eink.print("mmHG: " + String(getPressure()) + " -- " + getPressureTrendString());

  Serial.print("Temp: " + String(getTemp()) + "F  ");
  Serial.println("Hum: " + String(bme.humidity) + "%");
  Serial.print("mmHG: " + String(getPressure()) + " -- ");
  Serial.println(getPressureTrendString());

  Serial.println(getAlarmStateString());
  Serial.println(getNapStateString());

  eink.display();
  delay(200);
}

String getAlarmStateString() {
  String alarmString = "Alarm: ";
  if (alarmOn) {
    alarmString = alarmString + getTimeString(alarmHour, alarmMin);
  } else {
    alarmString = alarmString + "OFF";
  }
  return alarmString;
}


String getNapStateString() {
  String napString = "Nap: ";
  if (isNapping) {
    napString += getTimeString(napHour, napMin);
  } else {
    napString += "OFF";
  }
  return napString;
}

String getPressureTrendString() {
  String trend = "same";
  if (pressureTrend > 0) {
    trend = "better";
  } else if (pressureTrend < 0) {
    trend = "worse";
  }
  return trend;
}

void checkPressureTrend() {
  DateTime now = rtc.now();
  int day = now.day();
  if (day != prevDate) {
    pressureTrend = 0;
    int currMMHG = getPressure();
    // Update trend and prevMMHG
    if (currMMHG > prevMMHG) {
      pressureTrend = 1;
    } else if (currMMHG < prevMMHG) {
      pressureTrend = -1;
    }
    prevMMHG = currMMHG;
    prevDate = day;
  }
}

String getTimeString(uint8_t h, uint8_t m) {
  char timeStr[6];  // Enough for "HH:MM" + null terminator
  sprintf(timeStr, "%02d:%02d", h, m);
  return String(timeStr);
}

bool wasEncoderButtonPressed() {
  bool currButtonState = !ss.digitalRead(SS_SWITCH);  // true if pressed
  bool wasPressed = false;
  if (prevEncoderButtonState != currButtonState && currButtonState) {
    Serial.println("button pressed!");
    wasPressed = true;
  }
  prevEncoderButtonState = currButtonState;
  return wasPressed;
}

// Poll hardware buttons and encoder; must be called frequently from loop()
void handleButtonPress() {
  // update button state machines
  alarmButton.update();
  timeButton.update();
  snoozeButton.update();

  // encoder button handling is performed in handleEncoderButtonPress()
  handleEncoderButtonPress();
}

void setupAdjusting() {
  Serial.println("Adjusting Hours");
  adjustingHour = true;
  DateTime now = rtc.now();
  prevAdjustHour = now.hour();
  prevAdjustMin = now.minute();
  isAdjusting = true;
  screenOn();
  printTimeOledWithSelection(prevAdjustHour, prevAdjustMin, adjustingHour, adjustingMin);
}

void setupDateAdjusting() {
  Serial.println("Adjusting Month");
  adjustingMonth = true;
  DateTime now = rtc.now();
  prevAdjustMonth = now.month();
  prevAdjustDay = now.day();
  prevAdjustYear = now.year();
  isAdjusting = true;
  adjustingDate = true;
  screenOn();
  printDateOledWithSelection(prevAdjustMonth, prevAdjustDay, prevAdjustYear, adjustingMonth, adjustingDay, adjustingYear);
}

// Button Handlers
void handleAlarmButton() {
  // alarmButton state machine handles debouncing and hold detection
  if (alarmButton.wasHeld()) {
    if (!adjustingHour && !adjustingMin && !adjustingMonth && !adjustingDay && !adjustingYear) {
      setupAdjusting();
      adjustingAlarm = true;
    }
  } else if (alarmButton.wasPressed()) {
    // toggle alarm
    alarmOn = !alarmOn;
    String alarmText = "Alarm ";
    if (alarmOn) {
      alarmText += "on";
    } else {
      alarmText += "off";
    }
    drawTempTextOled(alarmText);
  }
}

void handleTimeButton() {
  if (timeButton.wasHeld()) {
    if (!adjustingHour && !adjustingMin && !adjustingMonth && !adjustingDay && !adjustingYear) {
      setupAdjusting();
      adjustingTime = true;
    }
  } else if (timeButton.wasPressed()) {
    isNapping = !isNapping;
    if (isNapping) {
      // Nap Time: add 45 minutes
      DateTime now = rtc.now();
      DateTime nap = now + napDuration;
      napHour = nap.hour();
      napMin = nap.minute();
      drawTempTextOled("Nap time");
    } else {
      drawTempTextOled("Nap off");
    }
  }
}

void handleSnoozeButton() {
  if (snoozeButton.wasHeld()) {
    Serial.println("Snooze button held");
    if (!adjustingHour && !adjustingMin && !adjustingMonth && !adjustingDay && !adjustingYear) {
      setupDateAdjusting();
    }
  } else if (snoozeButton.wasPressed()) {
    Serial.println("Snooze button pressed");
    if (inAlarm) {
      inAlarm = false;
      DateTime now = rtc.now();
      DateTime snooze = now + snoozeDuration;
      snoozeHour = snooze.hour();
      snoozeMin = snooze.minute();
      isSnoozed = true;
    } else {
      if (isGlowing) {
        glowOff();
      } else {
        glowOn();
      }
    }
  }
}

void handleEncoderButtonPress() {
  if (isAdjusting) {
    if (wasEncoderButtonPressed()) {
      // move the thing we are editing
      if (adjustingHour) {
        Serial.println("Adjusting Mins. Hours set to: " + String(prevAdjustHour));
        adjustingHour = false;
        adjustingMin = true;
      } else if (adjustingMin) {
        Serial.println("done adjusting. Mins set to: " + String(prevAdjustMin));
        adjustingMin = false;
        if (adjustingTime) {
          Serial.println("Setting time");
          DateTime now = rtc.now();
          rtc.adjust(DateTime(now.year(), now.month(), now.day(), prevAdjustHour, prevAdjustMin, now.second()));
        } else if (adjustingAlarm) {
          alarmHour = prevAdjustHour;
          alarmMin = prevAdjustMin;
        }
        adjustingTime = false;
        adjustingAlarm = false;
        screenOff();
        drawEink();
      } else if (adjustingMonth) {
        Serial.println("Adjusting Day. Month set to: " + String(prevAdjustMonth));
        adjustingMonth = false;
        adjustingDay = true;
      } else if (adjustingDay) {
        Serial.println("Adjusting Year. Day set to: " + String(prevAdjustDay));
        adjustingDay = false;
        adjustingYear = true;
      } else if (adjustingYear) {
        Serial.println("Done adjusting date. Year set to: " + String(prevAdjustYear));
        adjustingYear = false;
        adjustingDate = false;
        isAdjusting = false;
        Serial.println("Setting date");
        DateTime now = rtc.now();
        rtc.adjust(DateTime(prevAdjustYear, prevAdjustMonth, prevAdjustDay, now.hour(), now.minute(), now.second()));
        screenOff();
        drawEink();
      }
    }
  }
}

void drawTempTextOled(String text) {
  screenOn();
  drawTextOled(text);
  delay(1000);
  screenOff();
}

void printTimeOled(uint8_t hour, uint8_t min) {
  drawTextOled(getTimeString(hour, min));
}

void printDateOledWithSelection(uint8_t month, uint8_t day, uint16_t year, bool highlightMonth, bool highlightDay, bool highlightYear) {
  if (isScreenOn) {
    oled.clearDisplay();
    oled.setTextSize(2);  // Smaller text for date
    
    // Month names
    const char* monthNames[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
    
    int cursorX = 5;
    int cursorY = 0;
    
    // Draw month
    if (highlightMonth) {
      oled.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    } else {
      oled.setTextColor(SSD1306_WHITE, SSD1306_BLACK);
    }
    oled.setCursor(cursorX, cursorY);
    oled.print(monthNames[month - 1]);
    
    // Draw space
    oled.setTextColor(SSD1306_WHITE, SSD1306_BLACK);
    oled.print(" ");
    
    // Draw day
    char dayStr[3];
    sprintf(dayStr, "%02d", day);
    if (highlightDay) {
      oled.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    } else {
      oled.setTextColor(SSD1306_WHITE, SSD1306_BLACK);
    }
    oled.print(dayStr);
    
    // Draw comma and space
    oled.setTextColor(SSD1306_WHITE, SSD1306_BLACK);
    oled.print(", ");
    
    // Draw year
    char yearStr[5];
    sprintf(yearStr, "%04d", year);
    if (highlightYear) {
      oled.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    } else {
      oled.setTextColor(SSD1306_WHITE, SSD1306_BLACK);
    }
    oled.print(yearStr);
    
    oled.display();
    delay(100);
  }
}

void checkAndUpdateAlarm() {
  DateTime now = rtc.now();
  if (alarmOn && now.hour() == alarmHour && now.minute() == alarmMin) {
    inAlarm = true;
  } else if (isSnoozed && now.hour() == snoozeHour && now.minute() == snoozeMin) {
    inAlarm = true;
  } else if (isNapping && now.hour() == napHour && now.minute() == napMin) {
    inAlarm = true;
  }
}

void handleAlarm() {
  // Do something to make alarm sounds.
}

int handleEncoder() {
  int32_t new_pos = ss.getEncoderPosition();
  int delta = 0;
  if (encoder_position != new_pos) {
    if (encoder_position < new_pos) {
      delta = 1;
    } else {
      delta = -1;
    }
    encoder_position = new_pos;
  }
  // don't overwhelm serial port
  delay(10);
  Serial.println("Delta = " + String(delta));

  return delta;
}

void handleAdjusting() {
  if (adjustingHour) {
    adjustHours();
  } else if (adjustingMin) {
    adjustMin();
  } else if (adjustingMonth) {
    adjustMonth();
  } else if (adjustingDay) {
    adjustDay();
  } else if (adjustingYear) {
    adjustYear();
  }
  
  if (adjustingDate) {
    printDateOledWithSelection(prevAdjustMonth, prevAdjustDay, prevAdjustYear, adjustingMonth, adjustingDay, adjustingYear);
  } else {
    printTimeOledWithSelection(prevAdjustHour, prevAdjustMin, adjustingHour, adjustingMin);
  }
}

void handleGlow() {
  if (isGlowing) {
    if (millis() - glowStart >= glowDuration) {
      glowOff();
    }
  }
}

void adjustHours() {
  int delta = handleEncoder();
  int hour = prevAdjustHour + delta;
  if (hour == 0) {
    hour = 24;
  } else if (hour == 25) {
    hour = 1;
  }

  Serial.println("Hour = " + String(hour));
  prevAdjustHour = hour;
}

void adjustMin() {
  int delta = handleEncoder();
  int min = prevAdjustMin + delta;
  if (min == -1) {
    min = 59;
  } else if (min == 60) {
    min = 0;
  }
  Serial.println("Min = " + String(min));
  prevAdjustMin = min;
}

void adjustMonth() {
  int delta = handleEncoder();
  int month = prevAdjustMonth + delta;
  if (month == 0) {
    month = 12;
  } else if (month == 13) {
    month = 1;
  }
  Serial.println("Month = " + String(month));
  prevAdjustMonth = month;
}

void adjustDay() {
  int delta = handleEncoder();
  int day = prevAdjustDay + delta;
  
  // Get max days for the current month/year
  int maxDays = getMaxDaysInMonth(prevAdjustMonth, prevAdjustYear);
  
  if (day < 1) {
    day = maxDays;
  } else if (day > maxDays) {
    day = 1;
  }
  Serial.println("Day = " + String(day));
  prevAdjustDay = day;
}

int getMaxDaysInMonth(int month, int year) {
  switch (month) {
    case 2: // February
      return (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) ? 29 : 28;
    case 4: case 6: case 9: case 11: // 30-day months
      return 30;
    default: // 31-day months
      return 31;
  }
}

void adjustYear() {
  int delta = handleEncoder();
  int year = prevAdjustYear + delta;
  if (year < 2020) {
    year = 2020;
  } else if (year > 2050) {
    year = 2050;
  }
  Serial.println("Year = " + String(year));
  prevAdjustYear = year;
}

void initGlow() {
  Serial.println("Adafruit AW9523 GPIO Expander test!");

  if (!aw.begin(0x58)) {
    Serial.println("AW9523 not found? Check wiring!");
    while (1) delay(10);  // halt forever
  }

  Serial.println("AW9523 found!");
  aw.pinMode(glowPin, OUTPUT);
}

void initRTC() {
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }
  if (!rtc.initialized() || rtc.lostPower()) {
    Serial.println("RTC is NOT initialized, let's set the time!");
    rtc.adjust(DateTime(2015, 10, 12, 0, 0, 0));
  }
  rtc.start();
}

void initBME() {
  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1)
      ;
  }

  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);  // 320*C for 150 ms

  if (!bme.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }
  prevMMHG = getPressure();
}

void initSeesaw() {
  Serial.println("Looking for seesaw!");

  if (!ss.begin(SEESAW_ADDR) || !sspixel.begin(SEESAW_ADDR)) {
    Serial.println("Couldn't find seesaw on default address");
    while (1) delay(10);
  }
  Serial.println("seesaw started");

  uint32_t version = ((ss.getVersion() >> 16) & 0xFFFF);
  if (version != 4991) {
    Serial.print("Wrong firmware loaded? ");
    Serial.println(version);
    while (1) delay(10);
  }
  Serial.println("Found Product 4991");

  // set not so bright!
  sspixel.setBrightness(1);
  sspixel.show();

  // use a pin for the built in encoder switch
  ss.pinMode(SS_SWITCH, INPUT_PULLUP);

  // get starting position
  encoder_position = ss.getEncoderPosition();

  Serial.println("Turning on interrupts");
  delay(10);
  ss.setGPIOInterrupts((uint32_t)1 << SS_SWITCH, 1);
  ss.enableEncoderInterrupt();
}

void initEink() {
  Serial.println("Adafruit EPD full update test in mono");
  Serial.println("3.7 Monochrome EPD with UC8253 chipset");
  eink.begin();
}

void initOled() {
  if (!oled.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }

  Serial.println("turning on screen");
  oled.display();
  delay(200);
  Serial.println("trying to print the time");

  DateTime now = rtc.now();
  printTimeOled(now.hour(), now.minute());
  delay(2000);

  oled.clearDisplay();
  screenOff();
  Serial.println("screen init done");
}

void drawTextOled(String text) {
  if (isScreenOn) {
    oled.clearDisplay();
    oled.setTextSize(4);
    oled.setTextColor(SSD1306_WHITE);
    oled.setCursor(5, 0);
    oled.println(text);
    oled.display();
    delay(100);
  }
}


void screenOff() {
  oled.ssd1306_command(SSD1306_DISPLAYOFF);
  isScreenOn = false;
}

void screenOn() {
  oled.ssd1306_command(SSD1306_DISPLAYON);
  isScreenOn = true;
}

void glowOn() {
  aw.digitalWrite(glowPin, LOW);
  Serial.println("glow on");
  isGlowing = true;
  glowStart = millis();
}


void glowOff() {
  aw.digitalWrite(glowPin, HIGH);
  isGlowing = false;
  Serial.println("glow off");
}
