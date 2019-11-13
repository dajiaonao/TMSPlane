#!/usr/bin/env python
'''The script is used to check the filter. And it should work in two modes:
    1. Real time mode. It take data and run the filter to see the effect.
    2. Offline mode.

    The paramter of the filter can be tuned from the command line
    '''
from __future__ import print_function
from __future__ import division
from TMS1mmX19Tuner import SensorConfig, CommonData
import socket
import array
import sys
import numpy as np
from command import *
from sigproc import *
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.INFO)
from ROOT import *
gROOT.LoadMacro("sp.C+")
from ROOT import SignalProcessor
from reco_config import apply_config


class filterChecker:
    def __init__(self, recoCfg=None):
        self.IsConnected = False
        self.filterPars = [100,200,900,500]
        self.chan = 0
        self.recoCfg = recoCfg
        self.nCh = 19
        self.nAdcCh = 20

    def connect(self):
        self.IsConnected = True
        logging.info("connected")

    def offline_check(self, fname='C0_tt2b_valid0.root'):
        nSamples = 16384

#         data1 = array.array('f',[0]*nData)
        s1 = SigProc(nSamples, self.nAdcCh, self.nCh, 5) 
        data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
        ret1  = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nAdcCh)()

        
        f1 = TFile(fname,'read')
        tree1 = f1.Get('tree1')
        tree1.SetBranchAddress('adc',data1)
        tree1.SetBranchAddress('ret',ret1)
        tree1.Show(0)

#         return

        ## plotting
        plt.ion()
        plt.show()
#         fig, ax1 = plt.subplots(1, 1, figsize=(28, 10))
        fig, ax1 = plt.subplots(1, 1, figsize=(11, 6))
    #     fig.set_size_inches(11,8)
        ax1.set_xlabel('time index')
        ax1.set_ylabel('U [V]', color='b')
        ax1.tick_params('y', colors='b')
        ax2 = ax1.twinx()
        ax2.set_ylabel('U [V]', color='r')
        ax2.tick_params('y', colors='r')


        W = self.filterPars[2]
        ## run the filter
        NVAL = 4
        t_values = array.array('f',[0]*(s1.nAdcCh*NVAL))
        sp1 = SignalProcessor()
        if self.recoCfg is not None: apply_config(sp1, self.recoCfg)
