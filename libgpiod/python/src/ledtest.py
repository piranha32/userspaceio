# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Simple LED blink
-------------
Using the NanoPi Duo connect a 220Ω resistor to the anode (the long pin of
the LED), then the resistor to 3.3 V, and connect the cathode (the short
pin) of the LED to line 203 (IOG11). The anode of LED connects to a
current-limiting resistor and then to 3.3V. Therefore, to turn on an LED,
we need to make pin 12 low (0V) level.

See images/ledtest.jpg for schematic.
"""

import sys, time
from argparse import *
from cffi import FFI
from libgpiod import libgpiod


class ledtest:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.gpiod = libgpiod.libgpiod()
        self.lib = self.gpiod.lib
        self.ffi = self.gpiod.ffi    
    
    def main(self, chip, line):
        """Turn LED on and off once.
        """         
        print ("libgpiod version %s" % self.ffi.string(self.lib.gpiod_version_string()).decode('utf-8'))
        gpiod_chip = self.lib.gpiod_chip_open_by_number(chip)
        # Verify the chip was opened
        if gpiod_chip != self.ffi.NULL:
            print("Name: %s, label: %s, lines: %d" % (self.ffi.string(gpiod_chip.name).decode('utf-8'), self.ffi.string(gpiod_chip.label).decode('utf-8'), gpiod_chip.num_lines))
            gpiod_line = self.lib.gpiod_chip_get_line(gpiod_chip, line)
            # Verify we have line
            if gpiod_line != self.ffi.NULL:
                consumer = sys.argv[0][:-3]
                # This will set line for output and set initial value (LED on)
                if self.lib.gpiod_line_request_output(gpiod_line, consumer.encode('utf-8'), 0) == 0:
                    print("\nLED on")
                    time.sleep(3)
                    # LED off
                    self.lib.gpiod_line_set_value(gpiod_line, 1)
                    print("LED off")
                else:
                    print("Unable to set line %d to output" % line)
                self.lib.gpiod_line_release(gpiod_line)
            else:
                print("Unable to get line %d" % line)
            self.lib.gpiod_chip_close(gpiod_chip)    
        else:
            print("Unable to open chip %d" % chip)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip number (default 0 '/dev/gpiochip0')", type=int, default=0)
    parser.add_argument("--line", help="GPIO line number (default 203 IOG11 on NanoPi Duo)", type=int, default=203)
    args = parser.parse_args()
    obj = ledtest()
    obj.main(args.chip, args.line)
