#!/usr/bin/env python3
# from __future__ import print_function
import serial
import time
import os
from datetime import datetime

def listPorts():
    import serial.tools.list_ports
    port_list = list(serial.tools.list_ports.comports())
    print(port_list)
    if len(port_list) == 0:
        print('No port avaliable')
    else:
        for i in range(0,len(port_list)):
            print(port_list[i])

class Picoammeter:
    def __init__(self):
        self.ser = None
    def connect(self):
        portx="/dev/ttyUSB0"
        bps=57600
        timex=5
        self.ser=serial.Serial(portx,bps,timeout=timex)
    def send(self, msg):
        if msg[-2:] != '\r\n': msg+='\r\n'
        return self.ser.write(msg.encode("UTF-8"))

    def test1(self):
        self.send("FUNC 'CURR'")
        self.send('SYST:ZCH ON')
        self.send('RANG 2e-9')
        self.send('INIT')
        self.send('SYST:ZCOR:ACQ')
        self.send('SYST:ZCOR ON')
        self.send('RANG:AUTO ON')
        self.send('SYST:ZCH OFF')
        self.send('READ?')

        result = self.ser.read(200)
        print(result.decode())

    def speed_check(self):
        self.send('FORM:ELEM READ,TIME')
        self.send('SYST:ZCH OFF')

        for i in range(20):
            self.send('TRIG:COUN 20')
            self.send('TRAC:POIN 20')
            self.send('TRAC:FEED SENS')
            self.send('TRAC:FEED:CONT NEXT')
            print(datetime.now(), i)
            self.send('INIT')
            ret = self.query('TRAC:DATA?',4096)
            print(ret)
 
    def read_many(self):
#         self.send('*RST')
        self.send('TRIG:DEL 0')
        self.send('TRIG:COUN 2000')
        self.send('NPLC .01')
#         self.send('RANG .002')
        self.send('SYST:ZCH OFF')
        self.send('SYST:AZER:STAT OFF')
        self.send('DISP:ENAB OFF')
        self.send('*CLS')
        self.send('TRAC:POIN 2000')
        self.send('TRAC:CLE')
        self.send('TRAC:FEED:CONT NEXT')
        self.send('STAT:MEAS:ENAB 512')
        self.send('*SRE 1')
        q1 = self.query('*OPC?')
        print(q1)

        self.send('INIT')
        self.send('DISP:ENAB ON')
        q2 = self.query('TRAC:DATA?')
        print(q2)

    def test(self):
        self.connect()
        self.send('*IDN?')
        result = self.ser.read(1000)
        print(len(result),'->',result.decode())

        self.send('*RST')
#         self.test1()
        self.send("FUNC 'CURR'")
#         self.speed_check()
#         self.read_many()
        self.run_measure()
#         self.test_get_mean()
#         self.multiple_reading()
#         self.set_relative()
        self.ser.close()

    def set_relative(self): 
        self.send('READ?')
        ret1 = self.ser.read(200)
        print(ret1.decode())

        self.send('CALC2:NULL:OFFS 1e-6')
        self.send('CALC2:NULL:STAT ON')
        self.send('SYST:ZCH OFF')
        self.send('INIT')
        self.send('CALC2:DATA?')
        ret1 = self.ser.read(200)
        print(ret1.decode())

        self.send('READ?')
        ret1 = self.ser.read(200)
        print(ret1.decode())

    def multiple_reading(self):
        self.send('ARM:SOUR IMM')
        self.send('ARM:COUN 1')
        self.send('TRIG:SOUR IMM')
        self.send('TRIG:COUN 10')
        self.send('SYST:ZCH OFF')

        for i in range(10):
            self.send('READ?')

            ret1 = self.ser.read(1024)
            while ret1[-2:] != b'\r\n':
