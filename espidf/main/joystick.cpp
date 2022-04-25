#include "mpu6050.hpp"
#include "kalmanfilter.hpp"
#include "wifi.h"
#include "tcp_server.h"
#include "tcp_client.hpp"

#include "nvs_flash.h"

#include <esp_log.h>
#include <freertos/semphr.h>
#include <freertos/FreeRTOS.h>
#include <cmath>
#include <stdio.h>

static gpio_num_t i2c_gpio_sda = (gpio_num_t) 15;
static gpio_num_t i2c_gpio_scl = (gpio_num_t) 2;
#define I2C_NUM I2C_NUM_0

struct mpuData_t {
    float fpitch;
    float froll;
};

struct sharedData_t {
    SemaphoreHandle_t mutex;
    void *data_p;
};

const TickType_t xPeriodTicks = 100 / portTICK_PERIOD_MS;

static void vTaskMpu6050(void *pvParameters) {

    auto *sharedMpuData_p = (struct sharedData_t *const) pvParameters;

    /* Uncomment the following line if MPU6050 is connected */
//    MPU6050 mpu(i2c_gpio_scl, i2c_gpio_sda, I2C_NUM);
//    if (ESP_FAIL == mpu.init()) {
//        ESP_LOGE("mpu6050", "init failed!");
//        vTaskDelete(nullptr);
//    }
//    ESP_LOGI("mpu6050", "init success!");
//
//    float ax, ay, az, gx, gy, gz;
//    float pitch, roll;
//    float fpitch, froll;
    int count = 0;
//
//    KALMAN pfilter(0.005);
//    KALMAN rfilter(0.005);

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        const char TAG[] = "mpu_task";
//        ESP_LOGI(TAG, "wake at %lu", (unsigned long) xLastWakeTime);

        /* Uncomment the following line if MPU6050 is connected */
//        ax = -mpu.getAccX();
//        ay = -mpu.getAccY();
//        az = -mpu.getAccZ();
//        gx = mpu.getGyroX();
//        gy = mpu.getGyroY();
//        gz = mpu.getGyroZ();
//        pitch = (float)(atan(ax / az) * 57.2958);
//        roll = (float)(atan(ay / az) * 57.2958);
//        mpuData.fpitch = pfilter.filter(pitch, gy);
//        mpuData.froll = filter.filter(roll, -gx);

        if (xSemaphoreTake(sharedMpuData_p->mutex, 0) == pdTRUE) {
            ESP_LOGI(TAG, "take mutex");
            ((mpuData_t *) sharedMpuData_p->data_p)->fpitch = (float) count;
            ((mpuData_t *) sharedMpuData_p->data_p)->froll = (float) count;
            ESP_LOGI(TAG, "value to: %.2f", (float) count);
            ESP_LOGI(TAG, "give mutex");
            xSemaphoreGive(sharedMpuData_p->mutex);
            vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);
        } else {
            ESP_LOGW(TAG, "fail to take mutex");
        }


        /* MPU6050 data details */
        count++;
//        printf("Samples:%d ", count);
//        count = 0;
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
    auto sharedMpuData_p = (sharedData_t *const) pvParameters;
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
            xSemaphoreGive(sharedMpuData_p->mutex);
            ESP_LOGI(TAG, "from mutex: %.2f, %.2f", MpuData_p->fpitch, MpuData_p->froll);
            ESP_LOGI(TAG, "give mutex");
            sprintf(msg, "fpitch:%.2f, froll:%.2f", MpuData_p->fpitch, MpuData_p->froll);
            client.send(msg);
            vTaskDelayUntil(&xLastWakeTime, xPeriodTicks);

//            vTaskDelay(xPeriodTicks);
        } else {
            ESP_LOGW(TAG, "fail to take mutex");
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

//    TaskHandle_t tcp_server_handle;
//    xTaskCreate(tcp_server_task, "tcp_server", 4096, (void *) AF_INET, 5, &tcp_server_handle);


}