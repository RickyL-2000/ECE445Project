import machine
from machine import I2C
from machine import Pin
from machine import sleep


record = []
action1 = 0
action2 = 0
action3 = 0

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
