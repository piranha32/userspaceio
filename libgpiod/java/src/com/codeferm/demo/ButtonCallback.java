package com.codeferm.demo;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

import com.sun.jna.NativeLong;
import com.sun.jna.Pointer;

import gpiod.GpiodLibrary;
import gpiod.timespec;

/**
 * Use libgpiod context less event loop to implement blocking callback.
 * 
 * Should work on any board with a button built in. Just change chip and line
 * value as needed.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class ButtonCallback {

	public static void main(String args[]) throws InterruptedException {
		String chipNum = "/dev/gpiochip1";
		int lineNum = 3;
		// See if there are args to parse
		if (args.length > 0) {
			// GPIO chip number (default 1 '/dev/gpiochip1')
			chipNum = args[0];
			// GPIO line number (default 3 button on NanoPi Duo)
			lineNum = Integer.parseInt(args[1]);
		}
		// Use class name for consumer
		final String consumer = ButtonCallback.class.getSimpleName();
		// Load library
		final GpiodLibrary lib = GpiodLibrary.INSTANCE;
		// Timestamp formatter
		final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/dd/yyyy HH:mm:ss");
		// Use lambda for callback
		final GpiodLibrary.gpiod_ctxless_event_handle_cb func = (int evtype, int offset, timespec timeSpec,
				Pointer data) -> {
			int rc = GpiodLibrary.GPIOD_CTXLESS_EVENT_CB_RET_ERR;
			if (evtype == GpiodLibrary.GPIOD_CTXLESS_EVENT_CB_TIMEOUT) {
				rc = GpiodLibrary.GPIOD_CTXLESS_EVENT_CB_RET_STOP;
				System.out.println("Timed out");
			} else {
				rc = GpiodLibrary.GPIOD_CTXLESS_EVENT_CB_RET_OK;
				final LocalDateTime date = LocalDateTime.ofInstant(
						Instant.ofEpochMilli(timeSpec.tv_sec.longValue() * 1000), ZoneId.systemDefault());
				if (evtype == GpiodLibrary.GPIOD_CTXLESS_EVENT_CB_RISING_EDGE) {
					System.out.println(String.format("Rising  edge timestamp %s", date.format(formatter)));
				} else {
					System.out.println(String.format("Falling edge timestamp %s", date.format(formatter)));
				}
			}
			return rc;
		};
		System.out.println("Press and release button, timeout in 10 seconds\n");
		// Blocking poll until timeout, note gpiod_simple_event_poll_cb is passed as a
		// NULL
		if (lib.gpiod_ctxless_event_loop(chipNum, lineNum, (byte) 0, consumer,
				new timespec(new NativeLong(10), new NativeLong(0)), null, func, null) != 0) {
			System.out.println("gpiod_simple_event_loop error, check chip and line values");
		}
	}
}
