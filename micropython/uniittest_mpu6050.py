'''
Author: your name
Date: 2022-04-14 23:59:41
LastEditTime: 2022-04-14 23:59:41
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: \ECE445Project\joystick\serialport_monitor.py
'''
#-*-coding:utf-8 -*-
# import imp
# import os
# import sys
# import time
# import signal
# import string
# import pyqtgraph as pg
# import array
import serial
import threading
import numpy as np
from queue import Queue
import re
import math
import json

X_ACCEL_OFFSET = 0
Y_ACCEL_OFFSET = 0
Z_ACCEL_OFFSET = 3200
X_GYRO_OFFSET = -100
Y_GYRO_OFFSET = 70
Z_GYRO_OFFSET = 150

def Serial():
    ret = b''
    while(True):
        if mSerial.inWaiting():
            try:
                ret = mSerial.readline()
                if len(ret):
                    # print(ret.decode('UTF-8'))
                    data_get = json.loads(ret.decode('UTF-8').strip())
                    # print(data_get)
                    
                    # x_angle = math.acos(max(min(int(data_all[5]),32768),-32768)/32768) * 57.29577
                    # y_angle = math.acos(max(min(int(data_all[6]),32768),-32768)/32768) * 57.29577
                    # z_angle = math.acos(max(min(int(data_all[4]),32768),-32768)/32768) * 57.29577
                    
                    ax = int(data_get[0])
                    ay = int(data_get[1])
                    az = int(data_get[2])

                    pitch = math.atan(ax/az)*57.2958
                    roll = math.atan(ay/az)*57.2958

                    print(f"pitch:{pitch:>5.1f}, roll:{roll:>5.1f}")
            except Exception as e:
                print(e)
                continue

if __name__ == "__main__":
    portx = 'COM5'
    bps = 115200
    mSerial = serial.Serial(portx, int(bps))
    if (mSerial.isOpen()):
        print("open success")
        mSerial.flushInput()
    else:
        print("open failed")
        serial.close()
    
    #Serial data receive thread
    th1 = threading.Thread(target=Serial, daemon=True)
    th1.start()

    th1.join()