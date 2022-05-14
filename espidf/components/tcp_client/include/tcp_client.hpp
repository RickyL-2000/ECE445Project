//
// Created by 51284 on 2022/4/22.
//

#ifndef JOYSTICK_MYTCP_CLIENT_HPP
#define JOYSTICK_MYTCP_CLIENT_HPP

#include <string.h>
#include <sys/param.h>
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


//#define HOST_IP_ADDR "192.168.31.245" // COM10 light
 #define HOST_IP_ADDR "192.168.31.177" // HAOZHE-XIAOXIN central server
//#define HOST_IP_ADDR "192.168.43.136"

#define PORT 8880

class TcpClient {
private:
    int sock;
    static constexpr const char *host_ip = HOST_IP_ADDR;
    int addr_family;
    int ip_protocol;
    static constexpr const char *TAG = "tcp_client";
    bool connected;
public:
    TcpClient();

    int connect();

    int send(char *msg);

    ~TcpClient();
};

#endif //JOYSTICK_MYTCP_CLIENT_HPP
