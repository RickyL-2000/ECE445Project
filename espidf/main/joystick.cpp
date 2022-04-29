#include "i2c.hpp"
#include "kalmanfilter.hpp"
#include "mpu6050.hpp"
#include "wifi.h"
#include "tcp_client.hpp"

#include "nvs_flash.h"

#include <esp_log.h>
#include <freertos/semphr.h>
#include <freertos/FreeRTOS.h>
#include <cmath>
#include <stdio.h>
#include "driver/gpio.h"

#include "esp_timer.h"

static gpio_num_t i2c_gpio_sda = (gpio_num_t) 15;
static gpio_num_t i2c_gpio_scl = (gpio_num_t) 2;
static gpio_num_t i2c_record_button = (gpio_num_t) 13;
static gpio_num_t i2c_stop_button = (gpio_num_t) 12;
static gpio_num_t i2c_repeat_button = (gpio_num_t) 14;

#define I2C_NUM I2C_NUM_0
#define DEBOUNCE_TIME 50
#define HIGH 1
#define LOW 0
#define PRESS 1
#define RELEASE 0

struct mpuData_t {
    float fpitch;
    float froll;
    uint8_t record_button;
    uint8_t stop_button;
    uint8_t repeat_button;
};

struct sharedData_t {
    SemaphoreHandle_t mutex;
    void *data_p;
};

const TickType_t xPeriodTicks = 100 / portTICK_PERIOD_MS;

static void vTaskMpu6050(void *pvParameters) {

    auto *sharedMpuData_p = (struct sharedData_t *const) pvParameters;

    /* Uncomment the following line if MPU6050 is connected */
    MPU6050 mpu(i2c_gpio_scl, i2c_gpio_sda, I2C_NUM);
    if (ESP_FAIL == mpu.init()) {
        ESP_LOGE("mpu6050", "init failed!");
        vTaskDelete(nullptr);
    }
    ESP_LOGI("mpu6050", "init success!");

    float ax, ay, az, gx, gy, gz;
    float pitch, roll;
    float fpitch, froll;
    int count = 0;
//
    KALMAN pfilter(0.005);
    KALMAN rfilter(0.005);

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        const char TAG[] = "mpu_task";
        ESP_LOGI(TAG, "wake at %lu", (unsigned long) xLastWakeTime);

        /* Uncomment the following line if MPU6050 is connected */
        ax = -mpu.getAccX();
        ay = -mpu.getAccY();
        az = -mpu.getAccZ();
        gx = mpu.getGyroX();
        gy = mpu.getGyroY();
        gz = mpu.getGyroZ();
        pitch = (float)(atan(ax / az) * 57.2958);
        roll = (float)(atan(ay / az) * 57.2958);
        fpitch = pfilter.filter(pitch, gy);
        froll = rfilter.filter(roll, -gx);



        if (xSemaphoreTake(sharedMpuData_p->mutex, 0) == pdTRUE) {
            ESP_LOGI(TAG, "take mutex");
            ((mpuData_t *) sharedMpuData_p->data_p)->fpitch = fpitch;
            ((mpuData_t *) sharedMpuData_p->data_p)->froll = froll;
            ESP_LOGI(TAG, "value to: %.2f", (float) count);
            ESP_LOGI(TAG, "give mutex");

            /* MPU6050 data details */
            count++;
            printf("Samples:%d ", count);
            printf(" Acc:(%4.2f,%4.2f,%4.2f)", ax, ay, az);
            printf("Gyro:(%6.3f,%6.3f,%6.3f)", gx, gy, gz);
            printf(" Pitch:%6.3f ", pitch);
            printf(" Roll:%6.3f ", roll);
            printf(" FPitch:%6.3f ", fpitch);
            printf(" FRoll:%6.3f \n", froll);

            xSemaphoreGive(sharedMpuData_p->mutex);
            vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
        }
//        else {
//            ESP_LOGW(TAG, "fail to take mutex");
//        }


//        /* MPU6050 data details */
//        count++;
//        printf("Samples:%d ", count);
//        printf(" Acc:(%4.2f,%4.2f,%4.2f)", ax, ay, az);
//        printf("Gyro:(%6.3f,%6.3f,%6.3f)", gx, gy, gz);
//        printf(" Pitch:%6.3f ", pitch);
//        printf(" Roll:%6.3f ", roll);
//        printf(" FPitch:%6.3f ", fpitch);
//        printf(" FRoll:%6.3f \n", froll);
    }
    vTaskDelete(nullptr);

}


