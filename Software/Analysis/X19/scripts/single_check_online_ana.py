#!/usr/bin/env python36
'''This module does following:
    1. Show the waveshape for one of every 10 signal events;
    2. Apply the filter and extract the signal for every event;
    3. Show the basic results: A histogram of the charges in each event, the total charge as function of time.
'''
from ROOT import TFile, TTree
from array import array
from ROOT import gROOT
gROOT.LoadMacro("sp.C+")
from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent
from reco_config import apply_config


class SingleChannelAnalysiser:
    def __init__(self):
        mode = 1 # mode 0: offline; 1: online. offline will end with end_of_file and online will be ended with the Cntrol-C

#         self.s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
#         self.data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
        self.data1 = array('f',[0]*(16384*20))
        self.nShow = -1


        pass
    def run(self):
        ### need the file name pattern
        inRoot ='/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/raw/May13T1a/May13T1a_data_0.root' 
        fout1 = TFile(inRoot,'read')
        self.tree1 = fout1.Get('tree1')
        self.tree1.SetBranchAddress('adc',self.data1)
        self.tree1.Show(0)

        sp1 = SignalProcessor()
        apply_config(sp1, 'Hydrogen/c3')
        ich = 19


        ishow = 0
        ### keep trying to get the new entries
        ievt = 0
        while True:
            n = self.tree1.GetEntry(ievt)
            if n<=0: break

            sp1.filter_channel(ich, self.data1)
            sp1.find_sigs(ich)

            ievt += 1

            iss = 0
            if len(sp1.signals[ich])>0:
                print("idx: iMax iMidian A w0 w1 w2")
                print('-'*30)
            for s in sp1.signals[ich]:
                print (iss,':', s.idx, s.im, s.Q, s.w0, s.w1, s.w2)
                iss += 1

        ### show
        if ishow == self.nShow:
            self.show_vaveform()
            ishow = 0
        ishow += 1

        ### save to text file

    def show_vaveform(self):
        print("show waveform here")


def test():
    sca1 = SingleChannelAnalysiser()
    sca1.run()

if __name__ == '__main__':
    test()
