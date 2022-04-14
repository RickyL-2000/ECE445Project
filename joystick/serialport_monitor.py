'''
Author: your name
Date: 2022-04-14 23:59:41
LastEditTime: 2022-04-14 23:59:41
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: \ECE445Project\joystick\serialport_monitor.py
'''
#-*-coding:utf-8 -*-
import imp
import os
import sys
import time
import signal
import string
import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import re
import math

i = 0
q_mag_x = Queue(maxsize=0)
q_mag_y = Queue(maxsize=0)
q_mag_z = Queue(maxsize=0)
curve_num = 0

X_ACCEL_OFFSET = 0
Y_ACCEL_OFFSET = 0
Z_ACCEL_OFFSET = 3200
X_GYRO_OFFSET = -100
Y_GYRO_OFFSET = 70
Z_GYRO_OFFSET = 150

R = 0.1**2
A = 1
H = 1
Q = 10**(-6)
def kalmenfilter(s, hat, P, hatminus, Pminus, K):
    # time update
    hatminus.append(A*hat[-1])
    Pminus.append(A*P[-1]+Q)

    # measurement update
    K.append(Pminus[-1]/(Pminus[-1]+R))
    hat.append(hatminus[-1]+K[-1]*(s-H*hatminus[-1]))
    P.append((1-K[-1]*H)*Pminus[-1])
    return hat, P, hatminus, Pminus, K

def Serial():
    from h import v
    global i
    global q_mag_x 
    global q_mag_y
    global q_mag_z
    ret = b''
    while(True):
        n = mSerial.inWaiting()
        if(n):
            ret = mSerial.readline()
            # print(ret)
            if len(ret):
                data_get = ret.decode('UTF-8')
                pattern = re.compile(r"[+-]?\d+(?:\.\d+)?")   # find the num
                data_all = pattern.findall(data_get)
                print(data_all)
                for j in range(len(data_all)):
                    if j==5:
                        v.xhat, v.Px, v.xhatminus, v.Pxminus, v.Kx = kalmenfilter(float(data_all[j])+X_ACCEL_OFFSET, v.xhat, v.Px, v.xhatminus, v.Pxminus, v.Kx)
                        ACCEL_XOUT_H = min(v.xhat[-1],16384)
                        ACCEL_XOUT_H = max(ACCEL_XOUT_H,-16384)
                        X_Angle = math.acos(ACCEL_XOUT_H/16384) * 57.29577
                        q_mag_x.put(X_Angle)
                    if j==6:
                        v.yhat, v.Py, v.yhatminus, v.Pyminus, v.Ky = kalmenfilter(float(data_all[j])+Y_ACCEL_OFFSET, v.yhat, v.Py, v.yhatminus, v.Pyminus, v.Ky)
                        ACCEL_YOUT_H = min(v.yhat[-1],16384)
                        ACCEL_YOUT_H = max(ACCEL_YOUT_H,-16384)
                        Y_Angle = math.acos(ACCEL_YOUT_H/16384) * 57.29577
                        q_mag_y.put(Y_Angle)
                    if j==4:
                        v.zhat, v.Pz, v.zhatminus, v.Pzminus, v.Kz = kalmenfilter(float(data_all[j])+Z_ACCEL_OFFSET, v.zhat, v.Pz, v.zhatminus, v.Pzminus, v.Kz)
                        ACCEL_ZOUT_H = min(v.zhat[-1],16384)
                        ACCEL_ZOUT_H = max(ACCEL_ZOUT_H,-16384)
                        Z_Angle = math.acos(ACCEL_ZOUT_H/16384) * 57.29577
                        q_mag_z.put(Z_Angle)

def plotData():
    global i
    if i < historyLength:
        data_x[i] = q_mag_x.get()
        if curve_num >= 2:
            data_y[i] = q_mag_y.get()
        if curve_num >= 3:
            data_z[i] = q_mag_z.get()
        i = i+1
    else:
        data_x[:-1] = data_x[1:]
        data_x[i-1] = q_mag_x.get()
        if curve_num >= 2:
            data_y[:-1] = data_y[1:]
            data_y[i-1] = q_mag_y.get()
        if curve_num >= 3:
            data_z[:-1] = data_z[1:]
            data_z[i-1] = q_mag_z.get()

    curve1.setData(data_x)
    curve2.setData(data_y)
    curve3.setData(data_z)

def sig_handler(signum, frame):
    sys.exit(0)

if __name__ == "__main__":
    curve_num = 3
    
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    app = pg.mkQApp()           # App Setup
    win = pg.GraphicsWindow()   # Window Setup
    win.setWindowTitle(u'pyqtgraph chart tool')
    win.resize(900, 600)        #window size
    data_x = array.array('i')
    data_y = array.array('i')
    data_z = array.array('i')
    historyLength = 320 

    data_x = np.zeros(historyLength).__array__('d')
    data_y = np.zeros(historyLength).__array__('d')
    data_z = np.zeros(historyLength).__array__('d')
    p = win.addPlot() 
    p.showGrid(x=True, y=True)
    p.setRange(xRange=[0, historyLength], yRange=[-180, 180], padding=0)
    p.setLabel(axis='left',     text='y-mag')
    p.setLabel(axis='bottom',   text='x-time')
    p.setTitle('Serial Chart')
    curve1 = p.plot(data_x, pen='r')
    curve2 = p.plot(data_y, pen='g')
    curve3 = p.plot(data_z, pen='b')
    
    portx = 'COM9'
    bps = 115200
    mSerial = serial.Serial(portx, int(bps))
    if (mSerial.isOpen()):
        print("open success")
        mSerial.flushInput()
    else:
        print("open failed")
        serial.close()
    
    #Serial data receive thread
    th1 = threading.Thread(target=Serial)
    th1.setDaemon(True)
    th1.start()
    
    #plot timer define
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData)
    timer.start(10)
    app.exec_()
