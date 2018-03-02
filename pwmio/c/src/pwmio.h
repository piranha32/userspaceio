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

/**
 * @brief Open PWM device.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @return bytes written (1) or < 0 error.
 */
int pwm_open_device(int device);

/**
 * @brief Close PWM device.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @return bytes written (1) or < 0 error.
 */
int pwm_close_device(int device);

/**
 * @brief Enable PWM pin.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @param pwm Number after sys/class/pwm/pwmchip/pwm.
 * @return bytes written (1) or < 0 error.
 */
int pwm_enable(int device, int pmw);

/**
 * @brief Disable PWM pin.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @param pwm Number after /sys/class/pwm/pwmchip/pwm.
 * @return bytes written (1) or < 0 error.
 */
int pwm_disable(int device, int pmw);

/**
 * @brief Set the polarity to active HIGH (echo normal) or active LOW (echo inversed).
 * Must be done before enabled.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @param pwm Number after /sys/class/pwm/pwmchip/pwm.
 * @param polarity Number after /sys/class/pwm/pwmchip/pwm.
 * @return bytes written (1) or < 0 error.
 */
int pwm_set_polarity(int device, int pmw, const char *polarity);

/**
 * @brief Set the period in nanoseconds.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @param pwm Number after /sys/class/pwm/pwmchip/pwm.
 * @param period Period in nanoseconds.
 * @return bytes written (number of chars) or < 0 error.
 */
int pwm_set_period(int device, int pwm, int period);

/**
 * @brief Set the duty cycle in nanoseconds.
 * @param device Number after /sys/class/pwm/pwmchip.
 * @param pwm Number after /sys/class/pwm/pwmchip/pwm.
 * @param duty_cycle Duty cycle in nanoseconds.
 * @return bytes written (1) or < 0 error.
 */
int pwm_set_duty_cycle(int device, int pwm, int duty_cycle);
