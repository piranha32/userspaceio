# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Test blocking event using built in button
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time
from argparse import *
from cffi import FFI
from libgpiod import libgpiod


class buttonwait:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.gpiod = libgpiod.libgpiod()
        self.lib = self.gpiod.lib
        self.ffi = self.gpiod.ffi    
    
    def main(self, chip, line):
        """Wait for edge for 5 seconds or timeout.
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
                if self.lib.gpiod_line_request_falling_edge_events(gpiod_line, consumer.encode('utf-8')) == 0:
                    timespec = self.ffi.new("struct timespec*")
                    timespec.tv_sec = 5
                    print("Press button within 5 seconds")
                    rc = self.lib.gpiod_line_event_wait(gpiod_line, timespec)
                    if rc == 0:
                        print("Timed out")
                    elif rc == 1:
                        event = self.ffi.new("struct gpiod_line_event*")
                        # Read event off queue
                        self.lib.gpiod_line_event_read(gpiod_line, event)
                        if event.event_type == self.lib.GPIOD_LINE_EVENT_RISING_EDGE:
                            print("Rising edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.ts.tv_sec)))
                        else:
                            print("Falling edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.ts.tv_sec)))
                    else:
                        print("Unable request falling edge for line %d" % line)            
                self.lib.gpiod_line_release(gpiod_line)
            else:
                print("Unable to get line %d" % line)
            self.lib.gpiod_chip_close(gpiod_chip)    
        else:
            print("Unable to open chip %d" % chip)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip number (default 1 '/dev/gpiochip1')", type=int, default=1)
    parser.add_argument("--line", help="GPIO line number (default 3 button on NanoPi Duo)", type=int, default=3)
    args = parser.parse_args()
    obj = buttonwait()
    obj.main(args.chip, args.line)
