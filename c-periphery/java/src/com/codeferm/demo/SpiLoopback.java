package com.codeferm.demo;

import java.nio.ByteBuffer;

import com.codeferm.Spi;

import peripheryserial.PeripheryserialLibrary;
import peripheryspi.spi_handle;

/**
 * SPI loop back test.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith See LICENSE.md for details.
 */

public class SpiLoopback {

	public static void main(String args[]) {
		final Spi spi = new Spi();
		String device = "/dev/spidev1.0";
		int maxSpeed = 500000;
		// See if there are args to parse
		if (args.length > 0) {
			// SPI device name (default '/dev/i2c-0')
			device = args[0];
			// SPI maximum speed (default 500000)
			maxSpeed = Integer.parseInt(args[1]);
		}
		// Use to debug if JNA cannot find shared library
		System.setProperty("jna.debug_load", "false");
		System.setProperty("jna.debug_load.jna", "false");
		final spi_handle handle = spi.open(device, PeripheryserialLibrary.SPI_MODE_0, maxSpeed);
		final byte[] txBuf = new byte[128];
		txBuf[0] = (byte) 0xff;
		txBuf[127] = (byte) 0x80;
		final ByteBuffer rxBuf = ByteBuffer.allocate(128);
		spi.transfer(handle, txBuf, rxBuf);
		System.out.println(String.format("%02X, %02X", (short) rxBuf.get(0) & 0xff, (short) rxBuf.get(127) & 0xff));
		spi.close(handle);
	}
}
