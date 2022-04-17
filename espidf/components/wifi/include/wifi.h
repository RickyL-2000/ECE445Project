
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"

#include "lwip/err.h"
#include "lwip/sys.h"

static const char *TAG = "wifi station";

#ifdef __cplusplus
extern "C" void wifi_init_sta(void);
#else
void wifi_init_sta(void);
#endif


