# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Use libgpiod context less event loop to implement blocking callback
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time
from argparse import *
from cffi import FFI
from libgpiod import libgpiod


class buttoncallback:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.gpiod = libgpiod.libgpiod()
        self.lib = self.gpiod.lib
        self.ffi = self.gpiod.ffi

        # Inner Callback function
        @self.ffi.callback("int (int evtype, unsigned int offset, const struct timespec *ts, void *data)")
        def buttonCallback(evtype, offset, ts, data):
            # Use a try/except or an exception will cause an endless loop
            try:
                if evtype == self.lib.GPIOD_CTXLESS_EVENT_CB_TIMEOUT:
                    rc = self.lib.GPIOD_CTXLESS_EVENT_CB_RET_STOP
                    print("Timeout")
                else:
                    rc = self.lib.GPIOD_CTXLESS_EVENT_CB_RET_OK
                    if evtype == self.lib.GPIOD_CTXLESS_EVENT_CB_RISING_EDGE:
                        print("Rising  edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(ts.tv_sec)))
                    else:
                        print("Falling edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(ts.tv_sec)))
            except:
                rc = self.lib.GPIOD_CTXLESS_EVENT_CB_RET_ERR
                print("Unexpected error:", sys.exc_info()[0])
            return rc

        # Expose callback to object instance
        self.buttonCallback = buttonCallback

    def main(self, chip, line):
        """Print edge events for 10 seconds.
        """         
        print ("libgpiod version %s" % self.ffi.string(self.lib.gpiod_version_string()).decode('utf-8'))
        # Consumer is script name without .py
        consumer = sys.argv[0][:-3]
        # 10 second timeout
        timespec = self.ffi.new("struct timespec*")
        timespec.tv_sec = 10
        print("Press and release button, timeout in 10 seconds\n")
        # Blocking poll until timeout, note gpiod_simple_event_poll_cb is passed as a NULL
        if self.lib.gpiod_ctxless_event_loop(chip.encode('utf-8'), line, False, consumer.encode('utf-8'), timespec, self.ffi.NULL, self.buttonCallback, self.ffi.NULL) != 0:
            print("gpiod_ctxless_event_loop error, check --chip and --line values")     


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip name (default '/dev/gpiochip1')", type=str, default="/dev/gpiochip1")
    parser.add_argument("--line", help="GPIO line number (default 3 button on NanoPi Duo)", type=int, default=3)
    args = parser.parse_args()
    obj = buttoncallback()
    obj.main(args.chip, args.line)
