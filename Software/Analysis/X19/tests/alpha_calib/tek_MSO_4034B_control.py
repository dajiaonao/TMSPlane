#!/usr/bin/env python3
import time
from datetime import datetime
import socket
import numpy as np
from Rigol import Rigol

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

        ### check the connection
#         self.send("DCL;")                           #read back device ID
        time.sleep(5)
#         self.send("*CLS;")                           #read back device ID
        self.query("*IDN?;")                           #read back device ID
#         print("Instrument ID: %s"%self.ss.recv(128))

        self.connected = True
        return True

    def disconnect(self):
        if not self.connected: return
        self.ss.close()
        self.connected = False

    def send(self, cmd):
        ### to have costumize command string

        self.ss.send((cmd+self.cmdSuffix).encode("UTF-8"))                           #read back device ID

    def query(self,cmd, show=True, nByte=128):
        self.send(cmd)
        ret = self.ss.recv(nByte).decode()
        if show: print(f"{cmd}-> {ret}")
        return ret.rstrip().split(' ')[1:]

    def setup_default_mode(self):
        ss = self.ss

        ## acquire
        self.send("ACQuire:MODe HIRes")
        self.send("SELect:CH1 OFF; SELect:CH2 ON; SELect:CH3 OFF; SELect:CH4 OFF;")
        self.send("CH2:COUPling; CH2:INVert OFF")
        self.send("HORizontal:SCAle 1; HORizontal:RECOrdlength 20000000")
#         self.send("DESE 1")
#         self.send("DESE 1")

    def test2(self, N=10):
        self.connect() 
        self.setup_default_mode()

        self.ss.settimeout(2.)
        for i in range(N):
            print(datetime.now())
            self.send("*CLS;")
            self.send("ACQUIRE:STOPAFTER SEQUENCE")
            self.send("ACQuire:STATE ON")
            self.send('*WAI')

            self.send('SAVE:WAVEFORM CH2, "E:/test2.isf";')
#             self.send('*WAI')
#             self.send("BUSY?")
# 
#             while True:
#                 try:
#                     ret = self.ss.recv(128).decode()
#                 except socket.timeout:
#                     time.sleep(1)
#                     continue
#                 if ret == '0': break
            while True:
                try:
                    print("querying...")
#                     self.query("*ESR?")
                    self.query("BUSY?")
                except socket.timeout:
                    time.sleep(1)

    def test1(self):
        self.connect() 
        ss = self.ss

#         self.send("*CLS;")
#         self.query("*ESR?")
#         self.setup_default_mode()
#         return

#         time.sleep(200)
        ### trigger
#         self.send("DATa:SOUrce CH2")
#         self.query("DATa:STARt?")
#         self.send("DATa:STOP 1000")
# #         self.query("ACQuire:MAXSamplerate?")
#         self.query("DATa?")
#         self.send("ACQuire:MODe HIRes")
#         self.query("ACQuire:STATE?")
#         self.query("ACQUIRE:STOPAFTER?")

        print(datetime.now())
        self.send("ACQUIRE:STOPAFTER SEQUENCE")
        self.send("ACQuire:STATE ON")
        time.sleep(9)

#         print('A',self.query("ACQuire:STATE?"),"t")
        ss.settimeout(None)
        while True:
            if self.query("ACQuire:STATE?")[0] == '0': break
            time.sleep(1)
        
        self.send('SAVE:WAVEFORM CH2, "E:/test2.isf";')
        self.send('*WAI')
        self.query("BUSY?")
#         self.query("*ESR?")
        self.send("*CLS;")
        return
#         self.query("ACQuire:STATE?")
#         self.send("DATa:ENCdg RPBinary")
#         self.query("SET?")
#         self.query("*LRN?")
#         self.query("DATa?")
#         self.query("WFMOutpre?")
#         time.sleep(2)
#         self.query("*esr?")
#         self.query("*OP?")
        print("here....")
        self.send("ACQUIRE:STOPAFTER RUNSTop")
