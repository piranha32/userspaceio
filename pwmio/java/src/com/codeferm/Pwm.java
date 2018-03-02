package com.codeferm;

import pwmio.PwmioLibrary;

/**
 * PWM class to handle repetitive operations.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class Pwm {

	// Load JNA library
	final PwmioLibrary lib = PwmioLibrary.INSTANCE;

	/**
	 * Get JNA library.
	 * 
	 * @return Library instance.
	 */
	public PwmioLibrary getLib() {
		return lib;
	}

/**
 * Open PWM device and return bytes written or error if < 0.
 * Set the polarity to active HIGH "normal" or active LOW "inversed" must be
 * done before enabled.
 * 	
 * @param device Number after /sys/class/pwm/pwmchip.
 * @param pwm Number after /sys/class/pwm/pwmchip/pwm.
 * @return bytes written (1) or < 0 error.
 */
	public int open(final int device, final int pwm) {
		int rc = lib.pwm_open_device(device);
		if (rc < 0) {
			throw new RuntimeException(String.format("Error %d opening device %d", rc, device));
		}
		return rc;
	}

	/**
	 * Close PWM device.
	 * 
	 * @param device
	 *            PWM device.
	 */
	public void close(final int device) {
		int rc = lib.pwm_close_device(device);
		if (rc < 0) {
			throw new RuntimeException(String.format("Error %d closing device %d", rc, device));
		}
	}
}
