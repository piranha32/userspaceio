#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include "pwmio.h"

int main(void) {
	const int device = 0;
	const int pwm = 0;
	int rc, i, duty_cycle;

	rc = pwm_open_device(device);
	printf("pwm_open_device = %d\n", rc);
	usleep(1000000);
	rc = pwm_set_polarity(device, pwm, "inversed");
	printf("pwm_set_polarity = %d\n", rc);
	rc = pwm_set_polarity(device, pwm, "normal");
	printf("pwm_set_polarity = %d\n", rc);
	rc = pwm_enable(device, pwm);
	printf("pwm_enable = %d\n", rc);
	rc = pwm_set_period(device, pwm, 100000000);
	printf("pwm_set_period = %d\n", rc);
	duty_cycle = 300000;
	/* Increase duty cycle and flashing LED increases intensity */
	for (i = 1; i < 21; i += 1) {
		rc = pwm_set_duty_cycle(device, pwm, duty_cycle);
		printf("pwm_set_duty_cycle = %d\n", duty_cycle);
		// Sleep for a second
		usleep(1000000);
		duty_cycle += i * 100000;
	}
	rc = pwm_disable(device, pwm);
	printf("pwm_disable = %d\n", rc);
	rc = pwm_close_device(device);
	printf("pwm_close_device = %d\n", rc);
	return 0;
}