#         self.send("ACQuire:STATE ON")
        ss.settimeout(2.0)
        while True:
            try:
                print('wait A')
                self.send("ACQuire:STATE ON")
                print(self.query("ACQuire:STATE?"))
#                 print('A',self.query("ACQuire:STATE?"),"t")
            except socket.timeout:
                continue
            break
        print(datetime.now())
        return

        self.send("HORizontal:RECOrdlength 10000000")
        self.send("DATa:STOP 10000000")
        self.query("WFMOutpre?")
        self.query("CH2:OFFSet?")
        self.query("CH2:PRObe:UNIts?")
        self.query("CH2:YUNIts?")
        self.query("CH2:POSition?")
        self.query("CH2:SCAle?")
#         self.query("CURVe?",nByte=16384)


#         self.send("DATa:ENCdg RIBinary")
        self.send("DATa:ENCdg RPBinary")
        self.query("DATa?")
        ###get data
        self.send("CURVe?")
        lenx = 10000000+13
        a = self.ss.recv(128)
        while len(a)<lenx:
            a += self.ss.recv(128)
#         a += self.ss.recv(128).decode()
#         a += self.ss.recv(128).decode()
#         a += self.ss.recv(128).decode()
#         a += self.ss.recv(128).decode()
#         a += self.ss.recv(128).decode()
        b = a[:13]
        c = a[13:]
        print(len(c))
#         print(a)
#         print(b)
#         print(c)
#         print([int.from_bytes(x, byteorder='big', signed=True) for x in c])
#         print([(int(x)-128)*0.005 for x in c])
#         self.query("TRIGger:A?")
#         self.query("TRIGger:A:EDGE?")
#         self.query("HIStogram:DATa?", nByte=4096)
#         self.query("HIStogram:STARt?")
#         self.query("HIStogram:END?")
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

    def use_setup0(self):
        ### the range of x is 20us x 10

        pass

    def use_setup1(self):
        pass

    def getHistogramCounts(self, debug=False):
        t0 = self.query("TIME?", show=debug)
        n1 = self.query("MEASUREMENT:MEAS1:VALue?", show=debug)
        t1 = self.query("TIME?", show=debug)

        return t0[0], n1[0], t1[0]


    def getHistogramData(self, debug=False):
        a = self.query("HIStogram:STARt?")
        b = self.query("HIStogram:END?")
        c = self.query("HIStogram:DATa?", nByte=4096)

        return a[0], b[0], c[0]

def check_countloss(freq=600, dT=360, N=10):
    ### assume all other paramneters are setup
    ### setup Rigo to produce the freqency
    r1 = Rigol()
    r1.connect()
    r1._instr.write(":SOURce2:FREQuency %s"%freq)

    ### run the measurement
    os1 = Oscilloscope(name='Tektronix MSO 4034B', addr='192.168.2.17:4000')
    os1.connect()
    ### reset the histogram
    os1.send("HIStogram:COUNt RESET")
    time.sleep(5)

    with open("test2.csv",'a') as f1:
        f1.write(f"\n#freq={freq} Hz")
        i = 0
        while True:
            m1 = os1.getHistogramCounts()
            print(m1)
            f1.write('\n'+', '.join(m1))
            i += 1
            if i>N: break
            time.sleep(dT)
       
        ### finally save the histogram
        a,b,c = os1.getHistogramData()
        f1.write('\n#HistData:'+':'.join([a, b, c]))

    return

def check_multiple():
#     for f in [1000, 1500, 1200, 1300, 1100, 490, 510, 980]:
#     for f in [1000, 200]:
#     for f in [600,900,300,1500,700,1200,500,800,1000,400,200,550,650,750,450]:
    for f in [1510]:
        check_countloss(freq=f, dT=360, N=3)

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
    os1.test2()
    return

    for i in range(10):
        os1.test1()
        os1.disconnect()

if __name__ == '__main__':
    test()
#     check_multiple()
#     check_countloss()
