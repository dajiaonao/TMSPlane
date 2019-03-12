#!/usr/bin/python2
#!/usr/bin/env python
import sys, os
from ctypes import *
from sigproc import SigProc 
from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent
from array import array
import re, time
from glob import glob

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import artist
# from process_signal import apply_wiener_filter
from scipy.signal import wiener
import cmath
from math import modf
from rootUtil import waitRootCmdX
from reco_config import apply_config

def apply_wiener_filter(data,ich,n=16384):
    x = [data[ich*n+i] for i in range(n)]
    m = np.mean(x)
#     y = wiener([a-m for a in x], mysize=500)
    y = wiener([a-m for a in x], mysize=500, noise=0.0003)
    for i in range(n): data[ich*n+i] = y[i]+m

class bkgEstimator:
    def __init__(self):
        self.data = None
        self.npoints = None
        self.F = 59
        self.T = 16384./self.F
        self.A = 1
        self.scale = 0.48
        self.get_data()
        print self.A, self.phase

    def get_data(self, evt=150):
        ch = TChain('tree1')
        ch.Add('data/fpgaLin/Feb09b_data_1881.root')
        n1 = ch.Draw('adc[19]','Entry$=={0:d}'.format(evt),'goff')
        v1 = ch.GetV1()
        x1 = np.array([v1[i] for i in range(n1)])

        n = int(n1/self.F)*2
        m1 = np.mean(x1)
        self.data = [np.mean(x1[i::n])-m1 for i in range(n)]
        self.npoints = n

        N = 16384
        self.Par = np.array([cmath.exp(-2*cmath.pi/N*59*k*1j) for k in range(N)])
        self.A, self.phase = self.get_phase(x1)

    def get_phase(self,x1):
        ### adding 1 to make sure it's positve
#         p = lambda x: 
#         return np.angle(sum(x1*self.Par))/(2*cmath.pi)+1
        a = sum(x1*self.Par)
        print a
        return np.abs(a)/self.A, np.angle(a)/(2.*cmath.pi)+1

    def correct(self, data,ich,n=16384): 
        A, phase = self.get_phase(data[ich*n:((ich+1)*n)])
#         scale = pow(A,2)
        scale = A
        print 'S,P:', scale, phase
#         print phase, self.phase1
#         a = modf(i/self.T+phase-self.phase1)[0]
#         if a<0: a+=1
#         b = int(a*self.T)
        for i in range(n):
#             print i/self.T+phase-self.phase
#             print modf(i/self.T+phase-self.phase)
#             print self.T*(modf(i/self.T+phase-self.phase)[0])
#             data[ich*n+i] -= self.scale*self.data[int(self.T*modf(i/self.T+phase-self.phase1)[0])]
            data[ich*n+i] -= scale*self.data[int(self.T*modf(i/self.T+phase-self.phase)[0])+20]

#         for i in range(n): data[ich*n+i] -= self.data[(i-phase+self.phase1)%self.npoints]
#         for i in range(n): data[ich*n+i] -= self.scale*self.data[int(i+phase-self.phase1)%self.npoints]

    def show_data(self):
        plt.plot(self.data)

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

def test2a():
#     be1 = bkgEstimator()
#     be1.show_data()

    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
    data1 = array('f',[0]*(16384*20))

#     pTag = 'Feb09b'
    pTag = 'Feb25a'
    tagA = 'data/fpgaLin/'+pTag+'_data_'
    inRoot = 'data/fpgaLin/'+pTag+'_data_1138.root'
    if len(sys.argv)>1:
        import os
        if os.path.exists(sys.argv[1]):
            inRoot = sys.argv[1]
        elif os.path.exists(tagA+sys.argv[1]+'.root'):
            inRoot = tagA+sys.argv[1]+'.root'
        else:
            files = sorted([f for f in glob(tagA+'*.root')], key=lambda f:os.path.getmtime(f))

            a =  -1
            try:
                a = int(sys.argv[1])
            except TypeError:
                pass
            if time.time() - os.path.getmtime(files[-1]) < 10:
                print "dropping the latest file, which probably is still being written:", files[-1]
                if a!=0: files.pop()
                else: a = -1

            if abs(a)<len(files):
                inRoot = files[a]
            else:
                print "Index {0:d} out of range:{1:d}".format(a, len(files))
                return

    print "Using file:", inRoot
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    print "Entries in the tree:", tree1.GetEntries()

    run = -1
    runPattern = '.*_data_(\d+).root'
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print "Run number not exatracted for file", iRoot

    i = 56
    ich = 1
    sp1 = SignalProcessor()
    sp1.fltParam.clear()

