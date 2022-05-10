#include "wifi.h"
#include "tcp_server.h"
#include "ws2812.hpp"
#include "servo.hpp"
// #include "can.hpp"

#include "nvs_flash.h"

#include <esp_log.h>
#include <freertos/semphr.h>
#include <freertos/FreeRTOS.h>
#include <cmath>
#include <stdio.h>
#include <functional>

static const char *TAG = "light_main";

// parameters for ws2812 control
#define RMT_TX_CHANNEL RMT_CHANNEL_0
#define LED_NUMBER 64
static gpio_num_t RMT_TX_GPIO = (gpio_num_t) 25;

// parameters for servo control
static gpio_num_t SERVO_DS3230_GPIO = (gpio_num_t) 18;

typedef struct ledCommend_t {
    uint32_t R;
    uint32_t G;
    uint32_t B;
} ledCommend_t;

typedef struct commandQueues_t {
    QueueHandle_t ledQueue;
    QueueHandle_t stepQueue;
    QueueHandle_t servoQueue;
} commandQueues_t;

typedef struct tcpServerTaskParameters_t {
    commandQueues_t *commandQueues_p;
    int listen_sock;
} tcpServerTaskParameters_t;


//typedef struct sharedData_t {
//    SemaphoreHandle_t mutex;
//    void *data_p;
//} sharedData_t;


const TickType_t xPeriodTicks = 1000 / portTICK_PERIOD_MS;


void tcp_server_task(void *pvParameters) {
    static char TAG[] = "tcp_server_task";

    auto *parameters = (tcpServerTaskParameters_t *) pvParameters;
    char addr_str[128];
    int keepAlive = 1;
    int keepIdle = KEEPALIVE_IDLE;
    int keepInterval = KEEPALIVE_INTERVAL;
    int keepCount = KEEPALIVE_COUNT;
    for (;;) {

        ESP_LOGI(TAG, "Socket listening");

        struct sockaddr_storage source_addr{}; // Large enough for both IPv4 or IPv6
        socklen_t addr_len = sizeof(source_addr);
        int sock = accept(parameters->listen_sock, (struct sockaddr *) &source_addr, &addr_len);
        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to accept connection: errno %d", errno);
            break;
        }

        // Set tcp keepalive option
        setsockopt(sock, SOL_SOCKET, SO_KEEPALIVE, &keepAlive, sizeof(int));
        setsockopt(sock, IPPROTO_TCP, TCP_KEEPIDLE, &keepIdle, sizeof(int));
        setsockopt(sock, IPPROTO_TCP, TCP_KEEPINTVL, &keepInterval, sizeof(int));
        setsockopt(sock, IPPROTO_TCP, TCP_KEEPCNT, &keepCount, sizeof(int));
        // Convert ip address to string
        if (source_addr.ss_family == PF_INET) {
            inet_ntoa_r(((struct sockaddr_in *) &source_addr)->sin_addr, addr_str, sizeof(addr_str) - 1);
        }

        ESP_LOGI(TAG, "Socket accepted ip address: %s", addr_str);


        // receive message
        int recv_len;
        unsigned long slen;
        char output_buffer[BUFFER_SIZE];
        int buffer_size = BUFFER_SIZE;
//        char pitch_s[10], roll_s[10], R_s[5], G_s[5], B_s[5];
        float pitch, roll;
        ledCommend_t ledCommend;
        do {
            recv_len = recv(sock, &slen, sizeof(slen), 0);
            if (recv_len < 0) {
                ESP_LOGE(TAG, "Error occurred during receiving slen: errno %d", errno);
            } else if (recv_len == 0) {
                ESP_LOGW(TAG, "Connection closed during receiving slen");
            } else {

                // read all the current pack from socket buffer, avoiding influence the next pack
                if (slen > buffer_size) {
                    ESP_LOGE(TAG, "slen: %lu is larger than buffer size, this pack is dropped!", slen);
                    while (slen > 0) {
                        recv_len = recv(sock, output_buffer, slen > buffer_size ? buffer_size : slen, 0);
                        slen -= recv_len;
                    }
                    continue;
                }
                recv_len = recv(sock, output_buffer, slen, 0);
                if (recv_len < 0) {
                    ESP_LOGE(TAG, "Error occurred during receiving: errno %d", errno);
                } else if (recv_len == 0) {
                    ESP_LOGW(TAG, "Connection closed");
                } else {
                    output_buffer[slen] = 0; // Null-terminate whatever is received and treat it like a string
                    ESP_LOGI(TAG, "Received %d bytes: %s", recv_len, output_buffer);
                }
                sscanf(output_buffer, "(%f, %f), (%u, %u, %u)", &pitch, &roll, &(ledCommend.R), &(ledCommend.G),
                       &(ledCommend.B));

                // queue send will copy the content of the given pointer. So the buffer can be dynamically allocated.
                xQueueSend((parameters->commandQueues_p)->stepQueue, &pitch, 0);
                xQueueSend((parameters->commandQueues_p)->servoQueue, &roll, 0);
                xQueueSend((parameters->commandQueues_p)->ledQueue, &ledCommend, 0);

            }
        } while (recv_len > 0);

        shutdown(sock, 0);
        close(sock);
    }
    vTaskDelete(nullptr);
}

