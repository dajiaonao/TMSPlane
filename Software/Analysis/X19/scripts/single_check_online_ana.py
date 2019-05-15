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
import glob, os
import time


class SingleChannelAnalysiser:
    def __init__(self):
        mode = 1 # mode 0: offline; 1: online. offline will end with end_of_file and online will be ended with the Cntrol-C

        self.data1 = array('f',[0]*(16384*20))
        self.T1 = array('i',[0])
        self.nShow = 200
        self.dTx = 60

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
        self.totalQ = 0

    def process(self, pattern, mode):
        processed_files = []
        while True:
            try:
                files = [f for f in glob.glob(pattern) if f not in processed_files]

                for f in files:
                    self.process_file(f)

                if mode == 1:
                    processed_files += files
                    continue
                else: break
            except KeyboardInterrupt:
                break

    def process3(self, pattern, foutName='test.dat'):
        processed_files = []
        to_process = sorted([f for f in glob.glob(pattern)], key=lambda f:os.path.getmtime(f))

        with open(foutName,'w') as fout:
            while to_process:
                for f in to_process:
                    print("Processing",f)
                    if 0 == self.process_file(f, fout): processed_files.append(f)

                ### check and sort the remaining ones, so that the processed are excluded and old ones are processed first
                to_process = sorted([f for f in glob.glob(pattern) if f not in processed_files], key=lambda f:os.path.getmtime(f))

    def process2(self, pattern, excludeTmin=10):
        processed_files = []
        to_process = glob.glob(pattern)

        while to_process:
            waitT = None
            waitF = None
            for f in to_process:
                dT = time.time() - os.path.getmtime(f)
                if dT>excludeTmin:
                    self.process_file(f)
                    processed_files.append(f)
                elif waitT is None or dT<waitT:
                    waitT = dT ### wait for minimum time
                    waitF = f

            if waitT is not None:
                if waitT<60: waitT = 60
                print("Waiting for",f,"to finish.")
                time.sleep(waitT)
            to_process = [f for f in glob.glob(pattern) if f not in processed_files]

    def process_files(self,flist):
        for f in flist: self.process_file(f)

    def process_file(self,inRoot, fout=None):
        sp1 = self.sp1
        ich = self.ich
        run = -1
        try:
            run = int(inRoot.split('_')[-1][:-5])
        except:
            print(inRoot, inRoot.split('_')[-1][:-5])

        ### need the file name pattern
        fout1 = TFile(inRoot,'read')
        self.tree1 = fout1.Get('tree1')
        if not self.tree1:
            fout1.Close()
            return 1

        self.tree1.SetBranchAddress('adc',self.data1)
        self.tree1.SetBranchAddress('T',self.T1)
        self.tree1.Show(0)

        ishow = 0
        ### keep trying to get the new entries
        ievt = 0
        nTot = self.tree1.GetEntries()
        while ievt<nTot:
            self.tree1.GetEntry(ievt)

            sp1.filter_channel(ich, self.data1)
            sp1.find_sigs(ich)

            ievt += 1

            iss = 0
#             if len(sp1.signals[ich])>0:
#                 print("idx: iMax iMidian A w0 w1 w2 T")
#                 print('-'*30)
            for s in sp1.signals[ich]:
#                 print (iss,':', s.idx, s.im, s.Q, s.w0, s.w1, s.w2, self.T1[0])
                self.totalQ += s.Q
                fout.write('\n'+' '.join([str(self.T1[0]), str(s.Q), str(self.totalQ)]))
                if ievt%20 ==0: fout.flush()
                iss += 1

            ### show
            if ishow == self.nShow:
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

                plt.text(0.04, 0.01, 'run {0:d} event {1:d}, ch {2:d}'.format(run, ievt, ich), horizontalalignment='center', verticalalignment='center', transform=self.ax2.transAxes)
                plt.xlim(auto=False)
                if x1: self.ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')

                self.fig.tight_layout()
                plt.draw()
                plt.legend()
                plt.grid(True)
                plt.pause(0.001)

                ishow = 0

            ### update nTot if already the last one
            while ievt == nTot:
                self.tree1.Refresh()
                nTot = self.tree1.GetEntries()

                ### do not update any more if still get the same nubmer from an old-enough file
                if ievt == nTot:
                    dtx = self.dTx - (time.time() - os.path.getmtime(inRoot))
                    if dtx > 0:
                        if dtx < 1: dtx = 1
                        print("waiting for",inRoot, 'for', dtx,'seconds')
                        time.sleep(dtx)
                        continue
                    else:break
                else: break

            ishow += 1

        fout1.Close()
        return 0

def test():
    sca1 = SingleChannelAnalysiser()
#     sca1.run()
#     sca1.process('/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May13T1b/May13T1b_data_*.root', mode=0)
#     sca1.process('/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May13T1c/May13T1c_data_*.root', mode=0)
#     sca1.process2('/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May14T1a/May14T1a_data_*.root', 10)
    sca1.dTx = 5
    sca1.process3('/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May14T1c/May14T1c_data_*.root')

if __name__ == '__main__':
    test()