static void vTaskTcpClient(void *pvParameters) {
    const char TAG[] = "tcp_task";
    TcpClient client;
    auto sharedMpuData_p = (sharedData_t *const) pvParameters; // share MpuData_p 应该是指针吧
    auto *msg = (char *) malloc(sizeof(char) * 50);
    auto *MpuData_p = (struct mpuData_t *) malloc(sizeof(struct mpuData_t));

//    vTaskDelay(1000/portTICK_PERIOD_MS);

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();

    for (;;) {
//        ESP_LOGI(TAG, "wake at %lu", (unsigned long) xLastWakeTime);
        if (xSemaphoreTake(sharedMpuData_p->mutex, 0) == pdTRUE) {
            ESP_LOGI(TAG, "take mutex");
            MpuData_p->fpitch = ((mpuData_t *const) sharedMpuData_p->data_p)->fpitch;
            MpuData_p->froll = ((mpuData_t *const) sharedMpuData_p->data_p)->froll;
            MpuData_p->record_button = ((mpuData_t *const) sharedMpuData_p->data_p)->record_button;
            ((mpuData_t *) sharedMpuData_p->data_p)->record_button = RELEASE;
            ESP_LOGI(TAG, "from mutex: %.2f, %.2f, %d", MpuData_p->fpitch, MpuData_p->froll, MpuData_p->record_button);
            ESP_LOGI(TAG, "give mutex");
            xSemaphoreGive(sharedMpuData_p->mutex);
            sprintf(msg, "fpitch:%.2f, froll:%.2f, record_button:%d", MpuData_p->fpitch, MpuData_p->froll, MpuData_p->record_button);
            client.send(msg);
            vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);

//            vTaskDelay(xPeriodTicks);
        }
//        else
//        {
//            ESP_LOGW(TAG, "fail to take mutex");
//        }
    }
    vTaskDelete(nullptr);
}

static void record_button_f(void *pvParameters){
    const char TAG[] = "record_button";
    uint8_t laststeadystate = HIGH;
    uint8_t currentstate;
    uint8_t lastbouncestate = HIGH;
    uint64_t lastbouncetime = 0;
    uint64_t currenttime;
    gpio_set_pull_mode(i2c_record_button, GPIO_PULLUP_ONLY );
    auto *sharedMpuData_p = (struct sharedData_t *const) pvParameters;
    for (;;){
//        ESP_LOGI(TAG, "level of Pin13 %d", gpio_get_level(i2c_record_button));
        currentstate = gpio_get_level(i2c_record_button);
        if (currentstate != lastbouncestate){
            lastbouncetime = esp_timer_get_time();
            lastbouncestate = currentstate;
        }
        currenttime = esp_timer_get_time();
        if ((currenttime - lastbouncetime) > DEBOUNCE_TIME){
            if (laststeadystate == HIGH && currentstate == LOW){
                if (xSemaphoreTake(sharedMpuData_p->mutex, 50) == pdTRUE){
                    ESP_LOGI(TAG, "take mutex");
                    ((mpuData_t *const) sharedMpuData_p->data_p)->record_button = PRESS;
                    ESP_LOGI(TAG, "record button was pressed");
                    ESP_LOGI(TAG, "give mutex");
                    xSemaphoreGive(sharedMpuData_p->mutex);
                }
            }
//            else{
//                if (xSemaphoreTake(sharedMpuData_p->mutex, 50) == pdTRUE){
//                    ((mpuData_t *const) sharedMpuData_p->data_p)->record_button = RELEASE;
//                    xSemaphoreGive(sharedMpuData_p->mutex);
//                }
//            }
            laststeadystate = currentstate;
        }
    }
    vTaskDelete(nullptr);
}

