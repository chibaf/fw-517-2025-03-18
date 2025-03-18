#!/usr/bin/python3
#
from datetime import date
import time
import matplotlib.pyplot as plt
import serial
import RPi.GPIO as GPIO
import os
import sys
#
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)  # heater
GPIO.setup(12, GPIO.OUT)  # core heater
GPIO.setup(13, GPIO.OUT)  # heater
GPIO.setup(15, GPIO.OUT)  # pump
GPIO.setup(18, GPIO.OUT)  # freezer
GPIO.setup(19, GPIO.OUT)  # bottom heater
#
from read_m5_class import m5logger
from readser_class import readser
#
today = date.today()
t = time.localtime()
current_time = time.strftime("_H%H_M%M_S%S", t)
fn = "ACS_LOG_" + str(today) + current_time + ".csv"
f = open(fn, 'w', encoding="utf-8")
start = time.time()
#
ldata0 = [0] * 10
ldata = [ldata0] * 10
ser1 = serial.Serial("/dev/ttyACM0", 9600)
ser2 = serial.Serial("/dev/ttyACM1", 9600)
ser3 = serial.Serial("/dev/ttyUSB0", 115200)
read_ser1 = readser()
read_ser2 = readser()
sport = m5logger()
#
data = [0] * 10
data02 = [0] * 3
data2 = [data02] * 10
data03 = [0] * 10
data3 = [data03] * 10
#
ssr18 = ""
f18 = 0
flg = 0
t1 = 5
t2 = 5
while True:
    try:
        ttime = time.time() - start
        if ttime < 0.001:
            ttime = 0.0
        if f18 == 0:
            ctime = ttime
            f18 = 1
        if flg == 0:
            stime = ttime
            flg = 1
        st = time.strftime("%Y %b %d %H:%M:%S", time.localtime())
        ss = str(time.time() - int(time.time()))
        rttime = round(ttime, 2)
        curr1 = read_ser1.read(ser1)
        curr2 = read_ser1.read(ser2)
        if curr1[0] == "CUR":
            cur = float(curr1[1])
        else:
            dcu = [float(curr1[1]), float(curr1[2]), float(curr1[3])]
        if curr2[0] == "DCU":
            dcu = [float(curr2[1]), float(curr2[2]), float(curr2[3])]
        else:
            cur = float(curr2[1])
        array2 = sport.read_logger(ser3)
        sum = 0.0
        for i in range(0, 10):
            sum += array2[i]
        # SSR 11,12,13,18
        # SSR 11,12,13 on:1sec,off:9sec
        # 20250310
        # SSR 11,13 on:1sec,off:9sec
        # SSR 12 on 8sec, off 2sec
        if sum == 0.0:
            continue
        # heater on/off
        if stime + 5 >= ttime:
            GPIO.output(11, 1)
            GPIO.output(13, 1)
            GPIO.output(19, 1)
        if stime + 10 >= ttime > stime + 5:
            GPIO.output(11, 0)
            GPIO.output(13, 0)
            GPIO.output(19, 0)
        if stime + 10 < ttime:
            flg = 0
        if float(array2[5]) > -15.0:  # freezer on/off
            if ttime <= ctime + 1500.0:
                ssr18 = "1"
                GPIO.output(18, 1)
            if ctime + 1500 <= ttime <= ctime + 1800:
                ssr18 = "0"
                GPIO.output(18, 0)
            if ctime + 1800 < ttime:
                f18 = 0
        else:
            ssr18 = "0"
            GPIO.output(18, 0)
        GPIO.output(15, 1)  # pump on
        ssr15 = "1"
        
        # Control ssr12 based on Tcore
        Tcore = float(array2[6])
        print()
#        print("Tcore: "+str(Tcore))
        if Tcore >= 5.0:
            GPIO.output(12, 0)  # Turn off ssr12
        else:
            GPIO.output(12, 1)  # Turn on ssr12
        
        ss = st + ss[1:5] + "," + str(rttime) + ","
        ss12 = ss
        ss = ss + str(cur) + ","
        for i in range(0, len(array2) - 1):
            ss = ss + str(array2[i]) + ","
        ss = ss + str(array2[len(array2) - 1])
        f.write(ss + "," + ssr18 + "\n")
        data.pop(-1)
        data2.pop(-1)
        data3.pop(-1)
        data.insert(0, cur)
        data2.insert(0, dcu)
        data3.insert(0, array2)
        rez2 = [[data2[j][i] for j in range(len(data2))] for i in range(len(data2[0]))]  # transposing a matrix
        rez3 = [[data3[j][i] for j in range(len(data3))] for i in range(len(data3[0]))]  # transposing a matrix
        #
        x = range(0, 10, 1)
        plt.figure(100)
        plt.clf()
        plt.ylim(-25, 30)
        tl = [0] * 10
        h3 = []
        for i in range(0, 10):
            tl[i], = plt.plot(x, rez3[i], label="T" + str(i))
        for i in range(0, 10):
            h3.append(tl[i])
        plt.legend(handles=h3)
        plt.pause(0.1)
        #
        plt.figure(200)
        plt.clf()
        plt.ylim(0, 400000)
        plt.plot(x, data)
        plt.pause(0.1)
        #
        plt.figure(300)
        plt.clf()
        plt.ylim(0, 150)
        tl = [0] * 3
        h2 = []
        for i in range(0, len(rez2)):
            tl[i], = plt.plot(x, rez2[i], label="C" + str(i))
        for i in range(0, len(rez2)):
            h2.append(tl[i])
        #plt.legend(handles(h2))
        #plt.pause(0.1)
    except KeyboardInterrupt:
        GPIO.output(11, False)
        GPIO.output(12, False)
        GPIO.output(18, False)
        GPIO.output(15, False)
        GPIO.output(13, False)
        f.close()
        ser1.close()
        ser2.close()
        ser3.close()
        exit()