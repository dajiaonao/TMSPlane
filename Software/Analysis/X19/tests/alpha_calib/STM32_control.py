#!/usr/bin/env python3
'''
Find the manual here: https://iseg-hv.com/files/media/HPx-LPx_300-800W_eng.pdf
'''
# from __future__ import print_function
import serial
import time
import os
import sys
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

class STM32:
    def __init__(self):
        self.ser = None
    def connect(self):
        portx="/dev/ttyUSB2"
        bps=9600
        timex=5
        self.ser=serial.Serial(portx,bps,timeout=timex)
    def disconnect(self):
        print("disconnecting...")
        self.ser.close()

    def send(self, msg, log_cmd=True):
        if log_cmd: logging.info(msg.rstrip())
        if msg[-2:] != '\r\n': msg+='\r\n'
        return self.ser.write(msg.encode("UTF-8"))

    def query(self, cmd, L=1024):
        self.send(cmd, False)
        return self.recv_all(L);
#         return self.recv_all(L).decode();

    def recv_all(self, L=1024):
        ret1 = self.ser.read(L)
        while ret1[-2:] != b'\r\n': ret1 += self.ser.read(L)
        return ret1.rstrip()

    def test1(self):
        send_data = sys.argv[1] + sys.argv[2] + '\r\n'
        print(send_data)
        self.connect()
        q = self.query(send_data)
        print(q.decode('gbk'))
        self.disconnect()

def test1():
    is1 = STM32()
    is1.test1()

def main():
    usage_str = f"Usage: {sys.argv[0]} type value\n\ttype: \t1 digit. 1->Motor; 2->Temperature\n\tvalue: \t3 digits. Meaningless for type=2, but should be provided."
    if len(sys.argv)<3:
        print(usage_str)
        return

    is1 = STM32()
    is1.test1()
    return


if __name__ == '__main__':
#     listPorts()
    main()
#     test1()