void dummy_control_task(void *pvParameters) {
    static char TAG[] = "dummy_control_task";
    auto *commandQueues = (commandQueues_t *) pvParameters;

    float pitch, roll;
    ledCommend_t ledCommend;

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        xQueueReceive(commandQueues->servoQueue, &roll, 0);
        xQueueReceive(commandQueues->stepQueue, &pitch, 0);
        xQueueReceive(commandQueues->ledQueue, &ledCommend, 0);
        ESP_LOGI(TAG, "receive from command queue: %.2f, %.2f, %u,%u,%u", pitch, roll, ledCommend.R, ledCommend.G,
                 ledCommend.B);
        vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
    }
    vTaskDelete(nullptr);
}

void led_control_task(void *pvParameters) {
    static char TAG[] = "led_control_task";
    auto *commandQueues = (commandQueues_t *) pvParameters;

    ledCommend_t ledCommend;

    led_strip_t *strip = led_strip_init(RMT_TX_CHANNEL, RMT_TX_GPIO, LED_NUMBER);
    // Show simple rainbow chasing pattern
    ESP_LOGI(TAG, "LED Rainbow Chase Start");

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        xQueueReceive(commandQueues->ledQueue, &ledCommend, 0);
        ESP_LOGI(TAG, "receive from led queue:  %u,%u,%u", ledCommend.R, ledCommend.G, ledCommend.B);
        for (int j = 0; j < LED_NUMBER; j++) {
            ESP_ERROR_CHECK(strip->set_pixel(strip, j, ledCommend.R, ledCommend.G, ledCommend.B));
        }
        // Flush RGB values to LEDs
        ESP_ERROR_CHECK(strip->refresh(strip, 100));
        vTaskDelay(pdMS_TO_TICKS(10));
        strip->clear(strip, 50);
        vTaskDelay(pdMS_TO_TICKS(10));

        vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
    }
    vTaskDelete(nullptr);
}