#     P is the constant using 0.2 ps as unit wit
#     0.006 is the constant using 1/2500/1024 as unit 1/0.006 T = 1/0.006 * 1/2500/1024 s = 1/0.006 *1/2500/1024* 5000000 pts
#     for x in [500, 500, 700, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 5, 15, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 50, 150, 2500]: sp1.fltParam.push_back(x)
#     for x in [30, 15, 50, 2500]: sp1.fltParam.push_back(x)
#     for x in [30, 50, 250, 2500]: sp1.fltParam.push_back(x)
    P = 1./0.006/2500/1024*5000000;
    for x in [30, 50, 200, P]: sp1.fltParam.push_back(x)
#     for x in [50, 100, 500, -1]: sp1.fltParam.push_back(x)
#     for x in [30, 5, 100, 2500]: sp1.fltParam.push_back(x)
#     for x in [30, 250, 350, 2500]: sp1.fltParam.push_back(x)
#     sp1.x_thre = 0.002
#     for i in range(20): sp1.ch_thre[i] = 0.002
#     sp1.ch_thre[19] = 0.05
    thre = [0.002]*sp1.nAdcCh
    thre[19] = 0.05
    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    plt.ion()
    fig,axs = plt.subplots(nrows=20, ncols=1, sharex=True, sharey=False, squeeze=True, figsize=(13, 12.5), dpi=72)
    plt.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.05, hspace=0, wspace=0)
    plt.show()


#     fig, ax1 = plt.subplots(1, 1, figsize=(28, 10))
#     fig.set_size_inches(11,8)
#     ax1.set_xlabel('time index')
#     ax1.set_ylabel('U [V]', color='b')
#     ax1.tick_params('y', colors='b')
#     ax2 = ax1.twinx()
#     ax2.set_ylabel('U [V]', color='r')
#     ax2.tick_params('y', colors='r')


#     for ievt in range(tree1.GetEntries()):

    NMax = tree1.GetEntries()
    ievt = 0
    while ievt< NMax:

        print "Event:", ievt
        tree1.GetEntry(ievt)

        for ich in range(sp1.nAdcCh):
            va = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
            sp1.measure_pulse2(data1, ich)

            vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
            vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]

            axs[ich].clear()
            axs[ich].plot(vo)

            tx = axs[ich].twinx()
            tx.clear()
            tx.plot(vx,color='r')
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
            elif len(x)>2 and x[:2] == 'ch':
                try:
                    ich = int(x[2:])
                    print "Switching to channel:", ich
                    break
                except ValueError:
                    continue
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break
            

#         fig.legend()
#
def test2b():
    be1 = bkgEstimator()
#     be1.show_data()

    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
    data1 = array('f',[0]*(16384*20))

#     pTag = 'Feb09b'
    pTag = 'Feb25a'
    tagA = 'data/fpgaLin/'+pTag+'_data_'
    inRoot = 'data/fpgaLin/'+pTag+'_data_1138.root'
    if len(sys.argv)>1:
        if os.path.exists(sys.argv[1]):
            inRoot = sys.argv[1]
        elif os.path.exists(tagA+sys.argv[1]+'.root'):
            inRoot = tagA+sys.argv[1]+'.root'
        else:
            files = sorted([f for f in glob(tagA+'*.root')], key=lambda f:os.path.getmtime(f))

            a =  -1
            try:
                a = int(sys.argv[1])
            except TypeError:
                pass
            if time.time() - os.path.getmtime(files[-1]) < 10:
                print "dropping the latest file, which probably is still being written:", files[-1]
                if a!=0: files.pop()
                else: a = -1

            if abs(a)<len(files):
                inRoot = files[a]
            else:
                print "Index {0:d} out of range:{1:d}".format(a, len(files))
                return

    print "Using file:", inRoot
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    print "Entries in the tree:", tree1.GetEntries()

    run = -1
    runPattern = '.*_data_(\d+).root'
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print "Run number not exatracted for file", iRoot

    i = 56
    ich = 1
    sp1 = SignalProcessor()
    apply_config(sp1, 'Hydrogen')

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
    prev_ievt = -1
    while ievt< NMax:
        if ievt != prev_ievt:
            print "Event:", ievt
            tree1.GetEntry(ievt)
            va = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
            prev_ievt = ievt

          ### FIXME: be careful, data1 might not be updated yet
