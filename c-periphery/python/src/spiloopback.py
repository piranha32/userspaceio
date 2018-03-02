# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
SPI loop back test 
-------------

Send C byte array to SPI and read back results.
"""

from argparse import *
from cffi import FFI
from libperiphery import libperipheryspi


class spiloopback:
    
    def __init__(self):
        """Create library and ffi interfaces.
        """         
        self.spi = libperipheryspi.libperipheryspi()
        self.lib = self.spi.lib
        self.ffi = self.spi.ffi
        
    def main(self, device, maxSpeed):
        """Rx and tx 128 byte array.
        
        Note that structure is zero filled, so we only change a couple bytes.
        """         
        handle = self.spi.open(device, self.lib.SPI_MODE_0, maxSpeed)
        txbuf = self.ffi.new("uint8_t[]", 128)
        txbuf[0] = 0xff
        txbuf[127] = 0x80
        rxbuf = self.ffi.new("uint8_t[]", 128)
        self.spi.transfer(handle, txbuf, rxbuf)
        print(rxbuf[0], rxbuf[127])
        self.spi.close(handle)

        
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", help="SPI device name (default '/dev/spidev1.0')", type=str, default="/dev/spidev1.0")
    parser.add_argument("--maxSpeed", help="SPI maximum speed (default 500000)", type=int, default=500000)
    args = parser.parse_args()    
    obj = spiloopback()
    obj.main(args.device, args.maxSpeed)
