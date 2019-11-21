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
from Rigol import Rigol

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
        self.dV = None
        self.HV = 0

    def connect(self):
        ctrlipport = self.control_ip_port.split(':')
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect((ctrlipport[0],int(ctrlipport[1])))
        self.connected = True

    def take_samples2(self, n=10, outRootName='test_sample.root', runNumber=0, nMonitor = 20):
        if not self.connected: self.connect()

        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        T = array.array('i',[0])
        V = array.array('i',[0])
        HV = array.array('i',[0])
        if self.fileSuffix:
            while os.path.exists(outRootName): outRootName += self.fileSuffix
        fout1 = TFile(outRootName,'recreate')
        tree1 = TTree('tree1',"data: {0:d} channel, {1:d} samples".format(s1.nAdcCh, s1.nSamples))
        tree1.Branch('T',T,'T/i')
        tree1.Branch('V',V,'V/I')
        tree1.Branch('HV',HV,'HV/I')
        tree1.Branch('adc',data1, "adc[{0:d}][{1:d}]/F".format(s1.nAdcCh, s1.nSamples))

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)

        V[0] = -999 if self.dV is None else self.dV
        HV[0] = self.HV

        status = 0
        try:
            for i in range(n):
                ### time consitraint
                if self.tStop is not None and datetime.now()>self.tStop:
                    status = 2
                    break

                if self.dV is None and i%100==0:
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

def take_dataR(sTag, n=5000, N=-1, dirx=None,nm=1000, dVList=[], HV=-1):
    sc1 = DataRecorder()
    sc1.dV = None
    sc1.HV = HV
    dir1 = 'data/fpgaLin/'

    ### put in a dedicated direcotry
    if dirx is not None:
        dir1 += dirx
        if not os.path.exists(dir1):
            os.makedirs(dir1)
    dir1 = dir1.rstrip()
    if dir1[-1] != '/': dir1 += '/'

    ### really start taking samples
    idV = 0
    nSample = 0
    while nSample != N:
        if dVList:
            dv = dVList[idV]
            idV = (idV+1)%len(dVList)

            rg1 = Rigol()
            rg1.connect()
            rg1.setPulseV(dv)

            sc1.dV = int(1000*dv)
        print "Start sample {0:d}".format(nSample)
        status = sc1.take_samples2(n, dir1+sTag+"_data_{0:d}.root".format(nSample), nMonitor=nm)
        if status: break
        nSample += 1

def take_data(sTag, n=5000, N=-1, dirx=None,nm=1000, dV=None):
    sc1 = DataRecorder()
    sc1.dV = dV
#     sc1.control_ip_port = "localhost:1024"
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
        status = sc1.take_samples2(n, dir1+sTag+"_data_{0:d}.root".format(nSample), nMonitor=nm)
        if status: break
        nSample += 1

def take_dataT(sTag, n=5000, Tmin=30, dirx=None):
    ''' Take data for Tmin minutes'''

    sc1 = DataRecorder()
#     sc1.control_ip_port = "localhost:1024"
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

def take_Run():
    for dV in [0.1, 0.04, 0.2, 0.06, 0.4, 0.15, 0.3, 0.02, 0.25, 0.6, 0.35]:
#     for dV in [0.1, 0.2]:
        rg1 = Rigol()
        rg1.connect()

        rg1.setPulseV(dV)
        take_data(sTag='Nov13b_HV0p5b',n=1000, N=2, dirx='raw/Nov13b',nm=200, dV=int(1000*dV))

def take_calibration():
    rg1 = Rigol()
    rg1.connect()

    for dV in [0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]:
        rg1.setPulseV(dV)
        tag1 = '_{0:d}mV'.format(int(dV*1000))
        take_data(sTag='Nov04d'+tag1,n=1000, N=5, dirx='raw/Nov04d',nm=200)

if __name__ == '__main__':
#     useLHCbStyle()
#       take_data(sTag='Sep12b1',n=1000, N=-1, dirx='raw/Sep12b')
#       take_data(sTag='Oct09a',n=2000, N=5, dirx='raw/Oct09a',nm=200)
#       take_data(sTag='Oct10b',n=1000, N=5, dirx='raw/Oct10b',nm=200)
#       take_data(sTag='Nov04b',n=1000, N=20, dirx='raw/Nov04b',nm=200)
      take_data(sTag='Nov19b',n=1000, N=-1, dirx='raw/Nov19b',nm=1)
#       take_dataR(sTag='Nov19a',n=1000, N=-1, dirx='raw2/Nov19a',nm=200, dVList=[0.1, 0.04, 0.2, 0.06, 0.4, 0.15, 0.3, 0.02, 0.25, 0.6, 0.35, 0.5])
#       take_Run()
#       take_data(sTag='May13T1a',n=1000, N=-1, dirx='raw/May13T1a')
#       take_dataT(sTag='May14T1c',n=2000, Tmin = 30, dirx='raw/May14T1c')
#     take_calibration()
