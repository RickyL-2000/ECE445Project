
#define LOG_LOCAL_LEVEL ESP_LOG_INFO

#include <esp_log.h>

#include "i2c.hpp"
#include "kalmanfilter.hpp"
#include "mpu6050.hpp"
#include "wifi.h"
#include "tcp_client.hpp"

#include "nvs_flash.h"

#include <freertos/semphr.h>
#include <freertos/FreeRTOS.h>
#include <cmath>
#include <stdio.h>
#include "driver/gpio.h"

#include "esp_timer.h"

static gpio_num_t i2c_gpio_sda = (gpio_num_t) 15;
static gpio_num_t i2c_gpio_scl = (gpio_num_t) 2;
static gpio_num_t color_button_pin = (gpio_num_t) 12;
static gpio_num_t move_button_pin = (gpio_num_t) 13;
static gpio_num_t record_button_pin = (gpio_num_t) 14;
static gpio_num_t music_button_pin = (gpio_num_t) 15;

static gpio_num_t button_pins[3] = {move_button_pin, color_button_pin, record_button_pin};

#define I2C_NUM I2C_NUM_0
#define DEBOUNCE_TIME (50/portTICK_PERIOD_MS)
#define HIGH 1
#define LOW 0
#define PRESS 1
#define RELEASE 0
#define BUTTON_NUM 4

typedef struct mpuData_t {
    float fpitch;
    float froll;
//    uint8_t record_button_pin;
//    uint8_t stop_button;
//    uint8_t repeat_button;
} mpuData_t;

typedef int buttonData_t;

typedef struct sharedData_t {
    SemaphoreHandle_t mutex;
    void *data_p;
} sharedData_t;

typedef struct tcpClientParameter_t {
    sharedData_t *mpuData_p;
    sharedData_t *buttonsData_p;
} tcpClientParameter_t;

static void vTaskMpu6050(void *pvParameters) {

    const char TAG[] = "mpu_task";
    auto *sharedMpuData_p = (struct sharedData_t *) pvParameters;

    /* Uncomment the following line if MPU6050 is connected */
    MPU6050 mpu(i2c_gpio_scl, i2c_gpio_sda, I2C_NUM);
    if (ESP_FAIL == mpu.init()) {
        ESP_LOGE("mpu6050", "init failed!");
        vTaskDelete(nullptr);
    }
    ESP_LOGI("mpu6050", "init success!");

    float ax, ay, az, gx, gy, gz, R_pitch, R_roll;
    float pitch, roll;
    float fpitch, froll;
    int count = 0;

    KALMAN pfilter(0.005);
    KALMAN rfilter(0.005);

    const TickType_t xPeriodTicks = 10 / portTICK_PERIOD_MS;
    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        ESP_LOGD(TAG, "wake at %lu", (unsigned long) xLastWakeTime);

        /* Uncomment the following line if MPU6050 is connected */
        ax = -mpu.getAccX();
        ay = -mpu.getAccY();
        az = -mpu.getAccZ();
        gx = mpu.getGyroX();
        gy = mpu.getGyroY();
        gz = mpu.getGyroZ();

//        G = sqrtf(ax * ax + ay * ay + az * az);
        R_pitch = sqrtf(ax * ax + az * az);
        R_roll = sqrtf(ay * ay + az * az);
        pitch = (float) (acosf(az / R_pitch) * 57.2958); // 57.2958 = 360/2/pi
        roll = (float) (acosf(az / R_roll) * 57.2958);

        fpitch = pfilter.filter(pitch, gy) * abs(ax) / ax;
        froll = rfilter.filter(roll, -gx) * abs(ay) / ay;

//        fpitch = (float)count-180;
//        froll = (float)count-180;
//        count = (count+1)%360;
//        ESP_LOGD(TAG, "take mutex");
//        if (xSemaphoreTake(sharedMpuData_p->mutex, 0) == pdTRUE) {
        ((mpuData_t *) sharedMpuData_p->data_p)->fpitch = fpitch;
        ((mpuData_t *) sharedMpuData_p->data_p)->froll = froll;
//            xSemaphoreGive(sharedMpuData_p->mutex);

//            ESP_LOGI(TAG, "MPU angle: (%.2f, %.2f)", fpitch, froll);
//            ESP_LOGD(TAG, "give mutex");

//            /* MPU6050 data details */
//            count++;
//            printf("Samples:%d ", count);
//            printf(" Acc:(%4.2f,%4.2f,%4.2f)", ax, ay, az);
//            printf("Gyro:(%6.3f,%6.3f,%6.3f)", gx, gy, gz);
//            printf(" Pitch:%6.3f ", pitch);
//            printf(" Roll:%6.3f ", roll);
//            printf(" FPitch:%6.3f ", fpitch);
//            printf(" FRoll:%6.3f \n", froll);
        vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
//        } else {
//            ESP_LOGD(TAG, "fail to take mutex");
//        }
    }
    vTaskDelete(nullptr);

}

