#!/usr/bin/env python
import socket

class Rigol:
    def __init__(self):
        self.addr = '192.168.2.5:5555'
        self.s3 = None

    def connect(self):
        a = self.addr.split(':')
        Rig_hostname = a[0]                    #rigol dds ip address
        Rig_port = int(a[1])                                 #rigol dds instrument port
        self.s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #init local socket handle
        self.s3.connect((Rig_hostname, Rig_port))

    def test(self, freq):
        self.s3.send(":SOURce1:FREQuency %s\n"%freq)          #set output frequency, default value 1MHz 
        self.s3.send(":SOURce1:VOLTage 1\n")                 #set output amplitude
        self.s3.send(":PA:OFFSet:VALUe 1\n")                       #set output offset, default value 1V 

def test2():
    r1 = Rigol()
    r1.connect()
    r1.test(20)

def test1():
    freq = 50
    Rig_hostname = '192.168.2.5'                    #rigol dds ip address
    Rig_port = 5555                                 #rigol dds instrument port
    s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #init local socket handle
    s3.connect((Rig_hostname, Rig_port))

    s3.send(":SOURce1:FREQuency %s\n"%freq)          #set output frequency, default value 1MHz 
    s3.send(":SOURce1:VOLTage 1\n")                 #set output amplitude
    s3.send(":PA:OFFSet:VALUe 1\n")                       #set output offset, default value 1V 
#    s3.send("OUTPut ON\n")                 #turn on channel1

    s3.close()

if __name__ == '__main__':
    test2()
