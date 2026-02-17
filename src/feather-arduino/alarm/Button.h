#pragma once
#include <Arduino.h>

class Button {
public:
  Button(uint8_t pin, bool activeLow = true, unsigned long holdMillis = 1000, unsigned long debounceMillis = 50);
  void begin();
  void update();
  bool wasPressed();    // short press detected since last update
  bool wasReleased();   // release detected
  bool isHeld();        // currently held (after holdMillis)
  bool wasHeld();       // hold event detected since last update
private:
  uint8_t _pin;
  bool _activeLow;
  unsigned long _holdMillis;
  unsigned long _debounceMillis;

  bool _state; // logical state (true = pressed)
  bool _lastStableState;
  unsigned long _lastChangeMillis;
  unsigned long _pressStartMillis;
  bool _heldEventReported;

  bool _pressedEvent;
  bool _releasedEvent;
  bool _heldEvent;
};