static void vTaskTcpClient(void *pvParameters) {
    const char TAG[] = "tcp_client_task";

    auto *tcpClientParameter_p = (tcpClientParameter_t *) pvParameters;
    auto *sharedMpuData_p = tcpClientParameter_p->mpuData_p;
    auto *sharedButtonData_p = tcpClientParameter_p->buttonsData_p;
    TcpClient client;
    auto *msg = (char *) malloc(sizeof(char) * 50);
    auto *MpuData_p = (mpuData_t *) malloc(sizeof(mpuData_t));
    auto *buttonData_p = (buttonData_t *) malloc(sizeof(buttonData_t) * 3); // pointer to a 3 length buttonsData_p array


    const TickType_t xPeriodTicks = 10 / portTICK_PERIOD_MS;
    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();

    for (;;) {
        ESP_LOGD(TAG, "wake at %lu", (unsigned long) xLastWakeTime);
//        ESP_LOGD(TAG, "take MPU mutex");
//        if (xSemaphoreTake(sharedMpuData_p->mutex, 0) == pdTRUE) {
        MpuData_p->fpitch = ((mpuData_t *) sharedMpuData_p->data_p)->fpitch;
        MpuData_p->froll = ((mpuData_t *) sharedMpuData_p->data_p)->froll;
//            xSemaphoreGive(sharedMpuData_p->mutex);
//            ESP_LOGI(TAG, "from MPU mutex: %.2f, %.2f", MpuData_p->fpitch, MpuData_p->froll);
//            ESP_LOGD(TAG, "give MPU mutex");
//        } else {
//            ESP_LOGD(TAG, "fail to take MPU mutex");
//        }

//        ESP_LOGD(TAG, "take BUTTON mutex");
//        if (xSemaphoreTake(sharedButtonData_p->mutex, 0) == pdTRUE) {
        for (int button_idx = 0; button_idx < 3; button_idx++) {
            buttonData_p[button_idx] = (*((buttonData_t (*)[]) sharedButtonData_p->data_p))[button_idx];
        }
//            xSemaphoreGive(sharedButtonData_p->mutex);
//            ESP_LOGI(TAG, "from BUTTON mutex: %d, %d, %d", buttonsData_p[0], buttonsData_p[1], buttonsData_p[2]);
//            ESP_LOGD(TAG, "give BUTTON mutex");
//        } else {
//            ESP_LOGD(TAG, "fail to take BUTTON mutex");
//        }

        sprintf(msg, "%.2f, %.2f, %d, %d, %d, %d", MpuData_p->fpitch, MpuData_p->froll, buttonData_p[0], buttonData_p[1],
                buttonData_p[2],buttonData_p[3]);

        client.send(msg);
        ESP_LOGI(TAG, "send %s", msg);
        vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
    }
    vTaskDelete(nullptr);
}

static void vTaskButton(void *pvParameters) {
    const char TAG[] = "button_task";
    auto *sharedButtonData_p = (struct sharedData_t *) pvParameters;

    TickType_t lastBounceTime = 0;
    static int lastBounceState[BUTTON_NUM] = {LOW, LOW, LOW};
    static int buttonStates[BUTTON_NUM] = {LOW, LOW, LOW};
    gpio_set_pull_mode(record_button_pin, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(color_button_pin, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(move_button_pin, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(music_button_pin, GPIO_PULLUP_ONLY);

    const TickType_t xPeriodTicks = 10 / portTICK_PERIOD_MS;
    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        for (int button_idx = 0; button_idx < BUTTON_NUM; button_idx++) {

            // read the level of button pin, and turn the voltage level to logical truth
            int currentState = (1 - gpio_get_level(button_pins[button_idx]));

            if (currentState != lastBounceState[button_idx]) {
                lastBounceTime = xLastWakeTime;
                lastBounceState[button_idx] = currentState;
            }
            // output the last state until the signal is stable for the whole DEBOUNCE_TIME period.
            if ((xTaskGetTickCount() - lastBounceTime) > DEBOUNCE_TIME) {
                buttonStates[button_idx] = currentState;
            }

        }
//        ESP_LOGD(TAG, "take mutex");
//        if (xSemaphoreTake(sharedButtonData_p->mutex, 50) == pdTRUE) {
        for (int button_idx = 0; button_idx < BUTTON_NUM; button_idx++) {
            (*((buttonData_t (*)[]) sharedButtonData_p->data_p))[button_idx] = buttonStates[button_idx];
        }
//            xSemaphoreGive(sharedButtonData_p->mutex);
//            ESP_LOGI(TAG, "Button states (%d, %d, %d)", buttonStates[0], buttonStates[1], buttonStates[2]);
//            ESP_LOGD(TAG, "give mutex");
//        } else {
//            ESP_LOGD(TAG, "fail to take mutex");
//        }
        vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
    }
    vTaskDelete(nullptr);
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

    // Initialize wifi and connect
    wifi_init_sta();

    auto *sharedMpuData_p = (sharedData_t *) malloc(sizeof(sharedData_t));
    sharedMpuData_p->mutex = xSemaphoreCreateMutex();
    auto *mpuData_p = (mpuData_t *) malloc(sizeof(mpuData_t));
    sharedMpuData_p->data_p = (void *) mpuData_p;

    auto *sharedButtonData_p = (sharedData_t *) malloc(sizeof(sharedData_t));
    sharedButtonData_p->mutex = xSemaphoreCreateMutex();
    // pointer to a 3 length buttonsData_p array
    auto *buttonsData_p = (buttonData_t(*)[]) malloc(sizeof(buttonData_t) * BUTTON_NUM);
    sharedButtonData_p->data_p = (void *) buttonsData_p;

    auto *tcpClientParameter_p = (tcpClientParameter_t *) malloc(sizeof(tcpClientParameter_t));
    tcpClientParameter_p->mpuData_p = sharedMpuData_p;
    tcpClientParameter_p->buttonsData_p = sharedButtonData_p;

    TaskHandle_t mpu6050_handle;
    xTaskCreate(vTaskMpu6050, "vTaskMpu6050", 4096, sharedMpuData_p, 2, &mpu6050_handle);

    TaskHandle_t tcp_client_handle;
    xTaskCreate(vTaskTcpClient, "vTaskTcpClient", 4096, tcpClientParameter_p, 5, &tcp_client_handle);

    TaskHandle_t button_handle;
    xTaskCreate(vTaskButton, "vTaskButton", 4096, sharedButtonData_p, 2, &button_handle);

}