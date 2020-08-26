#!/usr/bin/env python3
'''
Find the manual here: http://10.149.10.106/twiki-plac/bin/view/PixelLab/SMT32MicroController
'''
# from __future__ import print_function
import serial, time, os, sys
from datetime import datetime, timedelta
import logging

dSuffix = 'project_'
usage_str = f"Usage: {sys.argv[0]} type value\n\ttype: \t1 digit. 1->Motor; 2->Temperature\n\tvalue: \t3 digits. Meaningless for type=2, but should be provided."

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

    def connect(self, portx="/dev/ttyUSB1"):
        portx=portx
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

    def run(self):
        send_data = sys.argv[1] + sys.argv[2] + '\r\n'
        self.connect()

        if sys.argv[1] == '1':
            self.set_M(int(sys.argv[2]))
        elif sys.argv[1] == '2':
            T = self.get_T()
            print(f"T: {T}")
        else:
            print("Unknown option!!!!")
            print(usage_str)

        self.disconnect()

    def get_T(self):
        data = '-999'
        self.send('2010')
        time.sleep(1)
        if self.ser.in_waiting:
            data = self.ser.read(self.ser.in_waiting).decode('gbk')
        return data

    def set_M(self, v=0):
        data = '-999'
        self.send(f'1{v:03d}')

    def test(self):
        print(self.get_T())

def test():
    is1 = STM32()
    is1.test()

def record_T(outfname='test_T.dat'):
    is1 = STM32()
    is1.connect()
    with open(outfname,'w') as fout1:
        fout1.write("idx/I:time/C:T/F")
        idx = 0
        while True:
            try:
                t0 = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
                T = is1.get_T()
                info = f"\n{idx:d} {t0} {T}"
                print(info)
                fout1.write(info)
                time.sleep(5)

                idx += 1
                if idx%10 == 9: fout1.flush()
            except KeyboardInterrupt:
                break
    is1.disconnect()


def loopAlpha():
    is1 = STM32()
    is1.connect()
    degree1=0
    degree2=90
    sleeptime=33.2
    command=degree1
    while True:
        try:
            is1.set_M(int(command))
            print(command)
            if command==degree1: command=degree2
            elif command==degree2: command=degree1
            time.sleep(sleeptime)
        except KeyboardInterrupt:
            break
    is1.disconnect()


def main():
    if len(sys.argv)<3:
        print(usage_str)
        return

    is1 = STM32()
    is1.run()
    return

if __name__ == '__main__':
#     listPorts()
#     main()
#     record_T()
   loopAlpha()