#         be1.correct(data1, ich)
#         apply_wiener_filter(data1, ich)

        sp1.measure_pulse2(data1, ich)

        vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
        vo = va
#         vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]

        ax1.clear()
        ax2.clear()
        ax1.plot(va, label='Raw', color='b')
#         ax1.plot(vo, label='Wiener', color='g')
        ax2.plot(vx, label='Filtered', color='r')
#         ax2.plot([vo[i]-va[i] for i in range(sp1.nSamples)], label='Correction', color='k')
        ylim1 = ax1.get_ylim()
        ylim2 = ax2.get_ylim()

        x1 = min(ylim1[0], ylim2[0]+vo[0])
        x2 = max(ylim1[1], ylim2[1]+vo[0])
#         print x1,x2
        ax1.set_ylim(x1,x2)
        ax2.set_ylim(x1-vo[0],x2-vo[0])

#         print sp1.signals[ich].size()
        x1 = []
        y1 = []
        iss = 0
        if len(sp1.signals[ich])>0:
            print "idx: iMax iMidian A w0 w1 w2"
            print '-'*30
        for s in sp1.signals[ich]:
            print iss,':', s.idx, s.im, s.Q, s.w0, s.w1, s.w2
            x1.append(s.im)
            y1.append(s.Q)
            plt.axvline(x=s.im, linestyle='--', color='black')
            iss += 1

        plt.text(0.04, 0.1, 'run {0:d} event {1:d}, ch {2:d}'.format(run, ievt, ich), horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)
        plt.xlim(auto=False)
        if x1: ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')

        fig.tight_layout()
        plt.draw()
        plt.legend()
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
            elif len(x)>2 and x[:2] == 'ch':
                try:
                    ich = int(x[2:])
                    print "Switching to channel:", ich
                    break
                except ValueError:
                    continue
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break

#         fig.legend()
#         plt.show()


def test2():
    be1 = bkgEstimator()
#     be1.show_data()

    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
    data1 = array('f',[0]*(16384*20))

#     pTag = 'Feb09b'
    pTag = 'Feb25a'
    tagA = 'data/fpgaLin/'+pTag+'_data_'
    inRoot = 'data/fpgaLin/'+pTag+'_data_1138.root'
    if len(sys.argv)>1:
        if os.path.exists(sys.argv[1]):
            inRoot = sys.argv[1]
        elif os.path.exists(tagA+sys.argv[1]+'.root'):
            inRoot = tagA+sys.argv[1]+'.root'
        else:
            files = sorted([f for f in glob(tagA+'*.root')], key=lambda f:os.path.getmtime(f))

            a =  -1
            try:
                a = int(sys.argv[1])
            except TypeError:
                pass
            if time.time() - os.path.getmtime(files[-1]) < 10:
                print "dropping the latest file, which probably is still being written:", files[-1]
                if a!=0: files.pop()
                else: a = -1

            if abs(a)<len(files):
                inRoot = files[a]
            else:
                print "Index {0:d} out of range:{1:d}".format(a, len(files))
                return

    print "Using file:", inRoot
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    print "Entries in the tree:", tree1.GetEntries()

    run = -1
    runPattern = '.*_data_(\d+).root'
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print "Run number not exatracted for file", iRoot

    i = 56
    ich = 1
    sp1 = SignalProcessor()
    sp1.fltParam.clear()

#     P is the constant using 0.2 ps as unit wit
#     0.006 is the constant using 1/2500/1024 as unit 1/0.006 T = 1/0.006 * 1/2500/1024 s = 1/0.006 *1/2500/1024* 5000000 pts
#     for x in [500, 500, 700, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 5, 15, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 50, 150, 2500]: sp1.fltParam.push_back(x)
#     for x in [30, 15, 50, 2500]: sp1.fltParam.push_back(x)
#     for x in [30, 50, 250, 2500]: sp1.fltParam.push_back(x)
    P = 1./0.006/2500/1024*5000000;
    for x in [30, 50, 200, P]: sp1.fltParam.push_back(x)
