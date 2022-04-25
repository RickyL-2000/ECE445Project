//
// Created by 51284 on 2022/4/22.
//

#include "tcp_client.hpp"

TcpClient::TcpClient() {
    tcpClientMsgQueue = xQueueCreate(10, sizeof(msgWarp_t));
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
    if (connected) {
        if (shutdown(sock, 0) < 0) {
            ESP_LOGE(TAG, "Failed to shutdown socket: errno %d", errno);
        }
        if (closesocket(sock) < 0) {
            ESP_LOGE(TAG, "Failed to close socket: errno %d", errno);
        }
        connected = false;
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
    ESP_LOGI(TAG, "Socket created, try to connect to %s:%d", host_ip, PORT);

    int err = ::connect(sock, (struct sockaddr *) &dest_addr, sizeof(struct sockaddr_in6));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to connect: errno %d", errno);
        return errno;
    }
    connected = true;
    ESP_LOGI(TAG, "Successfully connected");
    return ESP_OK;
}

static void daemonSendService(void *pvParameter) {
    char TAG[] = "tcp_client_daemon_send";
    msgWarp_t *msgWarp;

    for (;;) {
        if (xQueueReceive(TcpClient::tcpClientMsgQueue, msgWarp, 100 / portTICK_PERIOD_MS) != pdPASS) {
            ESP_LOGI(TAG, "msgWarp addr:%p, msgWarp.slen addr:%p, ", msgWarp, &(msgWarp->slen));

            ESP_LOGI(TAG, "Send slen:%lu", msgWarp->slen);
            if (::send(msgWarp->sock, &(msgWarp->slen), 4, 0) < 0) {
                ESP_LOGE(TAG, "Error occurred during sending slen: errno %d", errno);
                vTaskDelete(nullptr);
            }

            ESP_LOGI(TAG, "Send msg:%s", msgWarp->msg);
            if (::send(msgWarp->sock, &(msgWarp->msg), msgWarp->slen, 0) < 0) {
                ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
                vTaskDelete(nullptr);
            }
        }
    }
    vTaskDelete(nullptr);
}

void TcpClient::send(char *msg) {
    ESP_LOGI(TAG, "to %d: %s", sock, msg);
    auto *msgWarp_p = (struct msgWarp_t *) malloc(sizeof(msgWarp_t));
    msgWarp_p->slen = (unsigned long) strlen(msg);
    msgWarp_p->msg = msg;
    msgWarp_p->sock = sock;

    ESP_LOGI(TAG, "strlen:%d, msgWarp_p.slen:%lu, sock:%d, msgWarp_p.sock:%d, ", (int) strlen(msg), msgWarp_p->slen, sock,
             msgWarp_p->sock);
    ESP_LOGI(TAG, "msgWarp_p addr:%p, msgWarp_p.slen addr:%p, ", &msgWarp_p, &(msgWarp_p->slen));

    xQueueSend(tcpClientMsgQueue, msgWarp_p,100/portTICK_PERIOD_MS);

}