void dummy_led_task(void *pvParameters) {
    static char TAG[] = "dummy_led_task";

    led_strip_t *strip = led_strip_init(RMT_TX_CHANNEL, RMT_TX_GPIO, LED_NUMBER);

    // Show simple rainbow chasing pattern
    ESP_LOGI(TAG, "LED Rainbow Chase Start");
    uint32_t red = 0;
    uint32_t green = 0;
    uint32_t blue = 0;
    uint16_t hue = 0;
    uint16_t start_rgb = 0;
    for (;;) {
        for (int i = 0; i < 3; i++) {
            for (int j = i; j < LED_NUMBER; j += 3) {
                // Build RGB values
                hue = j * 360 / LED_NUMBER + start_rgb;
                led_strip_hsv2rgb(hue, 100, 100, &red, &green, &blue);
                // Write RGB values to strip driver
                // ESP_LOGI(TAG, "%d", j);
                ESP_ERROR_CHECK(strip->set_pixel(strip, j, red, green, blue));
            }
            // Flush RGB values to LEDs
            ESP_ERROR_CHECK(strip->refresh(strip, 100));
            vTaskDelay(pdMS_TO_TICKS(10));
            strip->clear(strip, 50);
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        start_rgb += 60;
    }
}

void dummy_servo_task(void *pvParameters) {
    // static char TAG[] = "dummy_servo_task";
    int servo_type = DS3230;

    // DS3218
    if (servo_type == DS3218) {
        static char TAG[] = "dummy_servo_task DS3218";
        Servo servo3218(servo_type, SERVO_DS3230_GPIO,
                        MCPWM_UNIT_0, MCPWM0A, MCPWM_TIMER_0, MCPWM_OPR_A);
        for (;;) {
            for (int angle = -SERVO_MAX_DEGREE_DS3218; angle < SERVO_MAX_DEGREE_DS3218; angle += 10) {
                ESP_LOGI(TAG, "Angle of rotation: %d", angle);
                ESP_ERROR_CHECK(servo3218.set_angle(angle));
                vTaskDelay(pdMS_TO_TICKS(500));
            }
            for (int angle = SERVO_MAX_DEGREE_DS3218; angle > -SERVO_MAX_DEGREE_DS3218; angle -= 10) {
                ESP_LOGI(TAG, "Angle of rotation: %d", angle);
                ESP_ERROR_CHECK(servo3218.set_angle(angle));
                vTaskDelay(pdMS_TO_TICKS(500));
            }
            vTaskDelay(pdMS_TO_TICKS(2000));
        }
    } else if (servo_type == DS3230) {
        // DS3230
        static char TAG[] = "dummy_servo_task DS3230";
        Servo servo3230(servo_type, SERVO_DS3230_GPIO,
                        MCPWM_UNIT_0, MCPWM0A, MCPWM_TIMER_0, MCPWM_OPR_A);
        for (;;) {
            for (int angle = -SERVO_MAX_DEGREE_DS3230; angle < SERVO_MAX_DEGREE_DS3230; angle += 10) {
                ESP_LOGI(TAG, "Angle of rotation: %d %d", angle, servo3230.servo_angle);
                ESP_ERROR_CHECK(servo3230.set_angle(angle));
                vTaskDelay(pdMS_TO_TICKS(500));
            }
            for (int angle = SERVO_MAX_DEGREE_DS3230; angle > -SERVO_MAX_DEGREE_DS3230; angle -= 10) {
                ESP_LOGI(TAG, "Angle of rotation: %d %d", angle, servo3230.servo_angle);
                ESP_ERROR_CHECK(servo3230.set_angle(angle));
                vTaskDelay(pdMS_TO_TICKS(500));
            }
            vTaskDelay(pdMS_TO_TICKS(2000));

            // ESP_ERROR_CHECK(servo3230.set_angle(-180));

            // vTaskDelay(pdMS_TO_TICKS(1000));
            // ESP_ERROR_CHECK(servo3230.set_angle(-100));
            // vTaskDelay(pdMS_TO_TICKS(1000));
            // ESP_ERROR_CHECK(servo3230.set_angle(0));
            // for (int angle = -SERVO_MAX_DEGREE_DS3230; angle < SERVO_MAX_DEGREE_DS3230; angle += 30) {
            //     ESP_LOGI(TAG, "Angle of rotation: %d", angle);
            //     ESP_ERROR_CHECK(servo3230.set_angle(30));
            //     vTaskDelay(pdMS_TO_TICKS(500));
            // }
            // for (int angle = SERVO_MAX_DEGREE_DS3230; angle > -SERVO_MAX_DEGREE_DS3230; angle -= 30) {
            //     ESP_LOGI(TAG, "Angle of rotation: %d", angle);
            //     ESP_ERROR_CHECK(servo3230.set_angle(-30));
            //     vTaskDelay(pdMS_TO_TICKS(500));
            // }
            // vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
}

extern "C" void app_main() {
    printf("app_main\n");

    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

   // // test dummy led
   // auto *commandQueues_p = (commandQueues_t *) malloc(sizeof(commandQueues_t));
   // TaskHandle_t dummy_led_handle;
   // xTaskCreate(dummy_led_task, "dummy_led", 4096,
   //             commandQueues_p, 5, &dummy_led_handle);

    // test dummy servo
    // auto *commandQueues_p = (commandQueues_t *) malloc(sizeof(commandQueues_t));
    // TaskHandle_t dummy_servo_handle;
    // xTaskCreate(dummy_servo_task, "dummy_servo", 4096,
    //             commandQueues_p, 5, &dummy_servo_handle);


    // Initialize wifi and connect
    wifi_init_sta();

   //  used for sharing data, but queue always copy, so un-used
   // auto *mpuData = (struct mpuData_t *) malloc(sizeof(struct mpuData_t));
   // auto *sharedMpuData = (sharedData_t *) malloc(sizeof(sharedData_t));
   // sharedMpuData->mutex = xSemaphoreCreateMutex();
   // sharedMpuData->data_p = (void *const) mpuData;


    // from tcp server to the command queue
    auto *commandQueues_p = (commandQueues_t *) malloc(sizeof(commandQueues_t));
    commandQueues_p->stepQueue = xQueueCreate(10, sizeof(float));
    commandQueues_p->servoQueue = xQueueCreate(10, sizeof(float));
    commandQueues_p->ledQueue = xQueueCreate(10, sizeof(ledCommend_t));


    int listen_sock = tcp_server_init();
    if (listen_sock == ESP_FAIL) {
        ESP_LOGE(TAG, "Failed to init tcp server");
    }

    auto *tcpServerTaskParameters = (tcpServerTaskParameters_t *) malloc(sizeof(tcpServerTaskParameters_t));
    tcpServerTaskParameters->commandQueues_p = commandQueues_p;
    tcpServerTaskParameters->listen_sock = listen_sock;

    TaskHandle_t tcp_server_handle;
    xTaskCreate(tcp_server_task, "tcp_server", 4096,
                tcpServerTaskParameters, 5, &tcp_server_handle);

    TaskHandle_t dummy_control_handle;
    xTaskCreate(dummy_control_task, "dummy_control", 4096,
                commandQueues_p, 5, &dummy_control_handle);

    TaskHandle_t led_control_handle;
    xTaskCreate(led_control_task, "led_control", 4096,
                commandQueues_p, 5, &led_control_handle);

}