#                 print(ret1)
                ret1 += self.ser.read(1024)
            ret1 = ret1.rstrip()
            data = list(zip(*[iter(ret1.split(b','))]*3))

            values = [float(x[0][:-1]) for x in data]
            print(values)

    def query(self, cmd, L=1024):
        self.send(cmd)
        return self.recv_all(L).decode();

    def recv_all(self, L=1024):
        ret1 = self.ser.read(L)
        while ret1[-2:] != b'\r\n': ret1 += self.ser.read(L)
        return ret1.rstrip()

    def test_get_mean(self):
        self.send('FORM:ELEM READ,TIME')
        self.send('TRIG:COUN 20')
        self.send('TRAC:POIN 20')
        self.send('TRAC:FEED SENS')
        self.send('TRAC:FEED:CONT NEXT')
        self.send('SYST:ZCH OFF')
        self.send('INIT')
        print(self.query('TRAC:DATA?'))

        self.send('CALC3:FORM MEAN')
        print(self.query('CALC3:DATA?'))


    def run_measure_tes2(self):
        self.send('FORM:ELEM READ,TIME')
        self.send('TRIG:COUN 20')
        self.send('TRAC:POIN 20')
        self.send('TRAC:FEED SENS')
        self.send('TRAC:FEED:CONT NEXT')
        self.send('SYST:ZCH OFF')
        self.send('INIT')
#         print(self.query('TRAC:DATA?'))

        self.send('CALC3:FORM MEAN')
        print(self.query('CALC3:DATA?'))

    def run_measure(self):
        ### setup the zero correction
        self.send('SYST:ZCH ON')
        self.send('RANG 2e-9')
        self.send('INIT')
        self.send('SYST:ZCOR:ACQ')
        self.send('SYST:ZCOR ON')
        self.send('RANG:AUTO ON')
#         self.send('RANG: 200e-9')
        self.send('SYST:ZCH OFF')

        ### HV
        self.send('SOUR:VOLT:RANG 10') #Select 10V source range.
        self.send('SOUR:VOLT 10') #  Set voltage source output to 10V.
        self.send('SOUR:VOLT:ILIM 2.5e-3') #  Set current limit to 2.5mA.
        self.send('SOUR:VOLT:STAT ON') # Put voltage source in operate.

        ### take data
        self.send('FORM:ELEM READ,VSO,TIME')
        self.send('TRIG:DEL 0')
        self.send('TRIG:COUN 10')
#         self.send('NPLC .01')
        self.send('NPLC 1')
        self.send('TRAC:POIN 10')
        self.send('SYST:AZER:STAT OFF')
        self.send('DISP:ENAB OFF')
#         self.send('*CLS')
#         self.send('STAT:MEAS:ENAB 512')
#         self.send('*SRE 1')
#         q1 = self.query('*OPC?')
#         print(q1)

#         time.sleep(3)
        sampleDir = './'
        idir = 0
        while os.path.exists('project_'+str(idir)): idir+=1
        project_dir = sampleDir+'project_'+str(idir)+'/'
        os.makedirs(project_dir)

        with open(project_dir+'current.dat','w') as fout1:
            while True:
#              for t in range(3):
                t0 = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
                try:
                    self.send('TRAC:CLE')
                    self.send('TRAC:FEED:CONT NEXT')
                    self.send('INIT')
                    q2 = self.query('TRAC:DATA?')

                    data = list(zip(*[iter(q2.split(','))]*3))
                    outx = ''
                    for d in data: outx += t0 + ' ' + d[0]+' '+d[1]+' '+d[2]+'\n'

#                     print(outx)
                    fout1.write(outx)
                    fout1.flush()

                except KeyboardInterrupt:
                    break
        self.send('TRAC:CLE')
        print('done')

    def run_measure_test(self):
        self.send('ARM:SOUR IMM')
        self.send('ARM:COUN 1')
        self.send('TRIG:SOUR IMM')
        self.send('TRIG:COUN 10')
        self.send('SYST:ZCH OFF')

        with open('current.dat','w') as fout1:
            while True:
                try:
                    self.send('READ?')

                    ret1 = self.ser.read(1024)
                    while ret1[-2:] != b'\r\n':
                        ret1 += self.ser.read(1024)
                    ret1 = ret1.rstrip()
                    data = list(zip(*[iter(ret1.split(b','))]*3))

                    values = [float(x[0][:-1]) for x in data]
                    fout1.write(time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))+' '+str(values[0])+'\n')
                    fout1.flush()

                except KeyboardInterrupt:
                    break

def test_measure():
    try:
        portx="/dev/ttyUSB0"
        bps=115200
        timex=5
        ser=serial.Serial(portx,bps,timeout=timex)
        print(ser)

        result=ser.write("*RST".encode("UTF-8"))
        print("return",result)

        ser.close()

    except Exception as e:
        print("Somthing wrong",e)


def test1():
    pm1 = Picoammeter()
    pm1.test()

if __name__ == '__main__':
    test1()
