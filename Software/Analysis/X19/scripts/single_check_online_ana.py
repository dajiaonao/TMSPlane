#!/usr/bin/env python36
'''This module does following:
    1. Show the waveshape for one of every 10 signal events;
    2. Apply the filter and extract the signal for every event;
    3. Show the basic results: A histogram of the charges in each event, the total charge as function of time.
'''
from __future__ import print_function
from ROOT import TFile, TTree
from array import array
from ROOT import gROOT
gROOT.LoadMacro("sp.C+")
from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent
from reco_config import apply_config
import numpy as np
# from matplotlib.figure import Figure
# import matplotlib
# matplotlib.use('pdf')
import matplotlib.pyplot as plt
import glob


class SingleChannelAnalysiser:
    def __init__(self):
        mode = 1 # mode 0: offline; 1: online. offline will end with end_of_file and online will be ended with the Cntrol-C

        self.data1 = array('f',[0]*(16384*20))
        self.T1 = array('i',[0])
        self.nShow = 200

        if self.nShow >= 0:
            plt.ion()
            plt.show()
            self.fig, self.ax1 = plt.subplots(1, 1, figsize=(10, 5))
            self.ax1.set_xlabel('time index')
            self.ax1.set_ylabel('U [V]', color='b')
            self.ax1.tick_params('y', colors='b')
            self.ax2 = self.ax1.twinx()
            self.ax2.set_ylabel('U [V]', color='r')
            self.ax2.tick_params('y', colors='r')

        self.sp1 = SignalProcessor()
        apply_config(self.sp1, 'Hydrogen/c3')
        self.ich = 19

    def process(self, pattern, mode):
        processed_files = []
        while True:
            files = [f for f in glob.glob(pattern) if f not in processed_files]

            for f in files:
                self.process_file(f)

            if mode == 1:
                processed_files += files
                continue
            else: break

    def process_file(self,inRoot):
        sp1 = self.sp1
        ich = self.ich

        ### need the file name pattern
        fout1 = TFile(inRoot,'read')
        self.tree1 = fout1.Get('tree1')
        self.tree1.SetBranchAddress('adc',self.data1)
        self.tree1.SetBranchAddress('T',self.T1)
        self.tree1.Show(0)

        ishow = 0
        ### keep trying to get the new entries
        ievt = 0
        run = 0
        while True:
            n = self.tree1.GetEntry(ievt)
            if n<=0: break

            sp1.filter_channel(ich, self.data1)
            sp1.find_sigs(ich)

            ievt += 1

            iss = 0
            if len(sp1.signals[ich])>0:
                print("idx: iMax iMidian A w0 w1 w2 T")
                print('-'*30)
            for s in sp1.signals[ich]:
                print (iss,':', s.idx, s.im, s.Q, s.w0, s.w1, s.w2, self.T1[0])
                iss += 1

            ### show
            if ishow == self.nShow:
                self.show_vaveform()

                va = self.data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
                vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
                vo = va

                self.ax1.clear()
                self.ax2.clear()
                self.ax1.plot(va, label='Raw', color='b')
                self.ax2.plot(vx, label='Filtered', color='r')
                ylim1 = self.ax1.get_ylim()
                ylim2 = self.ax2.get_ylim()

                x1 = min(ylim1[0], ylim2[0]+vo[0])
                x2 = max(ylim1[1], ylim2[1]+vo[0])
                self.ax1.set_ylim(x1,x2)
                self.ax2.set_ylim(x1-vo[0],x2-vo[0])

                x1 = []
                y1 = []
                iss = 0
                for s in sp1.signals[ich]:
                    x1.append(s.im)
                    y1.append(s.Q)
                    plt.axvline(x=s.im, linestyle='--', color='black')
                    iss += 1

                plt.text(0.04, 0.1, 'run {0:d} event {1:d}, ch {2:d}'.format(run, ievt, ich), horizontalalignment='center', verticalalignment='center', transform=self.ax2.transAxes)
                plt.xlim(auto=False)
                if x1: self.ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')

                self.fig.tight_layout()
                plt.draw()
                plt.legend()
                plt.grid(True)
                plt.pause(0.001)

                ishow = 0
            ishow += 1

    def run(self):
        ### need the file name pattern
        inRoot ='/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May13T1b/May13T1b_data_0.root' 
        fout1 = TFile(inRoot,'read')
        self.tree1 = fout1.Get('tree1')
        self.tree1.SetBranchAddress('adc',self.data1)
        self.tree1.SetBranchAddress('T',self.T1)
        self.tree1.Show(0)

        sp1 = SignalProcessor()
        apply_config(sp1, 'Hydrogen/c3')
        ich = 19


        ishow = 0
        ### keep trying to get the new entries
        ievt = 0
        run = 0
        while True:
            n = self.tree1.GetEntry(ievt)
            if n<=0: break

            sp1.filter_channel(ich, self.data1)
            sp1.find_sigs(ich)

            ievt += 1

            iss = 0
            if len(sp1.signals[ich])>0:
                print("idx: iMax iMidian A w0 w1 w2 T")
                print('-'*30)
            for s in sp1.signals[ich]:
                print (iss,':', s.idx, s.im, s.Q, s.w0, s.w1, s.w2, self.T1[0])
                iss += 1

            ### show
            if ishow == self.nShow:
                self.show_vaveform()

                va = self.data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
                vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
                vo = va

                self.ax1.clear()
                self.ax2.clear()
                self.ax1.plot(va, label='Raw', color='b')
                self.ax2.plot(vx, label='Filtered', color='r')
                ylim1 = self.ax1.get_ylim()
                ylim2 = self.ax2.get_ylim()

                x1 = min(ylim1[0], ylim2[0]+vo[0])
                x2 = max(ylim1[1], ylim2[1]+vo[0])
                self.ax1.set_ylim(x1,x2)
                self.ax2.set_ylim(x1-vo[0],x2-vo[0])

                x1 = []
                y1 = []
                iss = 0
                for s in sp1.signals[ich]:
                    x1.append(s.im)
                    y1.append(s.Q)
                    plt.axvline(x=s.im, linestyle='--', color='black')
                    iss += 1

                plt.text(0.04, 0.1, 'run {0:d} event {1:d}, ch {2:d}'.format(run, ievt, ich), horizontalalignment='center', verticalalignment='center', transform=self.ax2.transAxes)
                plt.xlim(auto=False)
                if x1: self.ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')

                self.fig.tight_layout()
                plt.draw()
                plt.legend()
                plt.grid(True)
                plt.pause(0.001)

                ishow = 0
            ishow += 1

            ### save to text file

    def show_vaveform(self):
        print("show waveform here")


def test():
    sca1 = SingleChannelAnalysiser()
#     sca1.run()
    sca1.process('/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May13T1b/May13T1b_data_*.root', mode=0)

if __name__ == '__main__':
    test()
