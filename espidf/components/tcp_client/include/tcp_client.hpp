//
// Created by 51284 on 2022/4/22.
//

#ifndef JOYSTICK_MYTCP_CLIENT_HPP
#define JOYSTICK_MYTCP_CLIENT_HPP

#include <string.h>
#include <sys/param.h>

#include "freertos/queue.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "lwip/err.h"
#include "lwip/sockets.h"

#define HOST_IP_ADDR "192.168.31.177"

#define PORT 12345

struct msgWarp_t{
    unsigned long slen;
    char* msg;
    int sock;
};

class TcpClient {
private:
    int sock;
    bool connected;
    static constexpr const char *host_ip = HOST_IP_ADDR;
    int addr_family;
    int ip_protocol;
    static constexpr const char *TAG = "tcp_client";

public:
    static QueueHandle_t tcpClientMsgQueue;

    TcpClient();

    int connect();

    void send(char *msg);

    ~TcpClient();
};

#endif //JOYSTICK_MYTCP_CLIENT_HPP
