#!/usr/bin/env python3
'''
Find the manual here: http://10.149.10.106/twiki-plac/bin/view/PixelLab/SMT32MicroController
'''
# from __future__ import print_function
import serial, time, os, sys
from datetime import datetime, timedelta
from multiprocessing import Process, Lock
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
        self.T_dt = 5
        self.M_dt = 33.2
        self.T_outfname = 'temp_testT.dat'
        self.ON = True
        self.debug = False

    def connect(self, portx="/dev/ttyUSB0"):
        portx=portx
        bps=9600
        timex=5
        self.ser=serial.Serial(portx,bps,timeout=timex)

    def disconnect(self):
        print("disconnecting...")
        self.ser.close()

    def send(self, msg):
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
        time.sleep(0.1)
        if self.ser.in_waiting:
            data = self.ser.read(self.ser.in_waiting).decode('gbk')
        else:
            print(self.ser.in_waiting)

        fs = data.split('\r\n')
        print(fs)
        if len(fs)>1:
            data = fs[-1]
        return data

    def set_M(self, v=0):
        data = '-999'
        self.send(f'1{v:03d}')

    def test(self):
        print(self.get_T())

class TemperatureMonitor:
    def __init__(self, savename, on=180, off=10):
        self.savename = savename
        self.instr = STM32()
        self.instr.connect()
        self.OnPosition = on
        self.OffPosition = off

        self.fout1 = open(self.savename,'w')
        self.fout1.write("idx/I:time/C:T/F")
        self.idx = 0
        self.instr.set_M(self.OffPosition)

    def measure(self, timestamp=None):
        ### run the moter to the correct position
        self.instr.set_M(self.OnPosition)
        time.sleep(1)

        ### perofrom the measurement
        t0 = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())) if timestamp is None else timestamp
        T = self.instr.get_T()
        info = f"\n{self.idx:d} {t0} {T}"
        print(info)
        self.fout1.write(info)

        self.idx += 1
        if self.idx%10 == 9: self.fout1.flush()

        ### move moter back
        self.instr.set_M(self.OffPosition)

    def close(self):
        self.fout1.close()
        self.instr.disconnect()

def action1(is0, M_pattern):
    '''This function does this:
        1) perform a measurement of temperature; 
        2) start a thread to operate the motor; 
        3) return the temperature;
        
    The input is the STM32 instance, and motor time parameters is taken from STM32 instance'''
    T = is0.get_T()
    print(f'T: {T}')
    ## Start the instance
    p2 = Process(target=run_motor_pattern, args=(is0, M_pattern))
    p2.start()

    return T


def run_mode3(outTname='tempT.dat'):
    is1 = STM32()
    is1.connect()

    ### configurations
    is1.T_dt = 150
    is1.M_dt = 33.2
    is1.T_outfname = outTname

    ### start the process
    lock = Lock()
    p1 = Process(target=measure_T, args=(lock, is1))
    p2 = Process(target=run_motor, args=(lock, is1))
    
    p1.start()
    p2.start()

    while p1.is_alive() or p2.is_alive():
        try:
            if p1.is_alive(): p1.join()
            if p2.is_alive(): p2.join()
        except KeyboardInterrupt:
            is1.ON = False

    ### done
    is1.disconnect()

def run_motor_pattern(clt, M_pattern):
    for p in M_pattern:
        if p[0]>0: time.sleep(p[0])
        print(f"M-->{p[1]}")
        clt.set_M(p[1])
 
def run_motor(l, clt):
    degree1=0
    degree2=90
    command=degree1
    try:
        while clt.ON:
            print(f"M->{command}")
            l.acquire()
            try:
                clt.set_M(int(command))
            finally:
                l.release()

            if command==degree1: command=degree2
            elif command==degree2: command=degree1
            time.sleep(clt.M_dt)

    except KeyboardInterrupt:
        pass
        
def measure_T(l, clt):
    with open(clt.T_outfname,'w') as fout1:
        fout1.write("idx/I:time/C:T/F")
        idx = 0

        try:
            while clt.ON:
                t0 = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))

                l.acquire()
                try:
                    T = clt.get_T()
                finally:
                    l.release()

                info = f"{idx:d} {t0} {T}"
                print(info)
                fout1.write('\n'+info)
                time.sleep(clt.T_dt)

                idx += 1
                if idx%10 == 9: fout1.flush()

        except KeyboardInterrupt:
            pass

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

def test_measureT():
    tm1 = TemperatureMonitor('tt.1')
    tm1.measure()
    tm1.close()

if __name__ == '__main__':
     listPorts()
     main()
#     test_measureT()
#     record_T("T_Aug27a_1920.dat")
#    loopAlpha()
#   run_mode3("T_Aug26_night1.dat")