#     for x in [50, 100, 500, -1]: sp1.fltParam.push_back(x)
#     for x in [30, 5, 100, 2500]: sp1.fltParam.push_back(x)
#     for x in [30, 250, 350, 2500]: sp1.fltParam.push_back(x)
#     sp1.x_thre = 0.002
#     for i in range(20): sp1.ch_thre[i] = 0.002
#     sp1.ch_thre[19] = 0.05
    thre = [0.002]*sp1.nAdcCh
    thre[19] = 0.05
    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

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

        va = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
#         be1.correct(data1, ich)
#         apply_wiener_filter(data1, ich)

        sp1.measure_pulse2(data1, ich)

        vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
        vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]

        ax1.clear()
        ax2.clear()
        ax1.plot(va, label='Raw', color='b')
#         ax1.plot(vo, label='Wiener', color='g')
        ax2.plot(vx, label='Filtered', color='r')
#         ax2.plot([vo[i]-va[i] for i in range(sp1.nSamples)], label='Correction', color='k')
        ylim1 = ax1.get_ylim()
        ylim2 = ax2.get_ylim()

        x1 = min(ylim1[0], ylim2[0]+vo[0])
        x2 = max(ylim1[1], ylim2[1]+vo[0])
#         print x1,x2
        ax1.set_ylim(x1,x2)
        ax2.set_ylim(x1-vo[0],x2-vo[0])

#         print sp1.signals[ich].size()
        x1 = []
        y1 = []
        iss = 0
        if len(sp1.signals[ich])>0:
            print "idx: iMax iMidian A w0 w1 w2"
            print '-'*30
        for s in sp1.signals[ich]:
            print iss,':', s.idx, s.im, s.Q, s.w0, s.w1, s.w2
            x1.append(s.im)
            y1.append(s.Q)
            plt.axvline(x=s.im, linestyle='--', color='black')
            iss += 1

        plt.text(0.04, 0.1, 'run {0:d} event {1:d}, ch {2:d}'.format(run, ievt, ich), horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)
        plt.xlim(auto=False)
        if x1: ax2.scatter(x1,y1, c="g", marker='o', s=220, label='Analysis')

        fig.tight_layout()
        plt.draw()
        plt.legend()
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
            elif len(x)>2 and x[:2] == 'ch':
                try:
                    ich = int(x[2:])
                    print "Switching to channel:", ich
                    break
                except ValueError:
                    continue
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break
            

#         fig.legend()
#         plt.show()

def test3():
    gStyle.SetOptStat(0)
    gROOT.ProcessLine('.L Pal.C')
    gStyle.SetPalette(55)
    gStyle.SetPadRightMargin(0.15)

#     from ROOT import Pal2
#     Pal2()

    '''To test the event reconstruction'''
    data1 = array('f',[0]*(16384*20))
    inRoot = 'data/fpgaLin/Feb27a_data_40.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    ### here comes the constructor
    sp1 = SignalProcessor()
    sp1.nAdcCh=20
    sp1.IO_adcData = data1

    sp1.fltParam.clear()
    for x in [30, 100, 300, -1]: sp1.fltParam.push_back(x)
    thre = [0.001]*sp1.nAdcCh
    thre[19] = 0.02

    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    Unit = 0.2
    h3 = TH3F('h3','h3;x [cm];y [cm];t [ps]',9,-1.8,1.8,9,-1.8,1.8,100,-1.*Unit*sp1.CF_uSize,Unit*sp1.CF_dSize)
    h2 = TH2F('h2','h2;t [ps];Channel;Q',(sp1.CF_uSize+sp1.CF_dSize),-1.*Unit*sp1.CF_uSize,Unit*sp1.CF_dSize,20,0,20)

    cx = TCanvas('cx','cx', 1500,700)
    cx.Divide(2,1)
    for i in range(tree1.GetEntries()):
        tree1.GetEntry(i)
        sp1.reco()

        for e in sp1.IO_evts:
            print e.trigID, len(e.sigs)
            h3.Reset()
            h2.Reset()
            showEvent(e, h3, h2)

            cx.cd(1)
            h3.Draw('BOX2')
            cx.cd(2)
            t = h2.GetBinContent(h2.GetMaximumBin())*1.06
            h2.GetZaxis().SetRangeUser(-0.05*t,t*0.95)
            h2.Draw('colz')
#             h2.Draw('axis same')

            cx.cd(0)
            waitRootCmdX()


