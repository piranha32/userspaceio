# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
libpwmio /sys/class/pwm/pwmchip* interface to PWM.
-------------

Helper methods added to handle repetitive operations.
"""

import time
from cffi import FFI


class libpwmio:

    def __init__(self):
        self.ffi = FFI()
        # Specify each C function, struct and constant you want a Python binding for
        # Copy-n-paste with minor edits
        self.ffi.cdef("""
        int pwm_open_device(int device);

        int pwm_close_device(int device);

        int pwm_enable(int device, int pmw);

        int pwm_disable(int device, int pmw);

        int pwm_set_polarity(int device, int pmw, const char *polarity);

        int pwm_set_period(int device, int pwm, int period);

        int pwm_set_duty_cycle(int device, int pwm, int duty_cycle);
        """)
        self.lib = self.ffi.dlopen("/usr/local/lib/libpwmio.so")

    def open(self, device, pwm):
        """Open PWM device and return bytes written or error if < 0.
        Set the polarity to active HIGH "normal" or active LOW "inversed" must
        be done before enabled.
        """
        rc = self.lib.pwm_open_device(device)
        if rc < 0:
            raise RuntimeError("Error %d opening device %d" % (rc, device))
        return rc

    def close(self, device):
        """Close PWM device.
        """
        rc = self.lib.pwm_close_device(device)
        if rc < 0:
            raise RuntimeError("Error %d closing device %d" % (rc, device))
        
