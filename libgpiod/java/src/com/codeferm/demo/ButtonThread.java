package com.codeferm.demo;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import com.sun.jna.NativeLong;

import gpiod.GpiodLibrary;
import gpiod.gpiod_chip;
import gpiod.gpiod_line;
import gpiod.gpiod_line_event;
import gpiod.timespec;

/**
 * Use a thread to monitor edge events in background.
 * 
 * Should work on any board with a button built in. Just change chip and line
 * value as needed.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class ButtonThread {

	/**
	 * Wait for edge thread.
	 * 
	 * @param line
	 *            GPIO line.
	 * @param consumer
	 *            Consumer name.
	 * @param timeoutSecs
	 *            Timeout seconds.
	 * @param executor
	 *            Executor service.
	 * @param lib
	 *            JNA library.
	 */
	public void submitWaitForEdge(final gpiod_line line, final String consumer, final int timeoutSecs,
			final ExecutorService executor, final GpiodLibrary lib) {
		// Returned event
		final gpiod_line_event event = new gpiod_line_event();
		// Timestamp formatter
		final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/dd/yyyy HH:mm:ss");
		// Submit lambda
		executor.submit(() -> {
			int rc = 1;
			while (rc == 1) {
				// Wait for event
				rc = lib.gpiod_line_event_wait(line, new timespec(new NativeLong(timeoutSecs), new NativeLong(0)));
				if (rc == 0) {
					System.out.println("Thread timed out");
				} else if (rc == 1) {
					// Read event off queue
					if (lib.gpiod_line_event_read(line, event) == 0) {
						final LocalDateTime date = LocalDateTime.ofInstant(
								Instant.ofEpochMilli(event.getTs().tv_sec.longValue() * 1000), ZoneId.systemDefault());
						if (event.getEvent_type() == GpiodLibrary.GPIOD_LINE_EVENT_RISING_EDGE) {
							System.out.println(String.format("Rising  edge timestamp %s", date.format(formatter)));
						} else {
							System.out.println(String.format("Falling edge timestamp %s", date.format(formatter)));
						}
					} else {
						System.err.println("gpiod_line_event_read error");
						rc = -1;
					}
				} else {
					System.err.println("gpiod_line_event_wait error");
					rc = -1;
				}
			}
		});
	}

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
		final String consumer = ButtonThread.class.getSimpleName();
		// Load library
		final GpiodLibrary lib = GpiodLibrary.INSTANCE;
		final gpiod_chip chip = lib.gpiod_chip_open_by_number(chipNum);
		// Verify the chip was opened
		if (chip != null) {
			final gpiod_line line = lib.gpiod_chip_get_line(chip, lineNum);
			// Verify we have line
			if (line != null) {
				// Request both edge events
				if (lib.gpiod_line_request_both_edges_events(line, consumer) == 0) {
					// Use executor service to run background thread
					final ExecutorService executor = Executors.newSingleThreadExecutor();
					final ButtonThread buttonThread = new ButtonThread();
					// Submit thread
					buttonThread.submitWaitForEdge(line, consumer, 5, executor, lib);
					try {
						// Initiate shutdown
						executor.shutdown();
						int count = 0;
						while (count <= 30 && !executor.isTerminated()) {
							System.out.println("Main program doing stuff, press button");
							TimeUnit.SECONDS.sleep(1);
							count++;
						}
						// Wait for thread to finish
						if (!executor.isTerminated()) {
							System.out.println("Waiting for thread to finish");
							executor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
						}
					} catch (InterruptedException e) {
						System.err.println("Tasks interrupted");
					} finally {
						executor.shutdownNow();
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
