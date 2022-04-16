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

# def server_test():
#     def recv(msg):
#         log.info(msg)
    
#     local_host = network.WLAN(network.STA_IF).ifconfig()[0]  # 获取IP地址
#     c = Channel("esp_server")
#     c.becomeServer(local_host,LIGHT_PORT,recv)
#     c.listen()

# def client_test():
#     c = Channel("esp_client")
#     c.becomeClient(PC_IP,DYNAMICS_PORT)
#     while True:
#         time.sleep(random.random())
#         c.send((random.random()*360,
#                         random.random()*360,
#                         random.random()*360))


# blink_connect()
# sleep(1)
# # server_test()
# client_test()



from machine import I2C
from machine import Pin
import drivers.mpu6050 as mpu6050

i2c = I2C(scl=Pin(2), sda=Pin(15))     #initializing the I2C method for ESP32
#i2c = I2C(scl=Pin(5), sda=Pin(4))       #initializing the I2C method for ESP8266
mpu= mpu6050.accel(i2c)

if __name__ == '__main__':
    xmin = float("inf")
    xmax = -float("inf")
    ymin = float("inf")
    ymax = -float("inf")
    zmin = float("inf")
    zmax = -float("inf")
    while True:
        vals = mpu.get_values()
        time.sleep(0.1)
        print([vals["AcX"],vals["AcY"],vals["AcZ"]])

        # x = vals["AcX"]
        # y = vals["AcY"]
        # z = vals["AcZ"]
        # R = (x**2+y**2+z**2)

        # xmin = min(x,xmin)
        # xmax = max(x,xmax)
        # ymin = min(y,ymin)
        # ymax = max(y,ymax)
        # zmin = min(z,zmin)
        # zmax = max(z,zmax)



        # print(xmin, xmax, ymin, ymax, zmin, zmax, R)

