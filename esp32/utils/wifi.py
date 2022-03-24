# import module
import time
import log
import blink
import network

# WIFI_SSID = "RICKY"
# PASSWD = "RICKY2000"
# WIFI_SSID = "nichousha"
# PASSWD = "chounizadi"
WIFI_SSID = "HAOZHE-Mi10S"
PASSWD = "411411411"

wifi = network.WLAN(network.STA_IF)


def blink_connect():
    blink.blink_sec(0.1, 10)

    wifi.active(1)

    log.info("wifi scan:\n{}".format("\n".join([str(x) for x in wifi.scan()])))

    start = time.time_ns()
    wifi.connect(WIFI_SSID, PASSWD)

    # time.sleep(3)
    # log.info("wifi.active: {}".format(wifi.active()))
    for i in range(5):
        log.info("[{}ns] wifi.ifconfig: {}".format(time.time_ns() - start,
                                                   wifi.ifconfig()))
        # log.info("wifi.active: {}".format(wifi.active()))
        time.sleep_ms(1000)

    if wifi.isconnected():
        log.success("wifi.isconnected: {}".format(wifi.isconnected()))
        blink.led_on(5)
    else:
        log.error("wifi.isconnected: {}".format(wifi.isconnected()))
        blink.blink_sec(1, 5)
        blink.led_off()
    return