//
// Created by 51284 on 2022/4/22.
//

#include "tcp_client.hpp"

TcpClient::TcpClient() {
    sock = 0;
    addr_family = 0;
    ip_protocol = 0;
    connected = false;
    connect();
}

TcpClient::~TcpClient() {
    ESP_LOGE(TAG, "Shutting down socket and restarting...");
    shutdown(sock, 0);
    close(sock);
}

int TcpClient::connect() {
    // The connected flag must be false when call the connect method.
    assert(connected == false);
    if (0!=sock){
        int err;
//        err = shutdown(sock,0);
        err = closesocket(sock);
        if (err<0){
            ESP_LOGE(TAG, "Failed to close socket: errno %d", errno);
        }
    }
    
    struct sockaddr_in dest_addr = {
            .sin_family = AF_INET,
            .sin_port = htons(PORT),
            .sin_addr = {
                    .s_addr = inet_addr(host_ip),
            }
    };
    addr_family = AF_INET;
    ip_protocol = IPPROTO_IP;

    sock = socket(addr_family, SOCK_STREAM, ip_protocol);
    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
        return errno;
    }
    ESP_LOGI(TAG, "Socket created, connecting to %s:%d", host_ip, PORT);

    int err = ::connect(sock, (struct sockaddr *) &dest_addr, sizeof(struct sockaddr_in6));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to connect: errno %d", errno);
        return errno;
    }
    connected = true;
    ESP_LOGI(TAG, "Successfully connected");
    return ESP_OK;
}

int TcpClient::send(char *msg) {
    if(!connected){
        return ESP_FAIL;
    }
    unsigned long slen = strlen(msg);
    ESP_LOGD(TAG,"Send slen:%lu",slen);
    if (::send(sock,&slen,4,0) < 0) {
        connected = false;
        ESP_LOGE(TAG, "Error occurred during sending slen: errno %d", errno);
//        vTaskDelay(1000/portTICK_PERIOD_MS);
        connect();
        return errno;
    }

    ESP_LOGD(TAG,"Send msg:%s",msg);
    if (::send(sock, msg, slen, 0) < 0) {
        connected = false;
        ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
//        vTaskDelay(1000/portTICK_PERIOD_MS);
        connect();
        return errno;
    }
    return ESP_OK;
}
