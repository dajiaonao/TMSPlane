#!/usr/bin/env python3

import socket
import numpy as np

class Oscilloscope:
    def __init__(self, name='Keysight MSO-x 4054', addr='192.168.2.5:5025'):
        self.addr = addr
        self.ss = None
        self.name = name
        self.fileSuffix = '.1'
        self.connected = False
        self.cmdSuffix = '\n'

    def connect(self, force=False):
        if self.connected and (not force): return

        t = self.addr.split(':')
        hostname = t[0]
        port = int(t[1]) if len(t)>1 else 5025

        self.ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)       #init local socket handle
        try:
            self.ss.connect((hostname,port))                                 #connect to the server
        except ConnectionRefusedError as e:
            print(e)
            return False 
        self.connected = True
        return True

    def disconnect(self):
        if not self.connected: return
        self.ss.close()
        self.connected = False

    def send(self, cmd):
        ### to have costumize command string

        self.ss.send((cmd+self.cmdSuffix).encode("UTF-8"))                           #read back device ID

    def query(self,cmd):
        self.send(cmd)
        print(cmd+"-> %s"%self.ss.recv(128))

    def test1(self):
        self.connect() 
        ss = self.ss

        ### trigger
#         self.query("TRIGger:A?")
        self.query("TRIGger:A:EDGE?")
        return


        ### setup histogram
        self.send("HISTOGRAM?")
        print("GET: %s"%ss.recv(128))

        self.send("HIStogram:COUNt RESET")
#         self.send("HIStogram:BOXPcnt?")
        self.send("MEASUREMENT:MEAS1?")
        print("GET: %s"%ss.recv(128))

        self.send("MEASUREMENT:MEAS1:COUNT?")
        print("GET: %s"%ss.recv(128))

        self.send("MEASUREMENT:MEAS1:VALue?")
        print("GET: %s"%ss.recv(128))


    def test(self, step=0):
        self.connect() 
        ss = self.ss

        self.send("*IDN?;")                           #read back device ID
        print("Instrument ID: %s"%ss.recv(128))

#         self.send("SETUP1:TIME?")
        self.send("MEASUrement:IMMed:TYPe WAVEFORMS")
        self.send("MEASUrement:IMMed:TYPe?")
        print("Time: %s"%ss.recv(128))
        self.send("MEASUrement:IMMed:UNIts?")
        print("Unit: %s"%ss.recv(128))
        self.send("TIME?")
        print("Time1: %s"%ss.recv(128))
        self.send("MEASUrement:IMMed:VALue?")
        print("Value: %s"%ss.recv(128))
        self.send("TIME?")
        print("Time2: %s"%ss.recv(128))

def test():
    os1 = Oscilloscope(name='Tektronix MSO 4034B', addr='192.168.2.17:4000')

#     for i in range(10000):
#         os1.addr = f'192.168.2.17:{i:d}'
#         try:
#             if not os1.connect(force=True):
#                 print(i)
#                 continue
#             os1.send("*IDN?;")
#             print(i, "Instrument ID: %s"%os1.ss.recv(128))
#             os1.disconnect()
#         except (ConnectionRefusedError,OSError,BrokenPipeError) as e:
# #             print(i)
#             continue

    os1.test1()

if __name__ == '__main__':
    test()
