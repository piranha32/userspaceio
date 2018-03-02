package com.codeferm.demo;

import java.nio.ByteBuffer;

import com.codeferm.Serial;
import com.ochafik.lang.jnaerator.runtime.NativeSize;

import peripheryserial.serial_handle;

/**
 * Serial loop back test.
 *
 * Send C byte array to serial device and read back results.
 * 
 * Install socat:
 * 
 * sudo apt-get install socat
 * 
 * Run in another terminal:
 * 
 * sudo socat PTY,link=/dev/ttyS10 PTY,link=/dev/ttyS11
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class SerialTest {

	public static void main(String args[]) {
		final Serial serial = new Serial();
		String device = "/dev/ttyS10";
		int baudRate = 115200;
		// See if there are args to parse
		if (args.length > 0) {
			// Serial device name (default '/dev/ttyS11')
			device = args[0];
			// SPI maximum speed (default 115200)
			baudRate = Integer.parseInt(args[1]);
		}
		// Use to debug if JNA cannot find shared library
		System.setProperty("jna.debug_load", "false");
		System.setProperty("jna.debug_load.jna", "false");
		final serial_handle handle = serial.open(device, baudRate);
		final byte[] txBuf = new byte[128];
		txBuf[0] = (byte) 0xff;
		txBuf[127] = (byte) 0x80;
		int rc = serial.getLib().serial_write(handle, txBuf, new NativeSize(txBuf.length));
		final ByteBuffer rxBuf = ByteBuffer.allocate(txBuf.length);
		System.out.println(rxBuf.capacity());
		serial.getLib().serial_read(handle, rxBuf, new NativeSize(rxBuf.capacity()), 2000);
		System.out.println(String.format("%02X, %02X", (short) rxBuf.get(0) & 0xff, (short) rxBuf.get(127) & 0xff));
		serial.close(handle);
	}
}
