# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
libperipheryi2c CFFI interface for I2C access
-------------

Helper methods added to handle repetitive operations.
"""

from cffi import FFI


class libperipheryi2c:

    def __init__(self):
        self.ffi = FFI()
        # Specify each C function, struct and constant you want a Python binding for
        # Copy-n-paste with minor edits
        self.ffi.cdef("""
        typedef unsigned char uint8_t;
        typedef unsigned short int uint16_t;
        
        struct i2c_msg {
            uint16_t addr;
            uint16_t flags;
        #define I2C_M_TEN          0x0010
        #define I2C_M_RD           0x0001
        #define I2C_M_STOP         0x8000
        #define I2C_M_NOSTART      0x4000
        #define I2C_M_REV_DIR_ADDR 0x2000
        #define I2C_M_IGNORE_NAK   0x1000
        #define I2C_M_NO_RD_ACK    0x0800
        #define I2C_M_RECV_LEN     0x0400
            uint16_t len;
            uint8_t *buf;
        };        
        
        enum i2c_error_code {
            I2C_ERROR_ARG               = -1,
            I2C_ERROR_OPEN              = -2,
            I2C_ERROR_QUERY_SUPPORT     = -3,
            I2C_ERROR_NOT_SUPPORTED     = -4,
            I2C_ERROR_TRANSFER          = -5,
            I2C_ERROR_CLOSE             = -6,
        };
        
        typedef struct i2c_handle {
            int fd;
        
            struct {
                int c_errno;
                char errmsg[96];
            } error;
        } i2c_t;
        
        int i2c_open(i2c_t *i2c, const char *path);
        
        int i2c_transfer(i2c_t *i2c, struct i2c_msg *msgs, size_t count);
        
        int i2c_close(i2c_t *i2c);
        
        int i2c_fd(i2c_t *i2c);
        
        int i2c_tostring(i2c_t *i2c, char *str, size_t len);
        
        int i2c_errno(i2c_t *i2c);

        const char *i2c_errmsg(i2c_t *i2c);
        """)
        self.lib = self.ffi.dlopen("/usr/local/lib/libperipheryi2c.so")

    def open(self, device):
        """Open I2C device and return handle.
        """
        handle = self.ffi.new("i2c_t*")
        if self.lib.i2c_open(handle, device.encode('utf-8')) < 0:
            raise RuntimeError(self.ffi.string(self.lib.i2c_errmsg(handle)).decode('utf-8'))
        return handle

    def close(self, handle):
        """Close I2C device.
        """
        if self.lib.i2c_close(handle) < 0:
            raise RuntimeError(self.ffi.string(self.lib.i2c_errmsg(handle)).decode('utf-8'))
        
    def writeReg(self, handle, addr, reg, value):
        """Write value to i2c register.
        """
        # Build message
        msg = self.ffi.new("uint8_t[]", 2)
        msg[0] = reg
        msg[1] = value
        # Build message array
        msgs = self.ffi.new("struct i2c_msg[]", 1)
        msgs[0].addr = addr
        msgs[0].flags = 0x00
        msgs[0].len = 2
        msgs[0].buf = msg            
        # Transfer a transaction with one I2C message
        if self.lib.i2c_transfer(handle, msgs, 1) < 0:
            raise RuntimeError(self.ffi.string(self.lib.i2c_errmsg(handle)).decode('utf-8'))
        
    def readReg(self, handle, addr, reg):
        """Read i2c register.
        
        In order to read a register, we first do a "dummy write" by writing 0 bytes
        to the register we want to read from. This is similar to writing to a
        register except it's 1 byte rather than 2.
        """
        # Register to read
        msg1 = self.ffi.new("uint8_t[]", 1)
        msg1[0] = reg
        # Set buffer to 0 that data will be read into
        msg2 = self.ffi.new("uint8_t[]", 1)
        msg2[0] = 0x00
        # Build message array
        msgs = self.ffi.new("struct i2c_msg[]", 2)
        # Build write message element 
        msgs[0].addr = addr
        msgs[0].flags = 0x00
        msgs[0].len = 1
        msgs[0].buf = msg1
        # Build read message element
        msgs[1].addr = addr
        msgs[1].flags = self.lib.I2C_M_RD
        msgs[1].len = 1
        msgs[1].buf = msg2            
        # Transfer a transaction with two I2C messages
        if self.lib.i2c_transfer(handle, msgs, 2) < 0:
            raise RuntimeError(self.ffi.string(self.lib.i2c_errmsg(handle)).decode('utf-8'))
        return msg2[0]
    
    def readWord(self, handle, addr, reg):
        """Read two i2c registers and combine them.
        """
        high = self.readReg(handle, addr, reg)
        # Increment register for next read
        low = self.readReg(handle, addr, reg + 1)
        value = (high << 8) + low
        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value        

    def readArray(self, handle, addr, reg, len):
        """Read array from i2c register.
        
        In order to read a register, we first do a "dummy write" by writing 0 bytes
        to the register we want to read from. This is similar to writing to a
        register except it's 1 byte rather than 2.
        """
        # Register to read
        msg1 = self.ffi.new("uint8_t[]", 1)
        msg1[0] = reg
        # Set buffer to 0 that data will be read into
        msg2 = self.ffi.new("uint8_t[]", len)
        # Build message array
        msgs = self.ffi.new("struct i2c_msg[]", 2)
        # Build write message element 
        msgs[0].addr = addr
        msgs[0].flags = 0x00
        msgs[0].len = 1
        msgs[0].buf = msg1
        # Build read message element
        msgs[1].addr = addr
        msgs[1].flags = self.lib.I2C_M_RD
        msgs[1].len = len
        msgs[1].buf = msg2            
        # Transfer a transaction with two I2C messages
        if self.lib.i2c_transfer(handle, msgs, 2) < 0:
            raise RuntimeError(self.ffi.string(self.lib.i2c_errmsg(handle)).decode('utf-8'))
        return msg2
