package com.codeferm.demo;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import com.codeferm.I2c;

import peripheryi2c.i2c_handle;

/**
 * Triple Axis Accelerometer & Gyro - MPU-6050 sensor example.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith See LICENSE.md for details.
 */

public class Mpu6050 {

	/**
	 * Reads the temperature from the on board temperature sensor of the MPU-6050.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @return Temperature in degrees Fahrenheit.
	 */
	public double getTemp(final I2c i2c, final i2c_handle handle, final short addr) {
		return 1.8 * ((i2c.readWord(handle, addr, (short) 0x41) / 340) + 36.53) + 32;
	}

	/**
	 * Sets the range of the accelerometer to range. Using a pre-defined range is
	 * advised.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param range
	 *            The range to set the accelerometer to.
	 */
	public void setAccelRange(final I2c i2c, final i2c_handle handle, final short addr, final short range) {
		// First change it to 0x00 to make sure we write the correct value later
		i2c.writeReg(handle, addr, (short) 0x1c, (short) 0x00);
		// Write the new range to the 0x1c register
		i2c.writeReg(handle, addr, (short) 0x1c, range);
	}

	/**
	 * Reads the range the accelerometer is set to. If raw is true, it will return
	 * the raw value from the 0x1c register. If raw is false, it will return an
	 * integer: -1, 2, 4, 8 or 16. When it returns -1 something went wrong.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param raw
	 *            True to return raw data.
	 */
	public short readAccelRange(final I2c i2c, final i2c_handle handle, final short addr, final boolean raw) {
		// Get the raw value
		final short rawData = i2c.readReg(handle, addr, (short) 0x1c);
		if (raw) {
			return rawData;
		} else {
			switch (rawData) {
			case 0x00:
				return 2;
			case 0x08:
				return 4;
			case 0x10:
				return 8;
			case 0x18:
				return 16;
			default:
				return -1;
			}
		}
	}

	/**
	 * Gets and returns the X, Y and Z values from the accelerometer. If g is true,
	 * it will return the data in g. If g is False, it will return the data in
	 * m/s^2. Returns a Map with the measurement results.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param g
	 *            True to return Gs.
	 * @return Map of values.
	 */
	public Map<String, Double> getAccelData(final I2c i2c, final i2c_handle handle, final short addr, final boolean g) {
		// Read the data from the MPU-6050
		int x = i2c.readWord(handle, addr, (short) 0x3b);
		int y = i2c.readWord(handle, addr, (short) 0x3d);
		int z = i2c.readWord(handle, addr, (short) 0x3f);
		final short accelRange = readAccelRange(i2c, handle, addr, true);
		double accelScaleModifier = 0;
		switch (accelRange) {
		case 0x00:
			accelScaleModifier = 16384.0;
			break;
		case 0x08:
			accelScaleModifier = 8192.0;
			break;
		case 0x10:
			accelScaleModifier = 4096.0;
			break;
		case 0x18:
			accelScaleModifier = 2048.0;
			break;
		default:
			System.out.println("Unkown range - accelScaleModifier set to 16384");
			accelScaleModifier = 16384;
		}
		double xd = x / accelScaleModifier;
		double yd = y / accelScaleModifier;
		double zd = z / accelScaleModifier;
		Map<String, Double> map = new HashMap<>();
		if (!g) {
			xd = xd * 9.80665;
			yd = yd * 9.80665;
			zd = zd * 9.80665;
		}
		map.put("x", xd);
		map.put("y", yd);
		map.put("z", zd);
		return map;
	}

	/**
	 * Sets the range of the gyroscope to range. Using a pre-defined range is
	 * advised.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param range
	 *            The range to set the gyroscope to.
	 */
	public void setGyroRange(final I2c i2c, final i2c_handle handle, final short addr, final short range) {
		// First change it to 0x00 to make sure we write the correct value later
		i2c.writeReg(handle, addr, (short) 0x1b, (short) 0x00);
		// Write the new range to the 0x1B register
		i2c.writeReg(handle, addr, (short) 0x1b, range);
	}

	/**
	 * Reads the range the gyroscope is set to. If raw is true, it will return the
	 * raw value from the 0x1b register. If raw is false, it will return 250, 500,
	 * 1000, 2000 or -1. If the returned value is equal to -1 something went wrong.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param raw
	 *            True to return raw data.
	 * @return
	 */
	public short readGyroRange(final I2c i2c, final i2c_handle handle, final short addr, final boolean raw) {
		// Get the raw value
		final short rawData = i2c.readReg(handle, addr, (short) 0x1b);
		if (raw) {
			return rawData;
		} else {
			switch (rawData) {
			case 0x00:
				return 250;
			case 0x08:
				return 500;
			case 0x10:
				return 1000;
			case 0x18:
				return 2000;
			default:
				return -1;
			}
		}
	}

	/**
	 * Gets and returns the X, Y and Z values from the gyroscope.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @return Map of values.
	 */
	public Map<String, Double> getGyroData(final I2c i2c, final i2c_handle handle, final short addr) {
		// Read the data from the MPU-6050
		int x = i2c.readWord(handle, addr, (short) 0x43);
		int y = i2c.readWord(handle, addr, (short) 0x45);
		int z = i2c.readWord(handle, addr, (short) 0x47);
		final short accelRange = readAccelRange(i2c, handle, addr, true);
		double gyroScaleModifier = 0;
		switch (accelRange) {
		case 0x00:
			gyroScaleModifier = 131.0;
			break;
		case 0x08:
			gyroScaleModifier = 65.5;
			break;
		case 0x10:
			gyroScaleModifier = 32.8;
			break;
		case 0x18:
			gyroScaleModifier = 16.4;
			break;
		default:
			System.out.println("Unkown range - gyroScaleModifier set to 131.0");
			gyroScaleModifier = 131.0;
		}
		double xd = x / gyroScaleModifier;
		double yd = y / gyroScaleModifier;
		double zd = z / gyroScaleModifier;
		Map<String, Double> map = new HashMap<>();
		map.put("x", xd);
		map.put("y", yd);
		map.put("z", zd);
		return map;
	}

	public static void main(String args[]) throws InterruptedException {
		final I2c i2c = new I2c();
		String device = "/dev/i2c-0";
		short address = 0x68; // 0x68
		// See if there are args to parse
		if (args.length > 0) {
			// I2C device name (default '/dev/i2c-0')
			device = args[0];
			// MPU-6050 address (default 0x68)
			address = (short) Integer.parseInt(args[1], 16);
		}
		// Use to debug if JNA cannot find shared library
		System.setProperty("jna.debug_load", "false");
		System.setProperty("jna.debug_load.jna", "false");
		final i2c_handle handle = i2c.open(device);
		final Mpu6050 app = new Mpu6050();
		// Wake up the MPU-6050 since it starts in sleep mode
		i2c.writeReg(handle, address, (short) 0x6b, (short) 0x00);
		for (int i = 0; i < 100; i++) {
			final double temp = app.getTemp(i2c, handle, address);
			final Map<String, Double> accel = app.getAccelData(i2c, handle, address, false);
			final Map<String, Double> gyro = app.getGyroData(i2c, handle, address);
			System.out.println(String.format("%2.1f ºF | Accel x: %+5.2f, y: %+5.2f, z: %+5.2f | Gyro  x: %+5.2f, y: %+5.2f, z: %+5.2f", temp,
					accel.get("x"), accel.get("y"), accel.get("z"), gyro.get("x"), gyro.get("y"), gyro.get("z")));
			TimeUnit.MILLISECONDS.sleep(500);
		}
		i2c.close(handle);
	}
}
