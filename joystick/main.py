'''
Author: Zhaohua Yang
Date: 2022-03-24 13:58:42
LastEditTime: 2022-04-14 23:21:52
LastEditors: Please set LastEditors
Description: Button control
FilePath: \ECE445Project\joystick\main.py
'''
import machine
from machine import I2C
from machine import Pin
from machine import sleep
import mpu6050
from threading import Thread
i2c = I2C(scl=Pin(22), sda=Pin(21))     #initializing the I2C method for ESP32
#i2c = I2C(scl=Pin(5), sda=Pin(4))       #initializing the I2C method for ESP8266
mpu= mpu6050.accel(i2c)
def check_button1():
    global action1
    action1 = 0
    p4 = machine.Pin(4,machine.Pin.OUT)
    previous = 0
    while True:
        current = p4.get_values()
        if (previous==0 and current==1):
            sleep(10)
            current = p4.get_values()
            action1 = 1      
        previous = current

def check_button2():
    global action2
    action2 = 0
    p5 = machine.Pin(5,machine.Pin.OUT)
    previous = 0
    while True:
        current = p5.get_values()
        if (previous==0 and current==1):
            sleep(10)
            current = p5.get_values() 
            action2 = 1
        previous = current

def check_button3():
    global action3
    action3 = 0
    p6 = machine.Pin(6,machine.Pin.OUT)
    previous = 0
    while True:
        current = p6.get_values()
        if (previous==0 and current==1):
            sleep(10)
            current = p6.get_values()   
            action3 = 1     
        previous = current

if __name__ == '__main__':
    t1 = Thread(target=check_button1)
    t2 = Thread(target=check_button2)
    t3 = Thread(target=check_button3)
    t1.start()
    t2.start()
    t3.start()
    record = []
    action1 = 0
    action2 = 0
    action3 = 0
    while True:
        values = mpu.get_values()
        print(values)
        sleep(500)
        if action1:
            action1 = 1
            action2 = 0
            action3 = 0
        if action2:
            action2 = 1
        if action3:
            action3 = 1
        if action1==1 and action2==0 and action3==0:
            record.append(values)
        if action1==1 and action2==1 and action3==0:
            pass
        if action1==1 and action2==1 and action3==1:
            break

