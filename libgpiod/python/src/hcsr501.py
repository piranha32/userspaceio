# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
HC-SR501 sensor example
-------------
Monitor rising edge (motion detected) and falling edge (no motion)
"""

import sys, time
from argparse import *
from cffi import FFI
from libgpiod import libgpiod


class hcsr501:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.gpiod = libgpiod.libgpiod()
        self.lib = self.gpiod.lib
        self.ffi = self.gpiod.ffi

        # Inner Callback function
        @self.ffi.callback("int (int evtype, unsigned int offset, const struct timespec *ts, void *data)")
        def motionCallback(evtype, offset, ts, data):
            # Use a try/except or an exception will cause an endless loop
            try:
                if evtype == self.lib.GPIOD_CTXLESS_EVENT_CB_TIMEOUT:
                    rc = self.lib.GPIOD_CTXLESS_EVENT_CB_RET_STOP
                    print("Timeout")
                else:
                    rc = self.lib.GPIOD_CTXLESS_EVENT_CB_RET_OK
                    if evtype == self.lib.GPIOD_CTXLESS_EVENT_CB_RISING_EDGE:
                        print("Motion detected %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(ts.tv_sec)))
                    else:
                        print("No motion       %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(ts.tv_sec)))
            except:
                rc = self.lib.GPIOD_CTXLESS_EVENT_CB_RET_ERR
                print("Unexpected error:", sys.exc_info()[0])
            return rc

        # Expose callback to object instance
        self.motionCallback = motionCallback

    def main(self, chip, line):
        """Show motion for 30 seconds.
        """         
        print("HC-SR501 motion detector, timeout in 300 seconds\n")
        # Consumer is script name without .py
        consumer = sys.argv[0][:-3]
        # 30 second timeout
        timespec = self.ffi.new("struct timespec*")
        timespec.tv_sec = 300
        # Blocking poll until timeout, note gpiod_simple_event_poll_cb is passed as a NULL
        if self.lib.gpiod_ctxless_event_loop(args.chip.encode('utf-8'), args.line, False, consumer.encode('utf-8'), timespec, self.ffi.NULL, self.motionCallback, self.ffi.NULL) != 0:
            print("gpiod_ctxless_event_loop error, check --chip and --line values")        


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip name (default '/dev/gpiochip0')", type=str, default="/dev/gpiochip0")
    parser.add_argument("--line", help="GPIO line number (default 203 IOG11 on NanoPi Duo)", type=int, default=203)
    args = parser.parse_args()
    obj = hcsr501()
    obj.main(args.chip, args.line)
