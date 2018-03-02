package com.codeferm;

import peripheryserial.PeripheryserialLibrary;
import peripheryserial.serial_handle;

/**
 * Serial class to handle repetitive operations.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class Serial {

	// Load JNA library
	final PeripheryserialLibrary lib = PeripheryserialLibrary.INSTANCE;

	/**
	 * Get JNA library.
	 * 
	 * @return Library instance.
	 */
	public PeripheryserialLibrary getLib() {
		return lib;
	}

	/**
	 * Open Serial device and return handle.
	 * 
	 * @param device
	 *            Device path.
	 * @param baudRate
	 *            Buad rate.
	 * @return File handle.
	 */
	public serial_handle open(final String device, final int baudRate) {
		final serial_handle handle = new serial_handle();
		if (lib.serial_open(handle, device, baudRate) < 0) {
			throw new RuntimeException(lib.serial_errmsg(handle));
		}
		return handle;
	}

	/**
	 * Close device.
	 * 
	 * @param handle
	 *            Serial file handle.
	 */
	public void close(final serial_handle handle) {
		if (lib.serial_close(handle) < 0) {
			throw new RuntimeException(lib.serial_errmsg(handle));
		}
	}
}
