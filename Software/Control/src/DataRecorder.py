#!/usr/bin/env python3
import socket, os
# import argparse
# import pprint
from command import *
from sigproc import SigProc 
import time
import array
import glob, re
from ROOT import TTree, TFile
from subprocess import call
from math import isnan
from datetime import datetime, timedelta
from Rigol import Rigol

def waitRootCmdY():
    a = input("waiting...")

def useLHCbStyle0():
    pass

def getMaxIndex(files,pattern='.*_data_(\d+).root'):
    idx0 = None
    for f in files:
        m = re.match(pattern,f)
        if m:
            idx = int(m.group(1))
            if idx0 is None or idx>idx0: idx0 = idx
    return idx0

try:
    from rootUtil3 import waitRootCmdX, useLHCbStyle
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

                if self.dV is None and i%100==1:
                    print((str(i)+' samples taken.'))
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
    #dir1 = 'data/fpgaLin/'
    #dir1 = '/home/TMSTest/PlacTests/TMSPlane/data/fpgaLin/'
    dir1 = '/data/TMS_data/raw/'

    ### put in a dedicated direcotry
    if dirx is not None:
        dir1 += dirx
        if not os.path.exists(dir1):
            os.makedirs(dir1)
    dir1 = dir1.rstrip()
    if dir1[-1] != '/': dir1 += '/'

    rg1 = Rigol()
    rg1.connect()
    rg1.calibration()

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
        print("Start sample {0:d}".format(nSample))
        status = sc1.take_samples2(n, dir1+sTag+"_data_{0:d}.root".format(nSample), nMonitor=nm)
        if status: break
        nSample += 1

def take_data(sTag, n=5000, N=-1, dirx=None,nm=1000, dV=None, dir1='/data/TMS_data/raw/'):
    sc1 = DataRecorder()
    sc1.dV = dV
#     sc1.control_ip_port = "localhost:1024"
#     dir1 = 'data/fpgaLin/'
#     dir1 = '/data/TMS_data/raw/'

    ### put in a dedicated direcotry
    if dirx is not None:
        dir1 += dirx
        if not os.path.exists(dir1):
            os.makedirs(dir1)
    dir1 = dir1.rstrip()
    if dir1[-1] != '/': dir1 += '/'

    ### find the start index
    ifdx = getMaxIndex(glob.glob(dir1+'*.root'),'.*_data_(\d+).root')
    if ifdx is None: ifdx = 0
    else: ifdx += 1

    ### really start taking samples
    nSample = 0
    while nSample != N:
        print("Start sample {0:d}".format(nSample))
        status = sc1.take_samples2(n, dir1+sTag+"_data_{0:d}.root".format(ifdx+nSample), nMonitor=nm)
        if status: break
        nSample += 1

def take_dataT(sTag, n=5000, Tmin=30, dirx=None):
    ''' Take data for Tmin minutes'''

    sc1 = DataRecorder()
#     sc1.control_ip_port = "localhost:1024"
#     dir1 = 'data/fpgaLin/'
    dir1 = '/data/TMS_data/raw/'

    sc1.tStop = datetime.now() + timedelta(minutes=Tmin)
    print(sc1.tStop, datetime.now())

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
        print("Start sample {0:d}".format(nSample))
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
#     rg1.syncPhase()
#     rg1.setPhaseDev(150)

#     for dV in [0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]:
#     for dV in [0.1, 0.2, 0.5, 1.0, 2.0]:
#    for dV in [0.1, 0.2, 0.5, 1.0, 1.5]:
    Nstep = 8
    highV = 0.98
    lowV = 0.9
    for i in range(Nstep+1):
        dV = lowV + (highV-lowV)/Nstep*i
        rg1.setPulseV(dV)
        tag1 = '_Gring{0:d}mV'.format(int(dV*1000))
#         take_data(sTag='Ext5p88F_A3'+tag1,n=1000, N=1, dirx='Jan23_TMS',nm=200)
        take_data(sTag='Ext5p88F20mV_A3'+tag1,n=1500, N=1, dirx='Jan25_TMS',nm=200)

    rg1.setPulseV(0.2)

if __name__ == '__main__':
#     useLHCbStyle()
    tTag = datetime.now().strftime("%Y%b%d%H%M")
#       take_data(sTag='Sep12b1',n=1000, N=-1, dirx='raw/Sep12b')
#       take_data(sTag='Oct09a',n=2000, N=5, dirx='raw/Oct09a',nm=200)
#       take_data(sTag='Oct10b',n=1000, N=5, dirx='raw/Oct10b',nm=200)
#     take_data(sTag='C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd500_fc1000_'+tTag, n=1000, N=5, dirx='Jan08_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd500_fc850_'+tTag, n=1000, N=5, dirx='Jan08_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd600_fc1020_'+tTag, n=1000, N=5, dirx='Jan08_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd700_fc1190_'+tTag, n=1000, N=5, dirx='Jan08_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd800_fc1360_'+tTag, n=1000, N=5, dirx='Jan08_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd900_fc1530_'+tTag, n=1000, N=5, dirx='Jan08_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8ch14_Gring1200mV_'+tTag, n=1000, N=5, dirx='Jan19_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8ch4_Ext30mV_Gring950mV_'+tTag, n=1000, N=1, dirx='Jan20_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8ch4_Gring924mV_'+tTag, n=1000, N=1, dirx='Jan20_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8ch4_Gring892mV_'+tTag, n=1000, N=1, dirx='Jan20_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='C8ch4_Ext30mV_'+tTag, n=1000, N=1, dirx='Jan20_TMS',nm=100, dir1='/data/TMS_data/raw/')

#       take_data(sTag='C7Ch5_alpha_Ar_12PSI_Pulse100Hz100mVpp_fc1500_fd1500_Oct271257',n=1000, N=-1, dirx='Oct27_TMS',nm=100, dir1='/data/TMS_data/raw/')
#       take_data(sTag='C7Ch5_gamma_Ar_12PSI_Pulse100Hz300mVpp_fc1500_fd1500_Oct271304',n=1000, N=-1, dirx='Oct27_TMS',nm=100, dir1='/data/TMS_data/raw/')
#     take_data(sTag='vessel_open',n=10, N=1, dirx='Oct27_TMS',nm=100, dir1='/data/TMS_data/raw/')

#       take_data(sTag='May13T1a',n=1000, N=-1, dirx='raw/May13T1a')
#       take_dataT(sTag='May14T1c',n=2000, Tmin = 30, dirx='raw/May14T1c')
    take_calibration()
#    take_data(sTag='Ext5p88F_A3_Ext5mV',n=1000, N=1, dirx='Jan23_TMS',nm=200)
#     take_data(sTag='Ext5p88F_A3_Extoff_Gring100mV',n=1000, N=1, dirx='Jan23_TMS',nm=200)
