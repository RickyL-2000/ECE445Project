#include "wifi.h"
#include "tcp_server.h"

#include "nvs_flash.h"

#include <esp_log.h>
#include <freertos/semphr.h>
#include <freertos/FreeRTOS.h>
#include <cmath>
#include <stdio.h>
#include <functional>


static const char *TAG = "light_main";

typedef struct ledCommend_t {
    int R;
    int G;
    int B;
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


typedef struct sharedData_t {
    SemaphoreHandle_t mutex;
    void *data_p;
} sharedData_t;


const TickType_t xPeriodTicks = 100 / portTICK_PERIOD_MS;


void tcp_server_task(void *pvParameters) {
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
                sscanf(output_buffer, "(%f, %f, %d, %d, %d)", &pitch, &roll, &(ledCommend.R), &(ledCommend.G),
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
    const TickType_t xPeriodTicks = 10 / portTICK_PERIOD_MS;

    float pitch, roll;
    ledCommend_t ledCommend;

    TickType_t xLastWakeTime;
    xLastWakeTime = xTaskGetTickCount();
    for(;;){
        xQueueReceive(commandQueues->servoQueue, &roll, 0);
        xQueueReceive(commandQueues->stepQueue, &pitch, 0);
        xQueueReceive(commandQueues->ledQueue, &ledCommend, 0);
        ESP_LOGI(TAG, "receive from command queue: %.2f, %.2f, %d,%d,%d", pitch, roll, ledCommend.R, ledCommend.G,
                 ledCommend.B);
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

    // used for sharing data, but queue always copy, so un-used
//    auto *mpuData = (struct mpuData_t *) malloc(sizeof(struct mpuData_t));
//    auto *sharedMpuData = (sharedData_t *) malloc(sizeof(sharedData_t));
//    sharedMpuData->mutex = xSemaphoreCreateMutex();
//    sharedMpuData->data_p = (void *const) mpuData;


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

}