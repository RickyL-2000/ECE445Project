# Complete project details at https://RandomNerdTutorials.com

from machine import Pin
from time import sleep

led = Pin(2, Pin.OUT)

def run():
    led = Pin(2, Pin.OUT)

    while True:
        led.value(not led.value())
        sleep(0.5)


def blink_sec(interval: float, blink_num: int):
    for i in range(blink_num):
        led.value(not led.value())
        sleep(interval)

def led_on(sec:float):
    led.value(True)
    sleep(sec)
    led.value(False)

def led_off():
    led.value(False)
