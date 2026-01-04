"""AW9523 LED controller using Adafruit's CircuitPython driver.

This module prefers `adafruit_aw9523` (CircuitPython) and Blinka's
`busio`/`board` for I2C access. If those libraries are not available it
falls back to the previous `smbus2` implementation so the module still
works on plain Linux systems without Blinka.

Install one of:
  pip install adafruit-circuitpython-aw9523
or
  pip install smbus2

Example (CircuitPython/Blika):
    from src.utils.aw9523_led import AW9523LED
    ctl = AW9523LED(led_channels=(0,1))
    ctl.on(0)
    ctl.set_brightness(1, 128)
    ctl.cleanup()
"""

from __future__ import annotations

import time
from typing import Sequence, List

# Try CircuitPython/Adafruit driver first
try:
    import board  # type: ignore
    import busio  # type: ignore
    import adafruit_aw9523  # type: ignore
except Exception:  # pragma: no cover - may not be installed on CI
    board = None  # type: ignore
    busio = None  # type: ignore
    adafruit_aw9523 = None  # type: ignore

# Fallback to smbus2 if CircuitPython libs are not available
try:
    from smbus2 import SMBus  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    SMBus = None  # type: ignore


class AW9523LED:
    """Controller for AW9523 LEDs.

    This implementation uses `adafruit_aw9523` when available. It accepts
    either a pre-created CircuitPython `I2C` object via the `i2c` arg or
    will create one using `board.SCL`/`board.SDA` if running under Blinka.

    If Adafruit libraries are not installed it falls back to a simple
    `smbus2` register write implementation compatible with the previous
    version of this module.
    """

    DEFAULT_I2C_ADDR = 0x58
    PWM_BASE = 0x10

    def __init__(self, i2c=None, i2c_bus: int = 1, address: int | None = None, led_channels: Sequence[int] = (0, 1)) -> None:
        self._led_channels = tuple(led_channels)
        self._address = address or self.DEFAULT_I2C_ADDR
        self._backend = None
        self._i2c = None
        self._driver = None

        # Prefer Adafruit CircuitPython driver
        if adafruit_aw9523 is not None:
            # Use provided I2C or create one from board if possible
            if i2c is not None:
                self._i2c = i2c
            else:
                if busio is None or board is None:
                    raise RuntimeError("Adafruit AW9523 driver available but busio/board not found; pass an I2C object via `i2c=`")
                self._i2c = busio.I2C(board.SCL, board.SDA)

            # Create the driver. The Adafruit library may not accept an address arg
            # so we don't pass it. If the user needs a non-standard address they
            # should provide a pre-configured I2C device object.
            self._driver = adafruit_aw9523.AW9523(self._i2c)
            self._backend = "adafruit"
            # Configure channels as PWM outputs if supported by the driver
            try:
                # Some builds expose .leds or .pwm as list-like APIs
                for ch in self._led_channels:
                    try:
                        # set mode to PWM (if supported)
                        self._driver.mode(ch, 1)  # type: ignore[attr-defined]
                    except Exception:
                        # ignore if method not present
                        pass
            except Exception:
                pass
            return

        # Otherwise fall back to smbus2
        if SMBus is None:
            raise RuntimeError("No supported AW9523 driver found. Install 'adafruit-circuitpython-aw9523' or 'smbus2'.")

        self._backend = "smbus"
        self._bus_num = i2c_bus
        self._bus = SMBus(self._bus_num)

    @property
    def address(self) -> int:
        return self._address

    def _write_register(self, register: int, value: int) -> None:
        if not (0 <= value <= 0xFF):
            raise ValueError("value must be 0..255")
        if self._backend == "smbus":
            self._bus.write_byte_data(self._address, register & 0xFF, value & 0xFF)
        else:
            # Try to use driver-level APIs if present; otherwise attempt direct register access
            # Adafruit driver doesn't expose raw register write; fall back to using pwm API
            raise RuntimeError("Direct register writes are not supported with the Adafruit backend")

    def set_brightness(self, channel: int, brightness: int) -> None:
        """Set brightness for a channel (0-255)."""
        if channel not in self._led_channels:
            raise ValueError(f"channel {channel} not configured; choose from {self._led_channels}")
        if not (0 <= brightness <= 255):
            raise ValueError("brightness must be in range 0..255")

        if self._backend == "adafruit":
            # Try common APIs in order
            try:
                # Some versions expose .pwm as list-like
                pwm = getattr(self._driver, "pwm", None)
                if pwm is not None:
                    pwm[channel] = int(brightness)
                    return
            except Exception:
                pass

            try:
                # Some versions expose a set_pwm method
                set_pwm = getattr(self._driver, "set_pwm", None)
                if set_pwm is not None:
                    set_pwm(channel, int(brightness))
                    return
            except Exception:
                pass

            try:
                # As a last resort, attempt to set led brightness via 'leds' collection
                leds = getattr(self._driver, "leds", None)
                if leds is not None:
                    leds[channel].duty_cycle = int(brightness) << 8  # if 16-bit duty expected
                    return
            except Exception:
                pass

            # If we couldn't set via driver, raise
            raise RuntimeError("Could not set brightness via Adafruit AW9523 driver - API not recognized")

        # smbus fallback
        reg = self.PWM_BASE + int(channel)
        self._write_register(reg, brightness)

    def on(self, channel: int, brightness: int = 255) -> None:
        self.set_brightness(channel, brightness)

    def off(self, channel: int) -> None:
        self.set_brightness(channel, 0)

    def toggle(self, channel: int, brightness: int = 255, delay: float = 0.1) -> None:
        self.on(channel, brightness)
        time.sleep(delay)
        self.off(channel)

    def discover(self) -> List[int]:
        """Discover readable/usable channels. Returns list of channels that appear to work."""
        found: List[int] = []
        if self._backend == "adafruit":
            for ch in self._led_channels:
                try:
                    # Try reading a pwm value or setting a harmless value then restoring
                    pwm = getattr(self._driver, "pwm", None)
                    if pwm is not None:
                        _ = pwm[ch]
                        found.append(ch)
                        continue
                except Exception:
                    pass
                # try leds collection
                try:
                    leds = getattr(self._driver, "leds", None)
                    if leds is not None and leds[ch] is not None:
                        found.append(ch)
                        continue
                except Exception:
                    pass
            return found

        # smbus fallback: try reading PWM registers
        for ch in self._led_channels:
            reg = self.PWM_BASE + ch
            try:
                val = self._bus.read_byte_data(self._address, reg)
                found.append(ch)
            except Exception:
                pass
        return found

    def cleanup(self) -> None:
        """Close any resources allocated by the chosen backend."""
        if self._backend == "smbus":
            try:
                self._bus.close()
            except Exception:
                pass
        elif self._backend == "adafruit":
            # busio I2C has no explicit close on some ports; try deinit() if present
            try:
                if hasattr(self._i2c, "deinit"):
                    self._i2c.deinit()  # type: ignore[attr-defined]
            except Exception:
                pass


if __name__ == "__main__":  # pragma: no cover - CLI usage
    import argparse

    parser = argparse.ArgumentParser(description="AW9523 LED test (2 channels)")
    parser.add_argument("--address", type=lambda x: int(x, 0), default=AW9523LED.DEFAULT_I2C_ADDR, help="I2C address (hex ok).")
    parser.add_argument("--leds", type=int, nargs=2, default=(0, 1), help="Two LED channels to control")
    args = parser.parse_args()

    # Try to create using CircuitPython driver if available
    try:
        ctl = AW9523LED(led_channels=tuple(args.leds))
    except RuntimeError:
        # Fallback to smbus: use bus 1
        ctl = AW9523LED(i2c_bus=1, address=args.address, led_channels=tuple(args.leds))

    print(f"Using backend={ctl._backend}, address=0x{ctl.address:02x}, channels={ctl._led_channels}")
    present = ctl.discover()
    print("Discovered channels:", present)

    try:
        for ch in ctl._led_channels:
            print(f"Blinking channel {ch}")
            ctl.on(ch, 255)
            time.sleep(0.25)
            ctl.off(ch)
    finally:
        ctl.cleanup()
