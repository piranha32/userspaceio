# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Serial loop back test 
-------------

Send C byte array to serial device and read back results.

Install socat:

sudo apt-get install socat

Run in another terminal:

sudo socat PTY,link=/dev/ttyS10 PTY,link=/dev/ttyS11
"""

from argparse import *
from cffi import FFI
from libperiphery import libperipheryserial


class serialtest:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.serial = libperipheryserial.libperipheryserial()
        self.lib = self.serial.lib
        self.ffi = self.serial.ffi
        
    def main(self, device, baudRate):
        """Rx and tx 128 byte array.
        
        Note that structure is zero filled, so we only change a couple bytes.
        """         
        handle = self.serial.open(device, baudRate)
        txbuf = self.ffi.new("uint8_t[]", 128)
        txbuf[0] = 0xff
        txbuf[127] = 0x80
        rc = self.lib.serial_write(handle, txbuf, len(txbuf))
        print("Sent %d bytes" % rc)
        rxbuf = self.ffi.new("uint8_t[]", 128)
        self.lib.serial_read(handle, rxbuf, len(rxbuf), 2000)
        print(rxbuf[0])
        self.serial.close(handle)

        
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", help="Serial device name (default '/dev/ttyS10')", type=str, default="/dev/ttyS10")
    parser.add_argument("--baudRate", help="Baud rate (default 115200)", type=int, default=115200)
    args = parser.parse_args()    
    obj = serialtest()
    obj.main(args.device, args.baudRate)        
