#include "mpu6050.hpp"
#include "kalmanfilter.hpp"
#include "wifi.h"

#include "nvs_flash.h"

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <cmath>

static gpio_num_t i2c_gpio_sda = (gpio_num_t)15;
static gpio_num_t i2c_gpio_scl = (gpio_num_t)2;
#define I2C_NUM I2C_NUM_0


static void mpu6050_task(void *pvParameters) {
    MPU6050 mpu(i2c_gpio_scl, i2c_gpio_sda, I2C_NUM);

    if(!mpu.init()) {
	    ESP_LOGE("mpu6050", "init failed!");
        vTaskDelete(0);
    }
	ESP_LOGI("mpu6050", "init success!");

    float ax,ay,az,gx,gy,gz;
    float pitch, roll;
    float fpitch, froll;

    KALMAN pfilter(0.005);
    KALMAN rfilter(0.005);

    int count = 0;

    while(1) {
        ax = -mpu.getAccX();
        ay = -mpu.getAccY();
        az = -mpu.getAccZ();
        gx = mpu.getGyroX();
        gy = mpu.getGyroY();
        gz = mpu.getGyroZ();
        pitch = atan(ax/az)*57.2958;
        roll = atan(ay/az)*57.2958;
        fpitch = pfilter.filter(pitch, gy);
        froll = rfilter.filter(roll, -gx);
        count++;
        printf("Samples:%d ", count);
        count = 0;
        printf(" Acc:(%4.2f,%4.2f,%4.2f)", ax, ay, az);
        printf("Gyro:(%6.3f,%6.3f,%6.3f)", gx, gy, gz);
        printf(" Pitch:%6.3f ", pitch);
        printf(" Roll:%6.3f ", roll);
        printf(" FPitch:%6.3f ", fpitch);
        printf(" FRoll:%6.3f \n", froll);
        vTaskDelay(1);
    }

}

extern "C" void app_main()
{
    printf("app_main\n");

    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "ESP_WIFI_MODE_STA");
    wifi_init_sta();

    mpu6050_task((void *)"xx");
    xTaskCreatePinnedToCore(&mpu6050_task,"mpu6050_task",2048*2,NULL,5,NULL,0);
//     xTaskCreate(mpu6050_task, "mpu6050_task", 4096, NULL, 3, NULL);
}