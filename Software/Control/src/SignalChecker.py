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
 
def test1():
    sc1 = SignalChecker()
    sc1.take_samples()

if __name__ == '__main__':
    test1()
