#include "Button.h"

Button::Button(uint8_t pin, bool activeLow, unsigned long holdMillis, unsigned long debounceMillis)
    : _pin(pin), _activeLow(activeLow), _holdMillis(holdMillis), _debounceMillis(debounceMillis) {
}

void Button::begin() {
  pinMode(_pin, INPUT_PULLUP);
  _state = false;
  _lastStableState = false;
  _lastChangeMillis = millis();
  _pressStartMillis = 0;
  _heldEventReported = false;
  _pressedEvent = false;
  _releasedEvent = false;
  _heldEvent = false;
}

void Button::update() {
  _pressedEvent = false;
  _releasedEvent = false;
  _heldEvent = false;

  bool raw = digitalRead(_pin);
  bool logical = _activeLow ? !raw : raw;

  unsigned long now = millis();

  if (logical != _lastStableState) {
    // possible bounce
    if (now - _lastChangeMillis >= _debounceMillis) {
      // stable change
      _lastStableState = logical;
      _lastChangeMillis = now;

      if (logical) {
        // pressed
        _pressStartMillis = now;
        _heldEventReported = false;
        _pressedEvent = true;
      } else {
        // released
        _releasedEvent = true;
        _pressStartMillis = 0;
        _heldEventReported = false;
      }
    }
  } else {
    // stable
    if (_lastStableState) {
      // currently pressed, check hold
      if (!_heldEventReported && (_pressStartMillis != 0) && (now - _pressStartMillis >= _holdMillis)) {
        _heldEvent = true;
        _heldEventReported = true;
      }
    }
  }

  _state = _lastStableState;
}

bool Button::wasPressed() { return _pressedEvent; }
bool Button::wasReleased() { return _releasedEvent; }
bool Button::isHeld() { return _state && _heldEventReported; }
bool Button::wasHeld() { return _heldEvent; }
