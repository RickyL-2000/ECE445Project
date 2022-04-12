from time import sleep
from utils.wifi import blink_connect
import utils.log as log
# from utils.uart import uart_loopback
from utils.channel import Channel
from utils.config import ESP_IP, PC_IP, BOARDCAST_IP, PORT
import network

print("start")

def server_test():
    def recv(msg):
        log.info(msg)
    
    local_host = network.WLAN(network.STA_IF).ifconfig()[0]  # 获取IP地址
    c = Channel("esp_server")
    c.becomeServer(local_host,PORT,recv)
    c.listen()

def client_test():
    c = Channel("esp_client")
    c.becomeClient(PC_IP,PORT)
    for i in range(10):
        c.send("msg"+str(i))


blink_connect()
sleep(1)
server_test()
# client_test()
