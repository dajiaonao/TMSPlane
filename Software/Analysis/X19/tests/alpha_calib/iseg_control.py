#!/usr/bin/env python3
# from __future__ import print_function
import serial
import time
import os
from datetime import datetime, timedelta
import logging

dSuffix = 'project_'

def listPorts():
    import serial.tools.list_ports
    port_list = list(serial.tools.list_ports.comports())
    print(port_list)
    if len(port_list) == 0:
        print('No port avaliable')
    else:
        for i in range(0,len(port_list)):
            print(port_list[i])


def vGen(vList):
    n = len(vList)
    i = 0
    while True:
        yield vList[i]
        i += 1
        if i==n: i-=n

class isegHV:
    def __init__(self):
        self.ser = None
    def connect(self):
        portx="/dev/ttyUSB1"
#         portx="/dev/ttyUSB0"
        bps=9600
        timex=5
        self.ser=serial.Serial(portx,bps,timeout=timex)

    def send(self, msg, log_cmd=True):
        if log_cmd: logging.info(msg.rstrip())
        if msg[-2:] != '\r\n': msg+='\r\n'
        return self.ser.write(msg.encode("UTF-8"))

    def query(self, cmd, L=1024):
        self.send(cmd, False)
        return self.recv_all(L).decode();

    def recv_all(self, L=1024):
        ret1 = self.ser.read(L)
        while ret1[-2:] != b'\r\n': ret1 += self.ser.read(L)
        return ret1.rstrip()

    def test0(self):
        self.connect()
        print(self.query('*IDN?'))

    def test1(self):
        self.connect()
        print(self.query(':READ:VOLTage?'))

    def test(self):
        self.connect()
        print(self.query('*IDN?'))

#         self.send('*RST')
#         self.test1()
#         self.send("FUNC 'CURR'")
#         self.speed_check()
#         self.read_many()
#         self.run_measure()
#         self.take_data()
#         self.run_measure1()
#         self.test_get_mean()
#         self.multiple_reading()
#         self.set_relative()
        self.ser.close()

def test1():
    is1 = isegHV()
#     is1.test0()
    is1.test1()
#     is1.test()

def test2():
    p = vGen([50, 100, 20, 120, 70, 10, 80, 30, 90, 40, 110, 60])

    for i in range(50):
        print(i, next(p))

    t = datetime.now()
    t2 = time.time()
    dT = timedelta(minutes=15)
    tN = t+dT
    print(t,t2,tN)

    

if __name__ == '__main__':
#     listPorts()
    test1()
#     test2()
