#ifndef _SERVO_HPP
#define _SERVO_HPP

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_check.h"
#include "driver/mcpwm.h"

// You can get these value from the datasheet of servo you use, in general pulse width varies between 1000 to 2000 mocrosecond
#define SERVO_MIN_PULSEWIDTH_US (500) // Minimum pulse width in microsecond
#define SERVO_MAX_PULSEWIDTH_US (2500) // Maximum pulse width in microsecond
#define SERVO_MAX_DEGREE_DS3230 (180)   // Maximum angle in degree of DS3230 (360 / 2 = 180)
#define SERVO_MAX_DEGREE_DS3218 (135)   // Maximum angle in degree of DS3218 (270 / 2 = 135)

// 3230 (360舵机)
// failed
// CCW: 10圈用了16.73秒，即每秒215.18度，
// CW: 10圈用了18.58秒，即每秒193.75

#define DS3230 3230
#define DS3218 3218


class Servo {

private:
    static constexpr const char *TAG = "servo";
    int servo_name;    // DS3230, or DS3218
    int servo_max_degree;
    gpio_num_t servo_pulse_gpio;
    mcpwm_unit_t servo_mcpwm_unit;
    mcpwm_io_signals_t servo_mcpwm_io_signal;
    mcpwm_timer_t servo_mcpwm_timer;
    mcpwm_generator_t servo_mcpwm_generator;

    uint32_t angle2dutyus(float angle) const;

public:
    int servo_angle = 0;

    Servo(int servo_type, gpio_num_t gpio_num,
          mcpwm_unit_t mcpwm_unit, mcpwm_io_signals_t mcpwm_io_signal,
          mcpwm_timer_t mcpwm_timer, mcpwm_generator_t mcpwm_generator);

    esp_err_t set_angle(float angle);
};

#endif //_SERVO_HPP