def test3a():
    '''To test the event reconstruction'''
    data1 = array('f',[0]*(16384*20))
    inRoot = 'data/fpgaLin/Feb27a_data_40.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    i = 81
    tree1.GetEntry(i)

    ### here comes the constructor
    sp1 = SignalProcessor()
    sp1.nAdcCh=20
    sp1.IO_adcData = data1

    sp1.fltParam.clear()
    for x in [30, 100, 300, -1]: sp1.fltParam.push_back(x)
    thre = [0.001]*sp1.nAdcCh
    thre[19] = 0.02

    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    sp1.reco()
    Unit = 0.2
    h3 = TH3F('h3','h3;x [cm];y [cm];t [ps]',9,-1.8,1.8,9,-1.8,1.8,100,-1.*Unit*sp1.CF_uSize,Unit*sp1.CF_dSize)
#     for e in sp1.IO_evts:
    for e in sp1.get_events():
        print e.trigID, len(e.sigs)
        h3.Reset()
        showEvent(e, h3, h2)

        h3.Draw('BOX2Z')
        waitRootCmdX()
#         for j in range(sp1.nAdcCh): print j, e.sigs[j].im
#         d = [e.sigs[j].Q for j in range(sp1.nAdcCh)]
#         print d
#         showA(d)

    e1 = sp1.IO_evts[0]
    print dir(e1)
    print dir(e1.sigs[0])
    print '****', e1.sigs[0].im

    showEvents(sp1.IO_evts)

def showA(d):
    from ROOT import TH2Poly, gStyle
    gStyle.SetOptStat(0)

    hc = TH2Poly();
    hc.SetTitle("TMS19Plane");
    hc.Honeycomb(-4.3,-4,1,5,5);
    listA = [(0,0),(2,0),(1,1.5),(-1,1.5),(-2,0),(-1,-1.5),(1,-1.5),(4,0),(3,2),(1,3),(0,3),(-1,3),(-3,2),(-4,0),(-3,-2),(-1,-3),(0,-3),(1,-3),(3,-2)]

    for i in range(len(listA)):
       hc.Fill(listA[i][0],listA[i][1],d[i])

    hc.Draw("text colz0");
    raw_input('next:')

def test4():
    '''Test the measure_multiple function in sp.C, which trys to locate the signal by seaching the maximum and use the period info to find others. It's used used only for calibration.'''
    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
#     data1 = s1.generate_adcDataBuf() # ((ctypes.c_float * self.nSamples) * self.nAdcCh)()
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()

    sp = SignalProcessor()
    sp.fltParam.clear()
    for x in [30, 50, 200, -1]: sp.fltParam.push_back(x)
#     sp.IO_adcData = data1
#     sp.allocAdcData()
    sp.CF_chan_en.clear()
    sp.IO_mAvg.clear()
    for i in range(20):
        sp.CF_chan_en.push_back(1)
        sp.IO_mAvg.push_back(0.)

    inRoot = 'data/fpgaLin/Feb28t3_data_0.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    N = 2000 # 2500 Hz

    for ievt in range(1):
        tree1.GetEntry(ievt)
        sp.measure_multiple(data1, N)

#         print sp.IO_mAvg.size()
        print ievt, [sp.IO_mAvg[i] for i in range(20)] 

def test5():
    '''Test the measure_multipleX function in sp.C, which trys to locate the signal by seaching the maximum and use the period info to find others. It's used used only for calibration.'''
    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()

    sp = SignalProcessor()
    sp.fltParam.clear()

    P = 1./0.006/2500/1024*5000000;
    for x in [30, 50, 200, P]: sp.fltParam.push_back(x)

    sp.CF_chan_en.clear()
    sp.IO_mAvg.clear()
    for i in range(20):
        sp.CF_chan_en.push_back(1)
        sp.IO_mAvg.push_back(0.)

#     inRoot = 'data/fpgaLin/Feb28t3_data_0.root'
    inRoot = 'data/fpgaLin/Mar05T1a_data_0.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    N = 2000 # 2500 Hz

    Vs = array('f',[0]*(20*8))
#     for i in range(20*8)

    for ievt in range(3):
        tree1.GetEntry(ievt)
        sp.measure_multipleX(data1, N, Vs)

        for i in range(20):
            print i,':',
            for j in range(8):
#                 print i*8+j,
                print Vs[i*8+j],
            print



if __name__ == '__main__':
#     test2()
#     test2b()
    test2a()
#     test5()
#     test4()
#     test3()
