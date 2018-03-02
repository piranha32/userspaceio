# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
libperipheryspi CFFI interface for SPI access
-------------

Helper methods added to handle repetitive operations.
"""

from cffi import FFI


class libperipheryspi:

    def __init__(self):
        self.ffi = FFI()
        # Specify each C function, struct and constant you want a Python binding for
        # Copy-n-paste with minor edits
        self.ffi.cdef("""
        #define SPI_MODE_0 0x00
        #define SPI_MODE_1 0x01
        #define SPI_MODE_2 0x02
        #define SPI_MODE_3 0x03
        
        enum spi_error_code {
            SPI_ERROR_ARG           = -1,
            SPI_ERROR_OPEN          = -2,
            SPI_ERROR_QUERY         = -3,
            SPI_ERROR_CONFIGURE     = -4,
            SPI_ERROR_TRANSFER      = -5,
            SPI_ERROR_CLOSE         = -6,
        };
        
        typedef struct spi_handle {
            int fd;
        
            struct {
                int c_errno;
                char errmsg[96];
            } error;
        } spi_t;
        
        typedef enum spi_bit_order {
            MSB_FIRST,
            LSB_FIRST,
        } spi_bit_order_t;
        
        int spi_open(spi_t *spi, const char *path, unsigned int mode,
                        uint32_t max_speed);
                        
        int spi_open_advanced(spi_t *spi, const char *path, unsigned int mode,
                                uint32_t max_speed, spi_bit_order_t bit_order,
                                uint8_t bits_per_word, uint8_t extra_flags);
                                
        int spi_transfer(spi_t *spi, const uint8_t *txbuf, uint8_t *rxbuf, size_t len);
        
        int spi_close(spi_t *spi);
        
        int spi_get_mode(spi_t *spi, unsigned int *mode);
        
        int spi_get_max_speed(spi_t *spi, uint32_t *max_speed);
        
        int spi_get_bit_order(spi_t *spi, spi_bit_order_t *bit_order);
        
        int spi_get_bits_per_word(spi_t *spi, uint8_t *bits_per_word);
        
        int spi_get_extra_flags(spi_t *spi, uint8_t *extra_flags);
        
        int spi_set_mode(spi_t *spi, unsigned int mode);
        
        int spi_set_max_speed(spi_t *spi, uint32_t max_speed);
        
        int spi_set_bit_order(spi_t *spi, spi_bit_order_t bit_order);
        
        int spi_set_bits_per_word(spi_t *spi, uint8_t bits_per_word);
        
        int spi_set_extra_flags(spi_t *spi, uint8_t extra_flags);
        
        int spi_fd(spi_t *spi);
        
        int spi_tostring(spi_t *spi, char *str, size_t len);
        
        int spi_errno(spi_t *spi);
        
        const char *spi_errmsg(spi_t *spi);
        """)
        self.lib = self.ffi.dlopen("/usr/local/lib/libperipheryspi.so")
        
    def open(self, device, mode, maxSpeed):
        """Open SPI device and return handle.
        """
        handle = self.ffi.new("spi_t*")
        if self.lib.spi_open(handle, device.encode('utf-8'), mode, maxSpeed) < 0:
            raise RuntimeError(self.ffi.string(self.lib.spi_errmsg(handle)).decode('utf-8'))
        return handle

    def close(self, handle):
        """Close SPI device.
        """
        if self.lib.spi_close(handle) < 0:
            raise RuntimeError(self.ffi.string(self.lib.spi_errmsg(handle)).decode('utf-8'))
        return handle        

    def transfer(self, handle, txbuf, rxbuf):
        """Transfer byte array.
        """
        # Get buffer length
        if txbuf != self.ffi.NULL:
            bufLen = len(txbuf)
        elif rxbuf != self.ffi.NULL:
            bufLen = len(rxbuf)
        else:
            raise RuntimeError("tx and rx buffer cannot both be null".decode('utf-8'))
        if self.lib.spi_transfer(handle, txbuf, rxbuf, bufLen) < 0:
            raise RuntimeError(self.ffi.string(self.lib.spi_errmsg(handle)).decode('utf-8'))
        return rxbuf       