static void stop_button_f(void *pvParameters){
    const char TAG[] = "stop_button";
    uint8_t laststeadystate = HIGH;
    uint8_t currentstate;
    uint8_t lastbouncestate = HIGH;
    uint64_t lastbouncetime = 0;
    uint64_t currenttime;
    gpio_set_pull_mode(i2c_stop_button, GPIO_PULLUP_ONLY );
    auto *sharedMpuData_p = (struct sharedData_t *const) pvParameters;
    for (;;){
        currentstate = gpio_get_level(i2c_stop_button);
        if (currentstate != lastbouncestate){
            lastbouncetime = esp_timer_get_time();
            lastbouncestate = currentstate;
        }
        currenttime = esp_timer_get_time();
        if ((currenttime - lastbouncetime) > DEBOUNCE_TIME){
            if (laststeadystate == HIGH && currentstate == LOW){
                if (xSemaphoreTake(sharedMpuData_p->mutex, 50) == pdTRUE){
                    ESP_LOGI(TAG, "take mutex");
                    ((mpuData_t *const) sharedMpuData_p->data_p)->stop_button = PRESS;
                    ESP_LOGI(TAG, "stop button was pressed");
                    ESP_LOGI(TAG, "give mutex");
                    xSemaphoreGive(sharedMpuData_p->mutex);
                }
            }
//            else{
//                if (xSemaphoreTake(sharedMpuData_p->mutex, 50) == pdTRUE){
//                    ((mpuData_t *const) sharedMpuData_p->data_p)->stop_button = RELEASE;
//                    xSemaphoreGive(sharedMpuData_p->mutex);
//                }
//            }
            laststeadystate = currentstate;
        }
    }
    vTaskDelete(nullptr);
}

static void repeat_button_f(void *pvParameters){
    const char TAG[] = "repeat_button";
    uint8_t laststeadystate = HIGH;
    uint8_t currentstate;
    uint8_t lastbouncestate = HIGH;
    uint64_t lastbouncetime = 0;
    uint64_t currenttime;
    gpio_set_pull_mode(i2c_repeat_button, GPIO_PULLUP_ONLY );
    auto *sharedMpuData_p = (struct sharedData_t *const) pvParameters;
    for (;;){
        currentstate = gpio_get_level(i2c_repeat_button);
        if (currentstate != lastbouncestate){
            lastbouncetime = esp_timer_get_time();
            lastbouncestate = currentstate;
        }
        currenttime = esp_timer_get_time();
        if ((currenttime - lastbouncetime) > DEBOUNCE_TIME){
            if (laststeadystate == HIGH && currentstate == LOW){
                if (xSemaphoreTake(sharedMpuData_p->mutex, 50) == pdTRUE){
                    ESP_LOGI(TAG, "take mutex");
                    ((mpuData_t *const) sharedMpuData_p->data_p)->repeat_button = PRESS;
                    ESP_LOGI(TAG, "repeat button was pressed");
                    ESP_LOGI(TAG, "give mutex");
                    xSemaphoreGive(sharedMpuData_p->mutex);
                }
            }
//            else{
//                if (xSemaphoreTake(sharedMpuData_p->mutex, 50) == pdTRUE){
//                    ((mpuData_t *const) sharedMpuData_p->data_p)->repeat_button = RELEASE;
//                    xSemaphoreGive(sharedMpuData_p->mutex);
//                }
//            }
            laststeadystate = currentstate;
        }
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

    auto *mpuData = (struct mpuData_t *) malloc(sizeof(struct mpuData_t));
    auto *sharedMpuData = (sharedData_t *) malloc(sizeof(sharedData_t));

    sharedMpuData->mutex = xSemaphoreCreateMutex();
    sharedMpuData->data_p = (void *const) mpuData;


    TaskHandle_t mpu6050_handle;
    xTaskCreate(vTaskMpu6050, "vTaskMpu6050", 4096, sharedMpuData, 2, &mpu6050_handle);


    TaskHandle_t tcp_client_handle;
    xTaskCreate(vTaskTcpClient, "vTaskTcpClient", 4096, sharedMpuData, 2, &tcp_client_handle);

    TaskHandle_t record_button_handle;
    xTaskCreate(record_button_f, "record_button_f", 4096, sharedMpuData, 1, &record_button_handle);

    TaskHandle_t stop_button_handle;
    xTaskCreate(stop_button_f, "stop_button_f", 4096, sharedMpuData, 2, &stop_button_handle);

    TaskHandle_t repeat_button_handle;
    xTaskCreate(repeat_button_f, "repeat_button_f", 4096, sharedMpuData, 2, &repeat_button_handle);

//    TaskHandle_t tcp_server_handle;
//    xTaskCreate(tcp_server_task, "tcp_server", 4096, (void *) AF_INET, 5, &tcp_server_handle);


}