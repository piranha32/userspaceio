# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
ADXL345 3-Axis, ±2 g/±4 g/±8 g/±16 g digital accelerometer 
-------------
I'm using I2C to communicate with the ADXL345 although SPI is supported as
well.
"""

import sys, time
from argparse import *
from cffi import FFI
from libperiphery import libperipheryi2c

class adxl345:
    
    def __init__(self):
        """Create library interface.
        """    
        self.i2c = libperipheryi2c.libperipheryi2c()
            
    def getRange(self, handle, addr):
        """Retrieve the current range of the accelerometer. See setRange for
        the possible range constant values that will be returned.
        """
        return self.i2c.readReg(handle, addr, 0x31) & 0x03


    def setRange(self, handle, addr, value):
        """Set the range of the accelerometer to the provided value. Read the data
        format register to preserve bits. Update the data rate, make sure that the
        FULL-RES bit is enabled for range scaling.
        """
        regVal = self.i2c.readReg(handle, addr, 0x31) & ~0x0f
        regVal |= value
        regVal |= 0x08  # FULL-RES bit enabled
        # Write the updated format register
        self.i2c.writeReg(handle, addr, 0x31, regVal)
    
    def setDataRate(self, handle, addr, rate):
        """Set the data rate of the accelerometer. Note: The LOW_POWER bits are
        currently ignored, we always keep the device in 'normal' mode.
        """
        self.i2c.writeReg(handle, addr, 0x2c, rate & 0x0f)
    
       
    def getDataRate(self, handle, addr):
        """Retrieve the current data rate.
        """
        return self.i2c.readReg(handle, addr, 0x2c) & 0x0f
    
    
    def read(self, handle, addr):
        """Retrieve the current data rate. X-axis data 0 (6 bytes for X/Y/Z).
        """
        self.i2c.readArray(handle, addr, reg, len)
        retVal = "012345"
        AIOReadI2C(handle, 0x32, retVal, len(retVal))
        # Convert string to tuple of 16 bit integers x, y, z
        x = ord(retVal[0]) | (ord(retVal[1]) << 8)
        if(x & (1 << 16 - 1)):
            x = x - (1 << 16)
        y = ord(retVal[2]) | (ord(retVal[3]) << 8)
        if(y & (1 << 16 - 1)):
            y = y - (1 << 16)
        z = ord(retVal[4]) | (ord(retVal[5]) << 8)
        if(z & (1 << 16 - 1)):
            z = z - (1 << 16)    
        return (x, y, z)

    def main(self, device, address):
        handle = self.i2c.open(device)
        # ADXL345 wired up on port 0x53?
        if self.i2c.readReg(handle, address, 0x00) == 0xE5:
            # Enable the accelerometer
            self.i2c.writeReg(handle, address, 0x2d, 0x08)
            # +/- 2g
            self.setRange(handle, address, 0x00)
            # 100 Hz
            self.setDataRate(handle, address, 0x0a)
            print("Range = %d, data rate = %d" % (self.getRange(handle, addr), self.getDataRate(handle, addr)))
            count = 0
            while count < 100:
                data = self.read(handle, address)
                print("x: %04d, y: %04d, z: %04d" % (data[0], data[1], data[2]))
                time.sleep(0.5)
                count += 1
        else:
            print("Not ADXL345?")
        self.i2c.close(handle)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", help="I2C device name (default '/dev/i2c-0')", type=str, default="/dev/i2c-0")
    parser.add_argument("--address", help="ADXL345 address (default 0x53)", type=str, default="0x53")
    args = parser.parse_args()
    obj = adxl345()
    # Convert from hex string to int
    address = int(args.address, 16)
    obj.main(args.device, address)
