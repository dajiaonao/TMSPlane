#!/usr/bin/env python3
# from __future__ import print_function
import serial

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

 
    def test(self):
        self.connect()
        self.send('*IDN?')
        result = self.ser.read(1000)
        print(len(result),'->',result.decode())

#         self.send('*RST')
#         self.test1()
        self.send("FUNC 'CURR'")
        self.multiple_reading()
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
        self.send('READ?')

        ret1 = self.ser.read(2000)
        print(ret1.decode())


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
