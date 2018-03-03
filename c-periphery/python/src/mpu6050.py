# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Triple Axis Accelerometer & Gyro - MPU-6050 sensor example
-------------
This is an example of using the c-periphery I2C bindings.
"""

import sys, time
from argparse import *
from cffi import FFI
from libperiphery import libperipheryi2c


class mpu6050:
    
    def __init__(self):
        """Create library interface.
        """    
        self.i2c = libperipheryi2c.libperipheryi2c()

    def getTemp(self, handle, addr):
        """Reads the temperature from the onboard temperature sensor of the
        MPU-6050.
        
        Returns the temperature in degrees Fahrenheit.
        """    
        # Get the actual temperature using the formula given in the MPU-6050
        # Register Map and Descriptions revision 4.2, page 30 and convert to
        # ºF
        return 1.8 * ((self.i2c.readWord(handle, addr, 0x41) / 340) + 36.53) + 32
    
    def setAccelRange(self, handle, addr, range):
        """Sets the range of the accelerometer to range.
        
        accel_range -- the range to set the accelerometer to. Using a pre-defined
        range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.i2c.writeReg(handle, addr, 0x1c, 0x00)
        # Write the new range to the 0x1c register
        self.i2c.writeReg(handle, addr, 0x1c, range)
        
    def readAccelRange(self, handle, addr, raw=False):
        """Reads the range the accelerometer is set to.
        
        If raw is True, it will return the raw value from the 0x1c register. If raw
        is False, it will return an integer: -1, 2, 4, 8 or 16. When it returns -1
        something went wrong.
        """
        # Get the raw value
        rawData = self.i2c.readReg(handle, addr, 0x1c)
        if raw is True:
            return rawData
        elif raw is False:
            if rawData == 0x00:
                return 2
            elif rawData == 0x08:
                return 4
            elif rawData == 0x10:
                return 8
            elif rawData == 0x18:
                return 16
            else:
                return -1
    
    def getAccelData(self, handle, addr, g=False):
        """Gets and returns the X, Y and Z values from the accelerometer.
            
        If g is True, it will return the data in g. If g is False, it will return
        the data in m/s^2. Returns a dictionary with the measurement results.
        """
        # Read the data from the MPU-6050
        x = self.i2c.readWord(handle, addr, 0x3b) 
        y = self.i2c.readWord(handle, addr, 0x3d)
        z = self.i2c.readWord(handle, addr, 0x3f)
        accelScaleModifier = None
        accelRange = self.readAccelRange(handle, addr, True)
        if accelRange == 0x00:
            accelScaleModifier = 16384.0
        elif accelRange == 0x08:
            accelScaleModifier = 8192.0
        elif accelRange == 0x10:
            accelScaleModifier = 4096.0
        elif accelRange == 0x18:
            accelScaleModifier = 2048.0
        else:
            print("Unkown range - accelScaleModifier set to 16384.0")
            accelScaleModifier = 16384.0
        x = x / accelScaleModifier
        y = y / accelScaleModifier
        z = z / accelScaleModifier
        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * 9.80665
            y = y * 9.80665
            z = z * 9.80665
        return {'x': x, 'y': y, 'z': z}
    
    def setGyroRange(self, handle, addr, gyroRange):
        """Sets the range of the gyroscope to range.
        
        gyroRange -- the range to set the gyroscope to. Using a pre-defined range
        is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.i2c.writeReg(handle, addr, 0x1b, 0x00)
        # Write the new range to the 0x1B register
        self.i2c.writeReg(handle, addr, 0x1b, gyroRange)
    
    def readGyroRange(self, handle, addr, raw=False):
        """Reads the range the gyroscope is set to.
        
        If raw is True, it will return the raw value from the 0x1b register. If raw
        is False, it will return 250, 500, 1000, 2000 or -1. If the returned value
        is equal to -1 something went wrong.
        """
        # Get the raw value
        rawData = self.i2c.readReg(handle, addr, 0x1b)
        if raw is True:
            return rawData
        elif raw is False:
            if rawData == 0x00:
                return 250
            elif rawData == 0x08:
                return 500
            elif rawData == 0x10:
                return 1000
            elif rawData == 0x18:
                return 2000
            else:
                return -1
    
    def getGyroData(self, handle, addr):
        """Gets and returns the X, Y and Z values from the gyroscope.
        
        Returns the read values in a dictionary.
        """
        # Read the raw data from the MPU-6050
        x = self.i2c.readWord(handle, addr, 0x43)
        y = self.i2c.readWord(handle, addr, 0x45)
        z = self.i2c.readWord(handle, addr, 0x47)
        gyroScaleModifier = None
        gyroRange = self.readGyroRange(handle, addr, True)
        if gyroRange == 0x00:
            gyroScaleModifier = 131.0
        elif gyroRange == 0x08:
            gyroScaleModifier = 65.5
        elif gyroRange == 0x10:
            gyroScaleModifier = 32.8
        elif gyroRange == 0x18:
            gyroScaleModifier = 16.4
        else:
            print("Unkown range - gyroScaleModifier set to 131.0")
            gyroScaleModifier = 131.0
        x = x / gyroScaleModifier
        y = y / gyroScaleModifier
        z = z / gyroScaleModifier
        return {'x': x, 'y': y, 'z': z}
    
    def getAllData(self, handle, addr):
        """Reads and returns all the available data.
        """
        temp = self.getTemp(handle, addr)
        accel = self.getAccelData(handle, addr)
        gyro = self.getGyroData(handle, addr)
        return [accel, gyro, temp]

    def main(self, device, address):
        handle = self.i2c.open(device)
        # Wake up the MPU-6050 since it starts in sleep mode
        self.i2c.writeReg(handle, address, 0x6b, 0x00)
        count = 0
        while count < 100:
            all = self.getAllData(handle, address)
            accel = all[0]
            gyro = all[1]
            temp = all[2]
            print("%.1f ºF | Accel x: %+5.2f, y: %+5.2f, z: %+5.2f | Gyro  x: %+5.2f, y: %+5.2f, z: %+5.2f" % (temp, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']))
            time.sleep(0.5)
            count += 1
        self.i2c.close(handle)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", help="I2C device name (default '/dev/i2c-0')", type=str, default="/dev/i2c-0")
    parser.add_argument("--address", help="MPU-6050 address (default 0x68)", type=str, default="0x68")
    args = parser.parse_args()
    obj = mpu6050()
    # Convert from hex string to int
    address = int(args.address, 16)
    obj.main(args.device, address)