#         sp1.fltParam.clear()
#         for p in self.filterPars: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ### start checking
        entry = 0
        while entry>=0:
            ich = self.chan
            tree1.GetEntry(entry)
            print("ret:", ret1[ich])
            sp1.filter_channel(ich, data1)

            ax1.clear()
            ax2.clear()
            vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
            vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
            ax1.plot(vo, label='Raw', color='b')
            ax2.plot(vx, label='Filtered', color='r')

            ylim1 = ax1.get_ylim()
            ylim2 = ax2.get_ylim()
            x1 = min(ylim1[0], ylim2[0]+vo[0])
            x2 = max(ylim1[1], ylim2[1]+vo[0])
            ax1.set_xlim(0,nSamples)
            ax1.set_ylim(x1,x2)
            ax2.set_ylim(x1-vo[0],x2-vo[0])

            a1 = np.argmax(vx)
            x1 = [a1]
            y1 = [sp1.scrAry[a] for a in x1]
            ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')
            print(x1, y1)

            if a1<5000: a1 += 4000
            if a1>10000: a1 -= 4000
            dW = int(W/3)
            a2 = a1-dW if sp1.scrAry[a1-dW]>sp1.scrAry[a1+dW] else a1+dW
            x2 = [a2]
            y2 = [sp1.scrAry[a] for a in x2]
            ax2.scatter(x2,y2, c="y", marker='x', s=220, label='Analysis2')
            print(x2, y2)


            fig.tight_layout()
            plt.legend()
            plt.grid(True)
            plt.draw()

            ### decide the next entry
            entry = self.next(entry)

    def next(self, ievt):
        '''Decide the next entry interactively'''

        while True:
            x = raw_input("Next:")
            if x=='q': sys.exit()
            elif len(x)>0 and x[0] == 's':
                for name in x.split()[1:]:
                    dirx = os.path.dirname(name)
                    if not os.path.exists(dirx): os.makedirs(dirx)
                    plt.savefig(name)
                    print("saved figure to", name)
            elif len(x)>2 and x[:2] == 'ch':
                try:
                    ch_temp = int(x[2:]) 
                    if ch_temp<self.nAdcCh:
                        print("Switching to channel:", self.chan)
                        self.chan = ch_temp
                    else: print("Channel number out of range:", ch_temp, "Max:", self.nAdcCh-1)
                    break
                except ValueError:
                    continue
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break
        return ievt
 
    def online_check(self):
        if not self.IsConnected: self.connect()

        ## take data
        host='192.168.2.3'
        if socket.gethostname() == 'FPGALin': host = 'localhost'

        dataIpPort = (host+':1024').split(':')
        sD = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sD.connect((dataIpPort[0],int(dataIpPort[1])))

        ctrlIpPort = (host+':1025').split(':')
        sC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sC.connect((ctrlIpPort[0],int(ctrlIpPort[1])))

        cmd = Cmd()
        cd1 = CommonData(cmd, dataSocket=sD, ctrlSocket=sC)
        cd1.aoutBuf = 1 # AOUT buffer select, 0:AOUT1, 1:AOUT2, >1:disable both
        cd1.x2gain = 2 # BufferX2 gain 
        cd1.sdmMode = 0 # SDM working mode, 0:disabled, 1:normal operation, 2:test with signal injection 
        cd1.bufferTest = 0 #
        cd1.atTbounds = (4050,4150)

        s1 = cd1.sigproc
        data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()

        cd1.dataSocket.sendall(cd1.cmd.send_pulse(1<<2));
        buf = cd1.cmd.acquire_from_datafifo(cd1.dataSocket, cd1.nWords, cd1.sampleBuf)
        s1.demux_fifodata(buf, data1, cd1.sdmData)

        W = 900
        ## run the filter
        NVAL = 4
        t_values = array.array('f',[0]*(s1.nAdcCh*NVAL))
        sp1 = SignalProcessor()
        if self.recoCfg is not None: apply_config(sp1, self.recoCfg)
#         sp1.fltParam.clear()
#         for p in self.filterPars: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ich = self.chan
        sp1.filter_channel(ich, data1)

        ## plotting
        plt.ion()
        plt.show()
        fig, ax1 = plt.subplots(1, 1, figsize=(28, 10))
    #     fig.set_size_inches(11,8)
        ax1.set_xlabel('time index')
        ax1.set_ylabel('U [V]', color='b')
        ax1.tick_params('y', colors='b')
        ax2 = ax1.twinx()
        ax2.set_ylabel('U [V]', color='r')
        ax2.tick_params('y', colors='r')

        
        vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
        vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
        ax1.plot(vo, label='Raw', color='b')
        ax2.plot(vx, label='Filtered', color='r')

        ylim1 = ax1.get_ylim()
        ylim2 = ax2.get_ylim()
        x1 = min(ylim1[0], ylim2[0]+vo[0])
        x2 = max(ylim1[1], ylim2[1]+vo[0])
        ax1.set_ylim(x1,x2)
        ax2.set_ylim(x1-vo[0],x2-vo[0])

        a1 = np.argmax(vx)
        x1 = [a1]
        y1 = [sp1.scrAry[a] for a in x1]
        ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')
        print(x1, y1)

        if a1<5000: a1 += 4000
        if a1>10000: a1 -= 4000
        dW = int(W/3)
        a2 = a1-dW if sp1.scrAry[a1-dW]>sp1.scrAry[a1+dW] else a1+dW
        x2 = [a2]
        y2 = [sp1.scrAry[a] for a in x2]
        ax2.scatter(x2,y2, c="y", marker='x', s=220, label='Analysis2')
        print(x2, y2)

        fig.tight_layout()
        plt.legend()
        plt.grid(True)
        plt.draw()
        plt.pause(10)

def test1():
    fc1 = filterChecker()
#     fc1.online_check()
#     fc1.offline_check()
    fc1.offline_check('C0_tt2c_valid0.root')

if __name__ == '__main__':
    test1()
