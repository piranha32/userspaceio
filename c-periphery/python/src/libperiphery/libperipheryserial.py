# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
libperipheryserial CFFI interface for I2C access
-------------

Helper methods added to handle repetitive operations.
"""

from cffi import FFI


class libperipheryserial:

    def __init__(self):
        self.ffi = FFI()
        # Specify each C function, struct and constant you want a Python binding for
        # Copy-n-paste with minor edits
        self.ffi.cdef("""
        enum serial_error_code {
            SERIAL_ERROR_ARG            = -1,
            SERIAL_ERROR_OPEN           = -2,
            SERIAL_ERROR_QUERY          = -3,
            SERIAL_ERROR_IO             = -5,
            SERIAL_ERROR_CONFIGURE      = -6,
            SERIAL_ERROR_CLOSE          = -7,
        };
        
        typedef struct serial_handle {
            int fd;
        
            struct {
                int c_errno;
                char errmsg[96];
            } error;
        } serial_t;
        
        typedef enum serial_parity {
            PARITY_NONE,
            PARITY_ODD,
            PARITY_EVEN,
        } serial_parity_t;
        
        int serial_open(serial_t *serial, const char *path, uint32_t baudrate);

        int serial_open_advanced(serial_t *serial, const char *path,
                                    uint32_t baudrate, unsigned int databits,
                                    serial_parity_t parity, unsigned int stopbits,
                                    bool xonxoff, bool rtscts);
                                    
        int serial_read(serial_t *serial, uint8_t *buf, size_t len, int timeout_ms);
        
        int serial_write(serial_t *serial, const uint8_t *buf, size_t len);
        
        int serial_flush(serial_t *serial);
        
        int serial_input_waiting(serial_t *serial, unsigned int *count);
        
        int serial_output_waiting(serial_t *serial, unsigned int *count);
        
        int serial_poll(serial_t *serial, int timeout_ms);
        
        int serial_close(serial_t *serial);
        
        int serial_get_baudrate(serial_t *serial, uint32_t *baudrate);
        
        int serial_get_databits(serial_t *serial, unsigned int *databits);
        
        int serial_get_parity(serial_t *serial, serial_parity_t *parity);
        
        int serial_get_stopbits(serial_t *serial, unsigned int *stopbits);
        
        int serial_get_xonxoff(serial_t *serial, bool *xonxoff);
        
        int serial_get_rtscts(serial_t *serial, bool *rtscts);
        
        int serial_set_baudrate(serial_t *serial, uint32_t baudrate);
        
        int serial_set_databits(serial_t *serial, unsigned int databits);
        
        int serial_set_parity(serial_t *serial, enum serial_parity parity);
        
        int serial_set_stopbits(serial_t *serial, unsigned int stopbits);
        
        int serial_set_xonxoff(serial_t *serial, bool enabled);
        
        int serial_set_rtscts(serial_t *serial, bool enabled);
        
        int serial_fd(serial_t *serial);
        
        int serial_tostring(serial_t *serial, char *str, size_t len);
        
        int serial_errno(serial_t *serial);
        
        const char *serial_errmsg(serial_t *serial);
        """)
        self.lib = self.ffi.dlopen("/usr/local/lib/libperipheryserial.so")

    def open(self, device, baudrate):
        """Open serial device and return handle.
        """
        handle = self.ffi.new("serial_t*")
        if self.lib.serial_open(handle, device.encode('utf-8'), baudrate) < 0:
            raise RuntimeError(self.ffi.string(self.lib.serial_errmsg(handle)).decode('utf-8'))
        return handle

    def close(self, handle):
        """Close serial device.
        """
        if self.lib.serial_close(handle) < 0:
            raise RuntimeError(self.ffi.string(self.lib.serial_errmsg(handle)).decode('utf-8'))
        return handle
