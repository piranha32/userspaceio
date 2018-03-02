package com.codeferm.demo;
import com.sun.jna.NativeLong;

import gpiod.GpiodLibrary;
import gpiod.gpiod_chip;
import gpiod.gpiod_line;
import gpiod.gpiod_line_event;
import gpiod.timespec;

/**
 * Test blocking event using built in button.
 * 
 * Should work on any board with a button built in. Just change chip and line
 * value as needed.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class ButtonWait {

	public static void main(String args[]) throws InterruptedException {
		int chipNum = 1;
		int lineNum = 3;
		// See if there are args to parse
		if (args.length > 0) {
			// GPIO chip number (default 1 '/dev/gpiochip1')
			chipNum = Integer.parseInt(args[0]);
			// GPIO line number (default 3 button on NanoPi Duo)
			lineNum = Integer.parseInt(args[1]);
		}
		// Use class name for consumer
		final String consumer = ButtonWait.class.getSimpleName();
		// Load library
		final GpiodLibrary lib = GpiodLibrary.INSTANCE;
		final gpiod_chip chip = lib.gpiod_chip_open_by_number(chipNum);
		// Verify the chip was opened
		if (chip != null) {
			final gpiod_line line = lib.gpiod_chip_get_line(chip, lineNum);
			// Verify we have line
			if (line != null) {
				// Request falling edge events
				if (lib.gpiod_line_request_falling_edge_events(line, consumer) == 0) {
					System.out.println("Press button within 5 seconds");
					final int rc = lib.gpiod_line_event_wait(line, new timespec(new NativeLong(5), new NativeLong(0)));
					if (rc == 0) {
						System.out.println("Timed out");
					} else if (rc == 1) {
						System.out.println("Event happened");
						final gpiod_line_event.ByValue event = new gpiod_line_event.ByValue();
						// Read event off queue
						lib.gpiod_line_event_read(line, event);
						System.out.println(event.event_type);
					} else {
						System.out.println("Error");
					}
				} else {
					System.out.println(String.format("Unable to set line %d to output", lineNum));
				}
				lib.gpiod_line_release(line);
			} else {
				System.out.println(String.format("Unable to get line %d", lineNum));
			}
			lib.gpiod_chip_close(chip);
		} else {
			System.out.println(String.format("Unable to open chip %d", chipNum));
		}
	}
}
