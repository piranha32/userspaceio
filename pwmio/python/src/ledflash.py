# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
PWM flashing LED.
-------------

Every second change duty cycle.
"""

import sys, time
from argparse import *
from cffi import FFI
from libpwmio import libpwmio


class ledflash:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.pwm = libpwmio.libpwmio()
        self.lib = self.pwm.lib
        self.ffi = self.pwm.ffi
        
    def changeBrightness(self, device, pwm, period, startDc, dcInc, count, sleepTime):
        """Increase/decrease LED brightness.
        """
        self.lib.pwm_set_period(device, pwm, period)
        dutyCycle = startDc
        i = 0;
        while i < count:
            self.lib.pwm_set_duty_cycle(device, pwm, dutyCycle)
            time.sleep(sleepTime)
            dutyCycle += dcInc
            i += 1
        
    def main(self, device, pwm):
        """Gradually increase intensity of flashing LED.
        """
        try:
            self.pwm.open(device, pwm)
            self.lib.pwm_enable(device, pwm)
            i = 0;
            # Make LED gradually brighter and dimmer
            while i < 10:
                self.changeBrightness(device, pwm, 1000, 0, 10, 100, .005)
                self.changeBrightness(device, pwm, 1000, 1000, -10, 100, .005)
                i += 1
        finally:
            self.lib.pwm_set_duty_cycle(device, pwm, 0)
            self.lib.pwm_set_period(device, pwm, 0)
            self.lib.pwm_disable(device, pwm)        
            self.pwm.close(device)

        
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", help="PWM device number (default 0 = sys/class/pwm/pwmchip0)", type=int, default=0)
    parser.add_argument("--pwm", help="PWM pin (default 0 = /sys/class/pwm/pwmchip0/pwm0)", type=int, default=0)
    args = parser.parse_args()    
    obj = ledflash()
    obj.main(args.device, args.pwm)
