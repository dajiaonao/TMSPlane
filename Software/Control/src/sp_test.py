#!/usr/bin/env python
import sys, os
from ctypes import *
from sigproc import SigProc 
from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor
from array import array

import numpy as np
import matplotlib.pyplot as plt

def test1():
    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    # data1 = s1.generate_adcDataBuf()
    # data2 = s1.generate_sdmDataBuf()
    # data1 = ((s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nSamples) * s1.nAdcCh)()
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
    # data1 = ((s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nSamples) * s1.nAdcCh)()
    # print len(data1[0])
    print type(data1)
    # print type(byref(data1[0]))
    print type(pointer(data1))
    data1 = array('f',[0]*(16384*20))
    inRoot = 'data/fpgaLin/Feb09b_data_581.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    i = 37
    tree1.GetEntry(i)
    # print data1[3]

    sp1 = SignalProcessor()
    sp1.nAdcCh=20
    # sp1.sRanges.clear()
    # sp1.sRanges.push_back((0,3000))
    # sp1.sRanges.push_back((3000,8000))
    # sp1.sRanges.push_back((8000,15000))
    # sp1.measure_pulse(byref(data1))
    # sp1.measure_pulse(pointer(data1))
    # sp1.measure_pulse(data1)
    print sp1.nMeasParam

    f = 1000
    a = 16384*0.2*f*0.000001
    print 16384*0.2*f*0.000001
    n1 = int(1/(0.2*f*0.000001))
    print n1
    sp1.sRanges.clear()
    ip = 0
    while ip+n1<sp1.nSamples:
        iq = ip+n1
    #     if iq > sp1.nSamples: iq = sp1.nSamples
    #     a = (ip, iq)
        sp1.sRanges.push_back((ip, iq))
        ip = iq
    #
    sp1.measure_pulse(data1)
    for i in range(sp1.nAdcCh):
    #     print i, sp1.measParam[sp1.nMeasParam*i], sp1.measParam[sp1.nMeasParam*i+1], sp1.measParam[sp1.nMeasParam*i+2], sp1.measParam[sp1.nMeasParam*i+3]
        print i,
        for j in range(sp1.nMeasParam):
            print sp1.measParam[sp1.nMeasParam*i+j],
        print
    sp1.test2()

def test2():
    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
    data1 = array('f',[0]*(16384*20))
    inRoot = 'data/fpgaLin/Feb09b_data_847.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    i = 56
    ich = 19
    sp1 = SignalProcessor()
    sp1.fltParam.clear()
    for x in [500, 250, 500, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 50, 150, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 15, 50, 2500]: sp1.fltParam.push_back(x)

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

#     for ievt in range(tree1.GetEntries()):

    NMax = tree1.GetEntries()
    ievt = 0
    while ievt< NMax:

        print "Event:", ievt
        tree1.GetEntry(ievt)
        sp1.measure_pulse2(data1, ich)

        vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
        vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]

        ax1.clear()
        ax2.clear()
        ax1.plot(vo, label='Raw', color='b')
        ax2.plot(vx, label='Filtered', color='r')

        print sp1.signals[ich].size()
        x1 = []
        y1 = []
        for s in sp1.signals[ich]:
            print s.idx, s.im, s.Q, s.w0, s.w1, s.w2
            x1.append(s.im)
            y1.append(s.Q)
            plt.axvline(x=s.im, linestyle='--', color='black')

#         if x1: ax2.scatter(x1,y1, label='Analysis')

        fig.tight_layout()
        plt.draw()
        plt.grid(True)
        plt.pause(0.001)

        while True:
            x = raw_input("Next:")
            if x=='q': sys.exit()
            elif len(x)>0 and x[0] == 's':
                for name in x.split()[1:]:
                    dirx = os.path.dirname(name)
                    if not os.path.exists(dirx): os.makedirs(dirx)
                    plt.savefig(name)
                    print "saved figure to", name
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break
            

#         fig.legend()
#         plt.show()

if __name__ == '__main__':
    test2()
