#!/usr/bin/env python
import socket
# import argparse
# import pprint
from command import *
from sigproc import SigProc 
import time


class SignalChecker:
    def __init__(self):
        self.control_ip_port = "192.168.2.3:1024"
        self.cmd = Cmd()
        self.s = None
        self.connect()

    def connect(self):
        ctrlipport = self.control_ip_port.split(':')
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect((ctrlipport[0],int(ctrlipport[1])))

    def take_samples(self, n=10, name="sample_{0:d}"):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)

        for i in range(n):
            self.s.sendall(self.cmd.send_pulse(1<<2));
            time.sleep(0.5)

            name1 = name.format(i)
            ret = self.cmd.acquire_from_datafifo(self.s, nWords, buf)
            s1.demux_fifodata(ret,data1,data2)
            s1.save_data([name1+'.adc', name1+'.sdm'], data1, data2)

    def show_signal(self):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)


        self.s.sendall(self.cmd.send_pulse(1<<2));
        time.sleep(0.5)

        ret = self.cmd.acquire_from_datafifo(self.s, nWords, buf)
        s1.demux_fifodata(ret,data1,data2)

        mx = s1.measure_pulse(data1, fltParam=[500, 150, 200, -1.])
        for x in mx:
            for i in range(len(x)):
                print x[i]
        d = [x[1] for x in mx]
        self.plot_data(d)

    def plot_data(self,d):
        if len(d)<19:
            print('Need 19 entries')
            return
        from ROOT import TH2Poly, gStyle
        gStyle.SetOptStat(0)

        hc = TH2Poly();
        hc.SetTitle("TMS19Plane");
        hc.Honeycomb(-4.3,-4,1,5,5);
        listA = [(0,0),(2,0),(1,1.5),(-1,1.5),(-2,0),(-1,-1.5),(1,-1.5),(4,0),(3,2),(1,3),(0,3),(-1,3),(-3,2),(-4,0),(-3,-2),(-1,-3),(0,-3),(1,-3),(3,-2)]

        for i in range(len(listA)):
            hc.Fill(listA[i][0],listA[i][1],d[i])

        hc.Draw("text colz0");
        raw_input('waiting...')

def test1():
    sc1 = SignalChecker()
#     sc1.take_samples()
    sc1.show_signal()

if __name__ == '__main__':
    test1()
