package com.codeferm;

import java.nio.ByteBuffer;

import com.ochafik.lang.jnaerator.runtime.NativeSize;

import peripheryspi.PeripheryspiLibrary;
import peripheryspi.spi_handle;

/**
 * SPI class to handle repetitive operations.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class Spi {

	// Load JNA library
	final PeripheryspiLibrary lib = PeripheryspiLibrary.INSTANCE;

	/**
	 * Get JNA library.
	 * 
	 * @return Library instance.
	 */
	public PeripheryspiLibrary getLib() {
		return lib;
	}

	/**
	 * Open SPI device and return handle.
	 * 
	 * @param device
	 *            Device path.
	 * @param mode
	 *            SPI mode.
	 * @param maxSpeed
	 *            Maximum speed.
	 * @return File handle.
	 */
	public spi_handle open(final String device, final int mode, final int maxSpeed) {
		final spi_handle handle = new spi_handle();
		if (lib.spi_open(handle, device, mode, maxSpeed) < 0) {
			throw new RuntimeException(lib.spi_errmsg(handle));
		}
		return handle;
	}

	/**
	 * Close device.
	 * 
	 * @param handle
	 *            SPI file handle.
	 */
	public void close(final spi_handle handle) {
		if (lib.spi_close(handle) < 0) {
			throw new RuntimeException(lib.spi_errmsg(handle));
		}
	}

	/**
	 * Transfer byte array.
	 * 
	 * @param device
	 *            Device path.
	 * @param txBuf
	 *            Transfer buffer.
	 * @param rxBuf
	 *            Receive buffer.
	 * @return Receive buffer.
	 */
	public ByteBuffer transfer(final spi_handle handle, final byte[] txBuf, final ByteBuffer rxBuf) {
		int len = 0;
		if (txBuf != null) {
			len = txBuf.length;
		} else if (rxBuf != null) {
			len = rxBuf.capacity();
		} else {
			throw new RuntimeException("tx and rx buffer cannot both be null");
		}
		lib.spi_transfer(handle, txBuf, rxBuf, new NativeSize(len));
		return rxBuf;
	}
}
