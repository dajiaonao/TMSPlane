#!/usr/bin/env python
import socket, os
# import argparse
# import pprint
from command import *
from sigproc import SigProc 
import time
import array
import glob
from ROOT import *
from subprocess import call
from math import isnan
from datetime import datetime, timedelta

def waitRootCmdY():
    a = raw_input("waiting...")

def useLHCbStyle0():
    pass

try:
    from rootUtil import waitRootCmdX, useLHCbStyle
except ImportError:
    waitRooCmdX = waitRootCmdY
    useLHCbStyle = useLHCbStyle0 

class DataRecorder:
    def __init__(self):
        self.control_ip_port = "192.168.2.3:1024"
        self.cmd = Cmd()
        self.s = None
        self.connected = False
        self.fileSuffix = '.1'
        self.tStop = None

    def connect(self):
        ctrlipport = self.control_ip_port.split(':')
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect((ctrlipport[0],int(ctrlipport[1])))
        self.connected = True

    def take_samples2(self, n=10, outRootName='test_sample.root', runNumber=0):
        if not self.connected: self.connect()
        nMonitor = 20

        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        T = array.array('i',[0])
        V = array.array('i',[0])
        if self.fileSuffix:
            while os.path.exists(outRootName): outRootName += self.fileSuffix
        fout1 = TFile(outRootName,'recreate')
        tree1 = TTree('tree1',"data: {0:d} channel, {1:d} samples".format(s1.nAdcCh, s1.nSamples))
        tree1.Branch('T',T,'T/i')
        tree1.Branch('V',V,'V/I')
        tree1.Branch('adc',data1, "adc[{0:d}][{1:d}]/F".format(s1.nAdcCh, s1.nSamples))

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)

        status = 0
        try:
            for i in range(n):
                ### time consitraint
                if self.tStop is not None and datetime.now()>self.tStop:
                    status = 2
                    break

                if i%100==0:
                    print(str(i)+' samples taken.')
                    try:
                        with open('/home/dlzhang/work/repos/TMSPlane2/Software/Control/src/.pulse_status') as f1:
                            V[0] = int(f1.readline().rstrip())
                    except:
                        V[0] = -999
                self.s.sendall(self.cmd.send_pulse(1<<2));

                T[0] = int(time.time())
                ret = self.cmd.acquire_from_datafifo(self.s, nWords, buf)
                s1.demux_fifodata(ret,data1,data2)
                tree1.Fill()

                if i%nMonitor == 1: tree1.AutoSave("SaveSelf");
        except KeyboardInterrupt:
            status = 1

        fout1.Write()
        return status

def take_data(sTag, n=5000, N=-1, dirx=None):
    sc1 = DataRecorder()
    sc1.control_ip_port = "localhost:1024"
    dir1 = 'data/fpgaLin/'

    ### put in a dedicated direcotry
    if dirx is not None:
        dir1 += dirx
        if not os.path.exists(dir1):
            os.makedirs(dir1)
    dir1 = dir1.rstrip()
    if dir1[-1] != '/': dir1 += '/'

    ### really start taking samples
    nSample = 0
    while nSample != N:
        print "Start sample {0:d}".format(nSample)
        status = sc1.take_samples2(n, dir1+sTag+"_data_{0:d}.root".format(nSample))
        if status: break
        nSample += 1

def take_dataT(sTag, n=5000, Tmin=30, dirx=None):
    ''' Take data for Tmin minutes'''

    sc1 = DataRecorder()
    sc1.control_ip_port = "localhost:1024"
    dir1 = 'data/fpgaLin/'

    sc1.tStop = datetime.now() + timedelta(minutes=Tmin)
    print sc1.tStop, datetime.now()

    ### put in a dedicated direcotry
    if dirx is not None:
        dir1 += dirx
        if not os.path.exists(dir1):
            os.makedirs(dir1)
    dir1 = dir1.rstrip()
    if dir1[-1] != '/': dir1 += '/'

    ### really start taking samples
    nSample = 0
    while True:
        print "Start sample {0:d}".format(nSample)
        status = sc1.take_samples2(n, dir1+sTag+"_data_{0:d}.root".format(nSample))
        if status: break
        nSample += 1

if __name__ == '__main__':
#     useLHCbStyle()
#       take_data(sTag='May13T1a',n=1000, N=-1, dirx='raw/May13T1a')
      take_dataT(sTag='May14T1c',n=2000, Tmin = 30, dirx='raw/May14T1c')
