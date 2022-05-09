#include "servo.hpp"

Servo::Servo(int servo_type, gpio_num_t gpio_num,
             mcpwm_unit_t mcpwm_unit, mcpwm_io_signals_t mcpwm_io_signal,
             mcpwm_timer_t mcpwm_timer, mcpwm_generator_t mcpwm_generator) {
    if (servo_type == DS3230) {
        servo_max_degree = SERVO_MAX_DEGREE_DS3230;
    } else if (servo_type == DS3218) {
        servo_max_degree = SERVO_MAX_DEGREE_DS3218;
    }
    servo_name = servo_type;
    servo_pulse_gpio = gpio_num;
    servo_mcpwm_unit = mcpwm_unit;
    servo_mcpwm_io_signal = mcpwm_io_signal;
    servo_mcpwm_timer = mcpwm_timer;
    servo_mcpwm_generator = mcpwm_generator;

    ESP_ERROR_CHECK(mcpwm_gpio_init(mcpwm_unit, mcpwm_io_signal, servo_pulse_gpio));

    mcpwm_config_t pwm_config = {
            .frequency = 50, // frequency = 50Hz, i.e. for every servo motor time period should be 20ms
            .cmpr_a = 0,     // duty cycle of PWMxA = 0
            .cmpr_b = 0,
            .duty_mode = MCPWM_DUTY_MODE_0,
            .counter_mode = MCPWM_UP_COUNTER,
    };
    ESP_ERROR_CHECK(mcpwm_init(mcpwm_unit, mcpwm_timer, &pwm_config));
}

uint32_t Servo::angle2dutyus(int angle) const {
    return (angle + servo_max_degree) * (SERVO_MAX_PULSEWIDTH_US - SERVO_MIN_PULSEWIDTH_US) /
            (2 * servo_max_degree) + SERVO_MIN_PULSEWIDTH_US;
}

esp_err_t Servo::set_angle(int angle) {
    if (servo_name == DS3218) {
        ESP_ERROR_CHECK(
                mcpwm_set_duty_in_us(servo_mcpwm_unit, servo_mcpwm_timer, servo_mcpwm_generator, angle2dutyus(angle))
        );
        return ESP_OK;
    } else if (servo_name == DS3230) {
           float ccw_speed = 215.18;
           float cw_speed = 193.75;
           float offset;
           int speed_index = 180;
           if (abs(servo_angle - angle) > abs((servo_angle+360)%360 - (angle+360)%360)) {
               offset =  (float)((angle+360) % 360 - (servo_angle+360) % 360);
           } else {
               offset = (float) (angle - servo_angle);
           }
           if (offset > 0) {
               speed_index = abs(speed_index);
               ESP_ERROR_CHECK(mcpwm_set_duty_in_us(servo_mcpwm_unit, servo_mcpwm_timer,
                                                    servo_mcpwm_generator, angle2dutyus(speed_index)));
               vTaskDelay(pdMS_TO_TICKS(int(1000 * abs(offset) / ccw_speed)));
               ESP_ERROR_CHECK(mcpwm_set_duty_in_us(servo_mcpwm_unit, servo_mcpwm_timer,
                                                    servo_mcpwm_generator, angle2dutyus(0)));
           } else if (offset < 0) {
               speed_index = -abs(speed_index);
               ESP_ERROR_CHECK(mcpwm_set_duty_in_us(servo_mcpwm_unit, servo_mcpwm_timer,
                                                    servo_mcpwm_generator, angle2dutyus(speed_index)));
               vTaskDelay(pdMS_TO_TICKS(int(1000 * abs(offset) / cw_speed)));
               ESP_ERROR_CHECK(mcpwm_set_duty_in_us(servo_mcpwm_unit, servo_mcpwm_timer,
                                                    servo_mcpwm_generator, angle2dutyus(0)));
           }
           servo_angle = angle;
           return ESP_OK;
    }
    return ESP_OK;
}
