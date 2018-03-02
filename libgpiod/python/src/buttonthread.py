# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Use a thread to monitor edge events in background
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time, threading
from argparse import *
from cffi import FFI
from libgpiod import libgpiod


class buttonthread:

    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.gpiod = libgpiod.libgpiod()
        self.lib = self.gpiod.lib
        self.ffi = self.gpiod.ffi

    def waitForEdge(self, line, consumer, timeoutSecs):
        print("Thread running\n")
        timespec = self.ffi.new("struct timespec*")
        timespec.tv_sec = timeoutSecs
        rc = 1
        event = self.ffi.new("struct gpiod_line_event*")
        while rc == 1:
            # Wait for event
            rc = self.lib.gpiod_line_event_wait(line, timespec)
            if rc == 0:
                print("Thread timed out")
            elif rc == 1:
                # Get event off queue
                if self.lib.gpiod_line_event_read(line, event) == 0:
                    if event.event_type == self.lib.GPIOD_LINE_EVENT_RISING_EDGE:
                        print("Rising  edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.ts.tv_sec)))
                    else:
                        print("Falling edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.ts.tv_sec)))
                else:
                    print("gpiod_line_event_read error")
                    rc = -1
            else:
                print("gpiod_line_event_wait error")
                rc = -1
        print("Thread exit")                

    def main(self, chip, line):
        """Use thread to wait for edge events while main method does other stuff.
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
                # Request detection of both edge events
                if self.lib.gpiod_line_request_both_edges_events(gpiod_line, consumer.encode('utf-8')) == 0:
                    # Kick off thread
                    thread = threading.Thread(target=self.waitForEdge, args=(gpiod_line, consumer.encode('utf-8'), 5,))
                    thread.start()
                    count = 0
                    # Just simulating main program doing something else
                    while count < 30 and thread.isAlive():
                        print("Main program doing stuff, press button")
                        time.sleep(1)
                        count += 1
                    # If thread is still alive wait for it to time out
                    if thread.isAlive():
                        print("Waiting for thread to exit, stop pressing button for 5 seconds")
                        thread.join()
                else:
                    print("Unable request both edges for line %d" % line)
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
    obj = buttonthread()
    obj.main(args.chip, args.line)
