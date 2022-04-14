from time import sleep
from utils.wifi import blink_connect
import utils.log as log
# from utils.uart import uart_loopback
from utils.channel import Channel
from utils.config import PC_IP, DYNAMICS_PORT, LIGHT_PORT
import network
import time
import random

print("start")

def server_test():
    def recv(msg):
        log.info(msg)
    
    local_host = network.WLAN(network.STA_IF).ifconfig()[0]  # 获取IP地址
    c = Channel("esp_server")
    c.becomeServer(local_host,LIGHT_PORT,recv)
    c.listen()

def client_test():
    c = Channel("esp_client")
    c.becomeClient(PC_IP,DYNAMICS_PORT)
    while True:
        time.sleep(random.random())
        c.send((random.random()*360,
                        random.random()*360,
                        random.random()*360))


blink_connect()
sleep(1)
# server_test()
client_test()
