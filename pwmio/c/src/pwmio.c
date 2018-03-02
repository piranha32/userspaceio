/**
 * Simple hardware PWM using /sys/class/pwm/pwmchip*
 *
 * Should work on any board with hardware PWM pin mapped to
 * /sys/class/pwm/pwmchip*. Use armbian-config and set pwm in Hardware
 * configuration. If you are not using Armbian you need a kernel that supports
 * /sys/class/pwm/pwmchip*
 *
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/types.h>
#include "pwmio.h"

#define PATH_MAX 128

int pwm_open_device(int device) {
	const char *value = "0";
	char file_name[PATH_MAX];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/export", device);
	handle = open(file_name, O_WRONLY);
	rc = write(handle, value, 1);
	close(handle);
	return rc;
}

int pwm_close_device(int device) {
	const char *value = "0";
	char file_name[PATH_MAX];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/unexport", device);
	handle = open(file_name, O_WRONLY);
	rc = write(handle, value, 1);
	close(handle);
	return rc;
}

int pwm_enable(int device, int pwm) {
	const char *value = "1";
	char file_name[PATH_MAX];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/pwm%d/enable", device, pwm);
	handle = open(file_name, O_WRONLY);
	rc = write(handle, value, 1);
	close(handle);
	return rc;
}

int pwm_disable(int device, int pwm) {
	const char *value = "0";
	char file_name[PATH_MAX];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/pwm%d/enable", device, pwm);
	handle = open(file_name, O_WRONLY);
	rc = write(handle, value, 1);
	close(handle);
	return rc;
}

int pwm_set_polarity(int device, int pwm, const char *polarity) {
	char file_name[PATH_MAX];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/pwm%d/polarity", device, pwm);
	handle = open(file_name, O_WRONLY);
	rc = write(handle, polarity, strlen(polarity));
	close(handle);
	return rc;
}

int pwm_set_period(int device, int pwm, int period) {
	char file_name[PATH_MAX];
	char period_str[12];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/pwm%d/period", device, pwm);
	handle = open(file_name, O_WRONLY);
	sprintf(period_str, "%d", period);
	rc = write(handle, period_str, strlen(period_str));
	close(handle);
	return rc;
}

int pwm_set_duty_cycle(int device, int pwm, int duty_cycle) {
	char file_name[PATH_MAX];
	char duty_cycle_str[12];
	int handle, rc;

	sprintf(file_name, "/sys/class/pwm/pwmchip%d/pwm%d/duty_cycle", device, pwm);
	handle = open(file_name, O_WRONLY);
	sprintf(duty_cycle_str, "%d", duty_cycle);
	rc = write(handle, duty_cycle_str, strlen(duty_cycle_str));
	close(handle);
	return rc;
}
