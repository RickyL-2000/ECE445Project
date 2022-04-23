//
// Created by 51284 on 2022/4/21.
//

#include "tcp_server.h"

static const char *TAG = "tcp_server";

static void do_retransmit(const int sock)
{
    int len;
    unsigned long slen;
    char output_buffer[BUFFER_SIZE];
    int buffer_size = BUFFER_SIZE;

    do {
        len = recv(sock, &slen, sizeof(slen), 0);
        if (len < 0) {
            ESP_LOGE(TAG, "Error occurred during receiving slen: errno %d", errno);
        } else if (len == 0) {
            ESP_LOGW(TAG, "Connection closed during receiving slen");
        } else {

            if (slen > buffer_size){
                ESP_LOGE(TAG, "slen: %lu is larger than buffer size, this pack is dropped!", slen);
                while (slen>0){
                    // read all the current pack from socket buffer, avoiding influence the next pack
                    len = recv(sock, output_buffer, slen>buffer_size?buffer_size:slen, 0);
                    slen -= len;
                }
                continue;
            }
            len = recv(sock, output_buffer, slen, 0);
            if (len < 0) {
                ESP_LOGE(TAG, "Error occurred during receiving: errno %d", errno);
            } else if (len == 0) {
                ESP_LOGW(TAG, "Connection closed");
            } else {
                output_buffer[slen] = 0; // Null-terminate whatever is received and treat it like a string
                ESP_LOGI(TAG, "Received %d bytes: %s", len, output_buffer);
            }
            
        }
    } while (len > 0);
}

void tcp_server_task(void *pvParameters)
{
    char addr_str[128];
    int addr_family = (int)pvParameters;
    int ip_protocol = 0;
    int keepAlive = 1;
    int keepIdle = KEEPALIVE_IDLE;
    int keepInterval = KEEPALIVE_INTERVAL;
    int keepCount = KEEPALIVE_COUNT;
    struct sockaddr_storage dest_addr;

    if (addr_family == AF_INET) {
        struct sockaddr_in *dest_addr_ip4 = (struct sockaddr_in *)&dest_addr;
        dest_addr_ip4->sin_addr.s_addr = htonl(INADDR_ANY);
        dest_addr_ip4->sin_family = AF_INET;
        dest_addr_ip4->sin_port = htons(PORT);
        ip_protocol = IPPROTO_IP;
    }

    int listen_sock = socket(addr_family, SOCK_STREAM, ip_protocol);
    if (listen_sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
        vTaskDelete(NULL);
        return;
    }
    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    ESP_LOGI(TAG, "Socket created");

    int err = bind(listen_sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to bind: errno %d", errno);
        ESP_LOGE(TAG, "IPPROTO: %d", addr_family);
        goto CLEAN_UP;
    }
    ESP_LOGI(TAG, "Socket bound, port %d", PORT);

    err = listen(listen_sock, 1);
    if (err != 0) {
        ESP_LOGE(TAG, "Error occurred during listen: errno %d", errno);
        goto CLEAN_UP;
    }

    while (1) {

        ESP_LOGI(TAG, "Socket listening");

        struct sockaddr_storage source_addr; // Large enough for both IPv4 or IPv6
        socklen_t addr_len = sizeof(source_addr);
        int sock = accept(listen_sock, (struct sockaddr *)&source_addr, &addr_len);
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
            inet_ntoa_r(((struct sockaddr_in *)&source_addr)->sin_addr, addr_str, sizeof(addr_str) - 1);
        }

        ESP_LOGI(TAG, "Socket accepted ip address: %s", addr_str);

        do_retransmit(sock);

        shutdown(sock, 0);
        close(sock);
    }

    CLEAN_UP:
    close(listen_sock);
    vTaskDelete(NULL);
}
//
//void app_main(void)
//{
//    ESP_ERROR_CHECK(nvs_flash_init());
//    ESP_ERROR_CHECK(esp_netif_init());
//    ESP_ERROR_CHECK(esp_event_loop_create_default());
//
//    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
//     * Read "Establishing Wi-Fi or Ethernet Connection" section in
//     * examples/protocols/README.md for more information about this function.
//     */
//    ESP_ERROR_CHECK(example_connect());
//
//#ifdef CONFIG_EXAMPLE_IPV4
//    xTaskCreate(tcp_server_task, "tcp_server", 4096, (void*)AF_INET, 5, NULL);
//#endif
//#ifdef CONFIG_EXAMPLE_IPV6
//    xTaskCreate(tcp_server_task, "tcp_server", 4096, (void*)AF_INET6, 5, NULL);
//#endif
//}
