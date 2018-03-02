package com.codeferm.demo;

import java.util.concurrent.TimeUnit;

import com.codeferm.Pwm;

import pwmio.PwmioLibrary;

/**
 * Simple LED blink using PWM.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class LedFlash {

	public void changeBrightness(final PwmioLibrary lib, final int device, final int pwm, final int period,
			final int startDc, final int dcInc, final int count, final int sleepTime) throws InterruptedException {
		lib.pwm_set_period(device, pwm, period);
		int dutyCycle = startDc;
		int i = 0;
		while (i < count) {
			lib.pwm_set_duty_cycle(device, pwm, dutyCycle);
			TimeUnit.MICROSECONDS.sleep(sleepTime);
			dutyCycle += dcInc;
			i += 1;
		}
	}

	public static void main(String args[]) throws InterruptedException {
		int device = 0;
		int pwmNum = 0;
		// See if there are args to parse
		if (args.length > 0) {
			// PWM device (default 0 = sys/class/pwm/pwmchip0)
			device = Integer.parseInt(args[0]);
			// PWM pin (default 0 = /sys/class/pwm/pwmchip0/pwm0)
			pwmNum = Integer.parseInt(args[1]);
		}
		// Use to debug if JNA cannot find shared library
		System.setProperty("jna.debug_load", "false");
		System.setProperty("jna.debug_load.jna", "false");
		final LedFlash ledFlash = new LedFlash();
		final Pwm pwm = new Pwm();
		final PwmioLibrary lib = pwm.getLib();
		try {
			pwm.open(device, pwmNum);
			lib.pwm_enable(device, pwmNum);
			for (int i = 0; i < 10; i++) {
				ledFlash.changeBrightness(lib, device, pwmNum, 1000, 0, 10, 100, 5000);
				ledFlash.changeBrightness(lib, device, pwmNum, 1000, 1000, -10, 100, 5000);
			}
		} finally {
            lib.pwm_set_duty_cycle(device, pwmNum, 0);
            lib.pwm_set_period(device, pwmNum, 0);			
			lib.pwm_disable(device, pwmNum);
			pwm.close(device);
		}
	}
}
