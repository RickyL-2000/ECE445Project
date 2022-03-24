from machine import UART
from machine import Timer
import time

# 创建一个UART对象，将13管脚和12管脚相连
# 为什么不适用UART1 默认的管脚？ 亲测在默认的 9，10号管脚下存在发送会触发重启的bug

uart = UART(1, rx=13, tx=12)
# 创建一个Timer，使用timer的中断来轮询串口是否有可读数据
timer = Timer(1)
timer.init(period=50, mode=Timer.PERIODIC, callback=lambda t: read_uart(uart))


def read_uart(uart=uart):
    if uart.any():
        uart.read()
        # print('received: ' + uart.read().decode())


def uart_loopback(period=50):
    try:
        while True:
            msg = input('send: ')
            uart.write(msg.encode("utf-8"))
            print(msg.encode("utf-8"))
            time.sleep_ms(50)
    except Exception as e:
        print(e)
    finally:
        # timer.deinit()
        pass


def send_msg(msg, period=50):
    # uart = UART(1, rx=13, tx=12)
    global uart
    uart.write(msg)


def sender(period=50):
    # uart = UART(1, rx=13, tx=12)
    global uart
    while True:
        uart.write(input("send by uart: \t"))
        time.sleep_ms(period)


def recieve_msg(period=50):
    # uart = UART(1, rx=13, tx=12)
    global uart
    time.sleep(5)
    if uart.any():
        return uart.read().decode()


def reciever(period=50):
    # uart = UART(1, rx=13, tx=12)
    global uart
    time.sleep(5)
    if uart.any():
        return uart.read().decode()

    # USAGE: register as a interrupt handler
    # timer = Timer(1)
    # timer.init(period=period, mode=Timer.PERIODIC,
    #            callback=lambda t: uart_utils.reciever())
