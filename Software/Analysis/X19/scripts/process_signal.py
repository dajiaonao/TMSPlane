#!/usr/bin/env python3
# from SignalChecker import SignalChecker
import numpy as np
from ROOT import gROOT, TChain, TFile, TNtuple
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor
from array import array

from multiprocessing import Pool
from glob import glob
import os, time, re
import socket
# from scipy.signal import wiener
import cmath
from check_decay import FilterConfig
from reco_config import apply_config
from math import sqrt


def parse_args(argX):
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    oDir = args[2] if len(args)>2 else os.path.dirname(inRoot)
    if oTag.find('/') != -1:
        oDir = os.path.dirname(oTag)
        oTag = os.path.basename(oTag)

    return inRoot,oTag,oDir

def get_number(pattern, filename):
    ### run info
    run = -1
    if pattern is not None:
        m = re.match(pattern, filename)
        if m: run = int(m.group(1))
    return run

def process_pulse(argX, runPattern='.*_data_(\d+).root'):
    '''Based on readSignal2b. Find signal in a range, meant for pulse calibration, for which you know where the signal is expected.'''
    inRoot, oTag, oDir = parse_args(argX)
    print(("Starting", inRoot, oTag))

    ### run info
    run = get_number(runPattern, inRoot)

    sp1 = SignalProcessor(16384,20)
    apply_config(sp1, 'Lithium/c')
   
    ### special configuration not given in the reco_config
    sp1.sRanges.clear()
#     sp1.sRanges.push_back((3500, 3501))
    sp1.sRanges.push_back((2950, 2951))

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])
    dataV = array('I',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')

    if tree1 is None:
        print('Problem to get the tree in', inRoot, 'skipping it')
        return
    try:
        tree1.SetBranchAddress('adc',data1)
        tree1.SetBranchAddress('T',dataT)
        tree1.SetBranchAddress('V',dataV)
    except TypeError:
        print(inRoot)

    fout1 = TFile(oDir+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:sID:ch:B:dB:im:idx:A:T:dV')

    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse(data1)
        for i in range(sp1.nAdcCh):
            itmp = sp1.nMeasParam*i
            if sp1.nMeasParam%2 != 0: print(sp1.nMeasParam, inRoot, ievt)
            for j in range(int(sp1.nMeasParam/2)-1):
                tup1.Fill(run, ievt, i, sp1.measParam[itmp], sp1.measParam[itmp+1], j, sp1.measParam[itmp+2*j+2], sp1.measParam[itmp+2*j+3], dataT[0]-788947200, dataV[0])

    tup1.Write()
    fout1.Close()

def process_event(argX, runPattern='.*_data_(\d+).root'):
    '''Based on 5b and process_pulse, using new '''
    inRoot, oTag, oDir = parse_args(argX)
    print(("Starting", inRoot, oTag))

    ### run info
    run = get_number(runPattern, inRoot)

    sp1 = SignalProcessor()
    #apply_config(sp1, 'Lithium/d')
    apply_config(sp1, 'Lithium/C7_shortA')

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')

    tree2 = 0
    outRoot = oDir+'/'+oTag+os.path.basename(inRoot)
    tf = sp1.processFile(tree1, tree2, outRoot, run)
    tf.Close()

class bkgEstimator:
    def __init__(self):
        self.data = None
        self.npoints = None
        self.F = 59
        self.T = 16384/self.F
        self.get_data()
        self.scale = 0.6

    def get_data(self, evt=20):
        ch = TChain('tree1')
        ch.Add('data/fpgaLin/Feb09b_data_1881.root')
        n1 = ch.Draw('adc[19]','Entry$=={0:d}'.format(evt),'goff')
        v1 = ch.GetV1()
        x1 = np.array([v1[i] for i in range(n1)])

        n = int(n1/self.F)
        m1 = np.mean(x1)
        self.data = [np.mean(x1[i::n])-m1 for i in range(n)]
        self.npoints = n

        N = 16384
        self.Par = np.array([cmath.exp(-2*cmath.pi/N*59*k*1j) for k in range(N)])
        self.phase1 = int(self.get_phase(x1))

    def get_phase(self,x1):
        return np.angle(sum(x1*self.Par))/(2*cmath.pi)*self.T

    def correct(self, data,ich,n=16384): 
        phase = int(self.get_phase(data[ich*n:((ich+1)*n)]))
#         print phase, self.phase1
#         for i in range(n): data[ich*n+i] -= self.data[(i-phase+self.phase1)%self.npoints]
        for i in range(n): data[ich*n+i] -= self.scale*self.data[(i+phase-self.phase1)%self.npoints]

    def show_data(self):
        plt.plot(self.data)

def apply_wiener_filter(data,ich,n=16384):
    print("Doing nothing....")
    return
    x = [data[ich*n+i] for i in range(n)]
#     y = wiener(x, mysize=500)
    for i in range(n): data[ich*n+i] = y[i]

def readSignal5a(argX, runPattern='.*_data_(\d+).root'):
    '''Based on readSignal4c; for single channel. Pulse processing'''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f.*.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
    apply_config(sp1, 'TEST1')


    ### IO configuration
    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)

    fout1 = TFile(os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:evt:ch:B:dB:iA:imean:imax:A:w0:w1:w2:T:dV')
    a = TObjString("filter:"+str(sp1.fltParam))
    a.Write('Info')

    chs = [10]
    chx = chs[0] if (chs and len(chs)==1) else -1
    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse2(data1, chx)
        for ich in range(sp1.nAdcCh):
            if chs and (ich not in chs): continue
            ss = sp1.signals[ich]

            itmp = sp1.nMeasParam*ich
            iA = 0
            for ii in ss:
                tup1.Fill(run, ievt, ich, sp1.measParam[itmp], sp1.measParam[itmp+1],iA,ii.im,ii.idx,ii.Q,ii.w0,ii.w1,ii.w2,dataT[0]-788947200,dV)
                iA += 1

    tup1.Write()
    fout1.Close()




def readSignal4a(argX, runPattern='.*_data_(\d+).root'):
    '''Use non default time window'''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
#     for i in range(sp1.nAdcCh): sp1.ch_thre[i] = 0.002
#     sp1.ch_thre[19] = 0.05
    thre = [0.002]*sp1.nAdcCh
    thre[2] = 0.0008
    thre[4] = 0.001
    thre[6] = 0.001
    thre[7] = 0.001
    thre[10] = 0.001
    thre[11] = 0.0007
    thre[14] = 0.0007
    thre[17] = 0.001
    thre[19] = 0.05

    sp1.CF_uSize = 600
    sp1.CF_dSize = 1100

    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    sp1.CF_chan_en.clear()
    for i in range(20): sp1.CF_chan_en.push_back(1)

    flt = [50, 100, 500, -1] # dp01a
    for x in flt: sp1.fltParam.push_back(x)

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')

    tree2 = 0
    outRoot = os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot)
    tf = sp1.processFile(tree1, tree2, outRoot, run)
    tf.Close()

def readSignal4d(argX, runPattern='.*_data_(\d+).root'):
    '''Based on readSignal4c; Take the dV from the tuple instead of the input file name.'''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    oDir = args[2] if len(args)>2 else os.path.dirname(inRoot)
    if oTag.find('/') != -1:
        oDir = os.path.dirname(oTag)
        oTag = os.path.basename(oTag)
    print(("Starting", inRoot, oTag))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
    apply_config(sp1, 'Lithium/b')

    ### IO configuration
    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])
    dataV = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)
    tree1.SetBranchAddress('V',dataV)

    fout1 = TFile(oDir+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:evt:ch:B:dB:iA:imean:imax:A:w0:w1:w2:T:dV')
    a = TObjString("filter:"+str(sp1.fltParam))
    a.Write('Info')

#     chs = [1,5]
    chs = [i for i in range(19)]
    chx = chs[0] if (chs and len(chs)==1) else -1
    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse2(data1, chx)
        for ich in range(sp1.nAdcCh):
            if chs and (ich not in chs): continue
            ss = sp1.signals[ich]

            itmp = sp1.nMeasParam*ich
            iA = 0
            for ii in ss:
                tup1.Fill(run, ievt, ich, sp1.measParam[itmp], sp1.measParam[itmp+1],iA,ii.im,ii.idx,ii.Q,ii.w0,ii.w1,ii.w2,dataT[0]-788947200,dataV[0])
                iA += 1

    tup1.Write()
    fout1.Close()

def readSignal4c(argX, runPattern='.*_data_(\d+).root'):
    '''Based on readSignal4b; for single channel. And IO is from readSignal3'''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
#     apply_config(sp1, 'Hydrogen')
#     apply_config(sp1, 'Helium')
    apply_config(sp1, 'Lithium')

    ### IO configuration
    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)

    fout1 = TFile(os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:evt:ch:B:dB:iA:imean:imax:A:w0:w1:w2:T:dV')
    a = TObjString("filter:"+str(sp1.fltParam))
    a.Write('Info')

#     chs = [0]
    chs = [i for i in range(19)]
    chx = chs[0] if (chs and len(chs)==1) else -1
    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse2(data1, chx)
        for ich in range(sp1.nAdcCh):
            if chs and (ich not in chs): continue
            ss = sp1.signals[ich]

            itmp = sp1.nMeasParam*ich
            iA = 0
            for ii in ss:
                tup1.Fill(run, ievt, ich, sp1.measParam[itmp], sp1.measParam[itmp+1],iA,ii.im,ii.idx,ii.Q,ii.w0,ii.w1,ii.w2,dataT[0]-788947200,dV)
                iA += 1

    tup1.Write()
    fout1.Close()

def readSignal5b(argX, runPattern='.*_data_(\d+).root'):
    '''Based on 4b, using new '''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    oDir = args[2] if len(args)>2 else os.path.dirname(inRoot)
    if oTag.find('/') != -1:
        oDir = os.path.dirname(oTag)
        oTag = os.path.basename(oTag)
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
#     apply_config(sp1, 'Hydrogen')
#     apply_config(sp1, 'Hydrogen/c3')
#     apply_config(sp1, 'Helium')
    apply_config(sp1, 'Lithium/c')

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')

    tree2 = 0
    outRoot = oDir+'/'+oTag+os.path.basename(inRoot)
    tf = sp1.processFile(tree1, tree2, outRoot, run)
    tf.Close()


def readSignal4b(argX, runPattern='.*_data_(\d+).root'):
    '''For Mar08 data processing, take the decay time from configuration file'''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
#     apply_config(sp1, 'Hydrogen')
#     apply_config(sp1, 'Hydrogen/c3')
#     apply_config(sp1, 'Helium')
    apply_config(sp1, 'Lithium/c')

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')

    tree2 = 0
    outRoot = os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot)
    tf = sp1.processFile(tree1, tree2, outRoot, run)
    tf.Close()

def readSignal4(argX, runPattern='.*_data_(\d+).root'):
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
#     for i in range(sp1.nAdcCh): sp1.ch_thre[i] = 0.002
#     sp1.ch_thre[19] = 0.05
    thre = [0.002]*sp1.nAdcCh
    thre[2] = 0.0008
    thre[4] = 0.001
    thre[6] = 0.001
    thre[7] = 0.001
    thre[10] = 0.001
    thre[11] = 0.0007
    thre[14] = 0.0007
    thre[17] = 0.001
    thre[19] = 0.05

    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    sp1.CF_chan_en.clear()
    for i in range(20): sp1.CF_chan_en.push_back(1)

    flt = [50, 100, 500, -1] # dp01a
    for x in flt: sp1.fltParam.push_back(x)

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')

    tree2 = 0
    outRoot = os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot)
    tf = sp1.processFile(tree1, tree2, outRoot, run)
    tf.Close()

def readSignal3(argX, runPattern='.*_data_(\d+).root'):
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_f\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### data check
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print(("Run number not exatracted for file", iRoot))
                return
        else:
            if dV<0:
                print(("Run number not exatracted for file", iRoot))
                return

    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
#     for i in range(sp1.nAdcCh): sp1.ch_thre[i] = 0.002
#     sp1.ch_thre[19] = 0.05
    thre = [0.002]*sp1.nAdcCh
    thre[2] = 0.0008
    thre[4] = 0.001
    thre[6] = 0.001
    thre[7] = 0.001
    thre[10] = 0.001
    thre[11] = 0.0007
    thre[14] = 0.0007
    thre[17] = 0.001
    thre[19] = 0.05

    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    # sp3a
#     for x in [30, 15, 50, 2500]: sp1.fltParam.push_back(x)
#     flt = [50, 50, 250, 2500]
#     flt = [50, 50, 150, -1]
    flt = [50, 100, 500, -1] # dp01a
#     flt = [30, 250, 350, 2500]
#     flt = [50, 10, 150, 2500]
#     flt = [50, 500, 600, 2500]
#     flt = [50, 5, 100, 2500]
    for x in flt: sp1.fltParam.push_back(x)

    # sp3b
#     for x in [50, 500, 700, 2500]: sp1.fltParam.push_back(x)

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)

    fout1 = TFile(os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:evt:ch:B:dB:iA:imean:imax:A:w0:w1:w2:T:dV')
    a = TObjString("filter:"+str(flt))
    a.Write('Info')

    ### for background subtraction
    be1 = bkgEstimator()

#     chs = [19]
    chs = None
    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

#         apply_wiener_filter(data1, ich=19)
#         be1.correct(data1, 19)


        sp1.measure_pulse2(data1)
        for ich in range(sp1.nAdcCh):
            if chs and (ich not in chs): continue
#             print "processing channle", ich
            ss = sp1.signals[ich]

            itmp = sp1.nMeasParam*ich
            iA = 0
            for ii in ss:
                tup1.Fill(run, ievt, ich, sp1.measParam[itmp], sp1.measParam[itmp+1],iA,ii.im,ii.idx,ii.Q,ii.w0,ii.w1,ii.w2,dataT[0]-788947200,dV)
                iA += 1

    tup1.Write()
    fout1.Close()


def readSignal2a(argX, runPattern='.*_data_(\d+).root'):
    '''Based on readSignal2, but only one range'''
    args = argX.split(';')
    inRoot = args[0]
    oTag = args[1]
    print(("Starting", inRoot, oTag))

    ### pulse test
    dV = -1
    dvPattern = '.*_(\d+)mV_data_\d+.root'
    m = re.match(dvPattern, inRoot)
    if m:
        try:
            dV = int(m.group(1))
        except ValueError:
            print(("Failed to get the dV in file:", iRoot))

    ### run info
    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            run = int(m.group(1))
    print(run)

    sp1 = SignalProcessor(16384,20)
    apply_config(sp1, 'Lithium')
   
    ### special configuration not given in the reco_config
    sp1.sRanges.clear()
    sp1.sRanges.push_back((3500, 3501))

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)

    fout1 = TFile(os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:sID:ch:B:dB:im:idx:A:T:dV')

    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse(data1)
        for i in range(sp1.nAdcCh):
            itmp = sp1.nMeasParam*i
            for j in range(sp1.nMeasParam/2-1):
                tup1.Fill(run, ievt, i, sp1.measParam[itmp], sp1.measParam[itmp+1], j, sp1.measParam[itmp+2*j+2], sp1.measParam[itmp+2*j+3], dataT[0]-788947200, dV)

    tup1.Write()
    fout1.Close()

def readSignal2(inRoot, oTag=None, freq=1000, runPattern='.*_data_(\d+).root'):
    '''Write out root file and add more info'''
    if oTag is None:
        oTag = readSignal2.oTag
    print(("Starting", inRoot, oTag))
#     return

    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            run = int(m.group(1))
    print(run)

    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
    for x in [50, 150, 250, 2500]: sp1.fltParam.push_back(x)
#     for x in [50, 150, 200, -1.]: sp1.fltParam.push_back(x)
#     for x in [50, 150, 200, 2500]: sp1.fltParam.push_back(x)
#     for x in [50, 15, 50, 2500]: sp1.fltParam.push_back(x)
#     for x in [500, 450, 800, 2500]: sp1.fltParam.push_back(x)

    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    dn = 2500%n1 ## 2500 is the expected position of the signal
#     while ip+dn < sp1.nSamples:
#         sp1.sRanges.push_back((ip, min(ip+n1, sp1.nSamples)))
#         ip += n1

#     sp1.sRanges.push_back((0, 400))
    sp1.sRanges.push_back((0, 3000))

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)

    fout1 = TFile(os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:sID:ch:B:dB:im:idx:A:T')

    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse(data1)
        for i in range(sp1.nAdcCh):
            itmp = sp1.nMeasParam*i
            for j in range(sp1.nMeasParam/2-1):
                tup1.Fill(run, ievt, i, sp1.measParam[itmp], sp1.measParam[itmp+1], j, sp1.measParam[itmp+2*j+2], sp1.measParam[itmp+2*j+3], dataT[0]-788947200)

    tup1.Write()
    fout1.Close()

def readSignal(inRoot, outText, freq=1000):
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
    for x in [50, 150, 200, -1.]: sp1.fltParam.push_back(x)

    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    dn = 2500%n1 ## 2500 is the expected position of the signal
#     while ip+dn < sp1.nSamples:
#         sp1.sRanges.push_back((ip, min(ip+n1, sp1.nSamples)))
#         ip += n1

    sp1.sRanges.push_back((0, 400))
#     while ip+n1<sp1.nSamples:
#         sp1.sRanges.push_back((ip, ip+n1))
#         ip += n1

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))

#     inRoot = 'data/fpgaLin/Jan21b_C2_100mV_f1000.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    with open(outText,'w') as fout:
        fout.write(':'.join(['sID/I', 'ch/I', 'B/F','dB/F', 'im/I','idx/I','A/F']))

        for ievt in range(tree1.GetEntries()):
            tree1.GetEntry(ievt)

            sp1.measure_pulse(data1)
            for i in range(sp1.nAdcCh):
                itmp = sp1.nMeasParam*i
                for j in range(sp1.nMeasParam/2-1):
                    fout.write('\n'+' '.join([str(ievt), str(i), str(sp1.measParam[itmp]), str(sp1.measParam[itmp+1]), str(j), str(int(sp1.measParam[itmp+2*j+2])), str(sp1.measParam[itmp+2*j+3])]))


def check_Jan22a(f):
    tag1 = 'data/fpgaLin/Jan22a_C2_100mV_'
    readSignal(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f), f)

def testK():
    p = Pool(4)
    p.map(check_Jan22a, [100,200,500,1000])


def check_Jan22b(v):
    tag1 = 'data/fpgaLin/Jan22b_C2_{0:d}mV_f1000'.format(v)
    readSignal(tag1+'.root', tag1+".dat", 1000)

def test_Jan22b():
    p = Pool(6)
#     p.map(check_Jan22b, [50+50*i for i in range(10)])
#     p.map(check_Jan22bx, glob('data/fpgaLin/Jan22b_C2_*5mV*.root'))
#     p.map(check_Jan22bx, glob('data/fpgaLin/Jan24a_C2_*.root'))
    p.map(check_Jan22bx, glob('data/fpgaLin/Jan25a_C2_*.root'))

def test_Feb06c(oTag):
    p = Pool(6)

    files = sorted([f for f in glob('data/fpgaLin/Feb06c_data_*.root') if not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))], key=lambda f:os.path.getmtime(f))
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

#     p.map(check_Jan22bx, files)
#     p.map(check_Jan22by, files)
    p.map(readSignal2, files)
# readSignal2.oTag = 'sp2_'

def test_Feb09(oTag):
    p = Pool(6)

    files = sorted([f for f in glob('data/fpgaLin/Feb09*_data_*.root') if not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))], key=lambda f:os.path.getmtime(f))
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

#     p.map(check_Jan22bx, files)
#     p.map(check_Jan22by, files)
    p.map(readSignal2, files)
readSignal2.oTag = 'sp2_'

def test_Feb09b(oTag):
    p = Pool(6)

    files = sorted([f for f in glob('data/fpgaLin/Feb09b*_data_*.root') if not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))], key=lambda f:os.path.getmtime(f))
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

    p.map(readSignal3, [f+';'+oTag for f in files])

def check_Jan22by(fname):
    tag = 'sp_'
    print(("Starting", fname, tag))
    readSignal2(fname, tag, 1000)

def check_Jan22bx(fname):
    out = fname[:-5]+'.dat'
    print(("Starting", fname, out))
    readSignal(fname, out, 1000)

# def testJ():
#     sc1 = SignalChecker()
#     sc1.control_ip_port = "localhost:1024"
#     dir1 = 'data/fpgaLin/'
#     tag1 = dir1+'Jan22a_C2_100mV_'
#     for f in [100,200,500,1000]:
# #         setPulse(0.1,f)
# #         time.sleep(20)
# #         sc1.take_samples2(5000, tag1+"f{0:d}.root".format(f))
# #         if f not in [1000]: continue
# #         sc1.check_enc2(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f))
#         readSignal(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f), f)
def testJ():
    from SignalChecker import SignalChecker
    sc1 = SignalChecker()
    sc1.control_ip_port = "localhost:1024"
    dir1 = 'data/fpgaLin/'
    tag1 = dir1+'Jan22a_C2_100mV_'
    for f in [100,200,500,1000]:
#         setPulse(0.1,f)
#         time.sleep(20)
#         sc1.take_samples2(5000, tag1+"f{0:d}.root".format(f))
#         if f not in [1000]: continue
#         sc1.check_enc2(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f))
        readSignal(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f), f)

def check_calib():
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20

    ### setup the calibration file
#     fin1 = TFile('fout_calib.root')
    fin1 = TFile('fout_calib.root')
    sp1.corr_spine.clear()
    sp1.corr_TF1.clear()
    sp1.corr_spine.reserve(sp1.nAdcCh)
    sp1.corr_TF1.reserve(sp1.nAdcCh)
    for i in range(sp1.nAdcCh-1):
        sp1.corr_spine.push_back(fin1.Get('gr_calib_ch'+str(i)))
        sp1.corr_TF1.push_back(sp1.corr_spine[i].GetFunction('pol1'))
    
    ## run a test
    for x in sp1.corr_spine[5].GetX():
        t = 1
        print((sp1.correction(1,x)*t, sp1.correction(1,x, 1)*t, '|', sp1.correction(5,x)*t, sp1.correction(5,x, 1)*t))

def test3(pList, pTag='Feb25a', skipExist=True):
    tasks = []
    for p in pList:
        r = p[0]
        while True:
            fname = 'data/fpgaLin/'+pTag+'_data_{0:d}.root'.format(r)
            r +=1

            if skipExist:
                if os.path.exists(fname.replace('/Feb','/'+p[1]+'Feb')): continue
            if not os.path.exists(fname) or time.time() - os.path.getmtime(fname) < 10: break

            tasks.append(fname+';'+p[1])

            if len(p)>2 and r>p[2]: break

    p = Pool(6)
    p.map(readSignal3, tasks)

def process_all_match(pattern, oTag, skipExist=True):
    files = sorted([f for f in glob(pattern) if ((not skipExist) or (not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))))], key=lambda f:os.path.getmtime(f))
    if len(files)==0:
        print("No files matchs.... Aborting...")
        return
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

    p = Pool(6)
    p.map(readSignal3, [f+';'+oTag for f in files])

def process_all_match4(pattern, oTag, skipExist=True):
    files = sorted([f for f in glob(pattern) if ((not skipExist) or (not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))))], key=lambda f:os.path.getmtime(f))
    if len(files)==0:
        print("No files matchs.... Aborting...")
        return
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

    p = Pool(6)
    p.map(readSignal4, [f+';'+oTag for f in files])

def process_all_matchX(funX, pattern, oTag, skipExist=True, nThread=6):
#     files = sorted([f for f in glob(pattern) if ((not skipExist) or (not os.path.exists(f.replace('/Mar','/'+oTag+'Mar'))))], key=lambda f:os.path.getmtime(f))
#     print(glob(pattern))
    files = sorted([f for f in glob(pattern) if ((not skipExist) or (not os.path.exists(oTag+os.path.basename(f))))], key=lambda f:os.path.getmtime(f))
    if len(files)==0:
        print("No files matchs.... Aborting...")
        return
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

    p = Pool(nThread)
    p.map(funX, [f+';'+oTag for f in files])

def process_all_matchY(funX, pattern, oTag, skipExist=True):
    files = sorted([f for f in glob(pattern) if ((not skipExist) or (not os.path.exists(f.replace('/Nov','/'+oTag+'Nov'))))], key=lambda f:os.path.getmtime(f))
    if len(files)==0:
        print("No files matchs.... Aborting...")
        return
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print(("dropping the latest file, which probably is still being written:", files[-1]))
        files.pop()

    for a in [f+';'+oTag for f in files]: funX(a)


if __name__ == '__main__':
    nThread = 6 if socket.gethostname() == 'eastlake' else 3
#     readSignal4(argX='data/fpgaLin/Feb27a_data_40.root;test_')
#     testJ()
#     testK()
#     test_Jan22b()
#     readSignal(inRoot = 'data/fpgaLin/Jan22a_C2_100mV_f500.root', outText='data/fpgaLin/Jan22a_C2_100mV_f500.dat', freq=500)
#     readSignal(inRoot = 'data/fpgaLin/Feb05a_noise_dc_ch19.root', outText='data/fpgaLin/Feb05a_noise_dc_ch19.dat', freq=100)
#     readSignal(inRoot = 'data/fpgaLin/Feb06a_noise_dc_ch19.root', outText='data/fpgaLin/Feb06a_noise_dc_ch19.dat', freq=100)
#     readSignal2(inRoot = 'data/fpgaLin/Feb06c_data_50.root', oTag='t1_')
#     readSignal2(inRoot = 'data/fpgaLin/Feb09a_data_1.root', oTag='sp0_')
#     readSignal(inRoot = 'data/fpgaLin/Feb06b_data_1.root', outText='data/fpgaLin/Feb06b_data_1.dat', freq=100)
#     readSignal3(argX='data/fpgaLin/Feb09b_data_2.root;tp1_')

#     readSignal3(argX='data/fpgaLin/Feb09b_data_1066.root;tp2_')
#     readSignal3(argX='data/fpgaLin/Feb09b_data_1067.root;tp2_')
#     readSignal3(argX='data/fpgaLin/Feb09b_data_1068.root;tp2_')
#     readSignal3(argX='data/fpgaLin/Feb09b_data_1069.root;tp2_')
#     test3(pList=[(0, 'tp09a_')])
#     process_all_match('data/fpgaLin/Feb26b_*mV_f*.root', 'sp02a_', False)
#     process_all_match('data/fpgaLin/Feb27a_data_*.root', 'dp01a_', True)
#     process_all_match4('data/fpgaLin/Feb27a_data_*.root', 'dp02a_', False)
#     process_all_match4('data/fpgaLin/Feb27b_data_*.root', 'dp02a_', False)
#     process_all_match4('data/fpgaLin/Feb28a_data_*.root', 'dp02a_', False)
#     readSignal4a('data/fpgaLin/Mar04C1a_data_0.root;dp02a_')
#     readSignal4c('data/fpgaLin/Mar08D1a_data_80.root;tpx01a_')
#     process_all_matchX(readSignal4c, 'data/fpgaLin/Mar08D1a_data_*.root', 'tpx01a_')
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Mar08D1a/Mar08D1a_data_*.root', 'tpx01a_', False)
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Apr22T1a_data_5*.root', 'tpx01a_', True)
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Apr22T1a_data_???.root', 'tpx02a_', 1False)
#     process_all_matchX(readSignal4d, dataDir+'/Nov13b/Nov13b_HV0p5b_data_*.root*', 'temp1_out/s1a_', True, nThread)
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Apr22T1a_data_1???.root', 'tpx02a_', False)
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Apr22T1a_data_64??.root', 'tpx01b_', True)
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Apr22T1a_data_1???.root', 'tpx01a_', True)
#     process_all_matchX(readSignal4b, 'data/fpgaLin/Apr22T1a_data_609.root', 'atpx01a_', False)
#     process_all_matchX(readSignal5a, '/data/Samples/TMSPlane/CCNU_tests/extended_plane/raw/Jul19C1a/Jul19C1a_*.root', 'aa1_', False)
#     readSignal5a('/data/Samples/TMSPlane/CCNU_tests/extended_plane/raw/Jul19C1a/Jul19C1a_55mV_f50_2.root;aa1_')
#     process_all_matchX(readSignal4c, '/data/Samples/TMSPlane/data/Sep19a/Sep19a_data_0.root', 'atpx01c_', False, 3)
#     process_all_matchX(readSignal4c, '/data/Samples/TMSPlane/data/Sep19b/Sep19b_data_3.root', 'atpx01c_', False, 3)
#     process_all_matchX(readSignal4c, '/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_*.root*', 'atpx01c_', False, 3)
#     process_all_matchX(readSignal2a, '/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_*.root*', 's2a_', False, 3)
#     process_all_matchX(readSignal2a, '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p2_data_0.root*', 's2a_', False, 3)
#     process_all_matchX(readSignal4d, '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5c_*.root', 's1a_', True, 6)
#    dataDir = '/data/Samples/TMSPlane/fpgaLin/raw2/'
    dataDir = '/data/TMS_data/raw/'
#     dataDir = '/run/media/dzhang/Backup\ Plus/TMS_data/'
#     dataDir = '/media/dzhang/dzhang/tms_data/'
#     process_all_matchX(readSignal4d, dataDir+'/Nov13b/Nov13b_HV0p5b_data_*.root*', 'temp1_out/s1a_', True, nThread)
#     print('/data/Samples/TMSPlane/fpgaLin/Dec05b/Dec05b_data_*.root*')
#     process_all_matchX(readSignal5b, dataDir+'Dec05b/Dec05b_data_*.root*', 'temp1_out/s1a_', False, nThread)
#     process_all_matchX(process_data, dataDir+'Dec05b/Dec05b_data_*.root*', 'temp1_out/p1a_', False, nThread)
#     process_all_matchX(process_pulse, dataDir+'Dec05b/Dec05b_data_*.root*', 'temp1_out/p3a_', False, nThread)
#     process_all_matchX(process_event, dataDir+'Dec05b/Dec05b_data_*.root*', 'temp1_out/trigCh4c_', False, nThread)
    process_all_matchX(process_event, dataDir+'Oct19_TMS/*.root', '/data/TMS_data/Processed/Oct19_TMS/trig16thre0d00001_C7_shortA_', False, nThread)
#     process_all_matchY(readSignal4d, '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5c_*.root', 's1a_', True)
#     readSignal2a('/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_100mV_data_2.root;s2a_')
#     readSignal4b('data/fpgaLin/Mar08D1a/Mar08D1a_data_70.root;tpx01a_')

#     test3(pList=[(0, 'tp09a_')], pTag='Feb26a')

#     pList = []
#     pList.append((1489, 'tp3_'))
#     pList.append((1497, 'tp4_'))
#     pList.append((1500, 'tp5_'))
#     pList.append((1511, 'tp6_'))
#     pList.append((1511, 'tp6a_'))
#     pList.append((1511, 'tp6b_'))
#     pList.append((1511, 'tp6b_', 1520)) $ 
#     pList.append((1511, 'tp6c_', 1520)) # [50, 10, 150, 2500]
#     pList.append((1511, 'tp6d_', 1520)) # [50, 500, 600, 2500]
#     pList.append((1511, 'tp6e_', 1520)) # [50, 5, 100, 2500]
#     pList.append((1511, 'tp7a_', 1520))   # [50, 10, 100, 2500] -- test with wiener filter
#     pList.append((1511, 'tp7b_', 1520))   # [30, 250, 350, 2500] -- test with wiener filter with different trapoziodal filter parameters
#     pList.append((1511, 'tp8a_', 1520))   # [30, 10, 100, 2500] -- test with background subtraction with different trapoziodal filter parameters
#     pList.append((0, 'tp09a_'))   # [30, 10, 100, 2500] -- test with background subtraction with different trapoziodal filter parameters

#     for x in [30, 15, 50, 2500]: sp1.fltParam.push_back(x)
#     flt = [50, 10, 100, 2500]
#     flt = [50, 10, 150, 2500]
#     flt = [50, 500, 600, 2500]


#     for p in pList:
#         r = p[0]
#         while True:
# #             fname = 'data/fpgaLin/Feb09b_data_{0:d}.root'.format(r)
#             fname = 'data/fpgaLin/Feb25a_data_{0:d}.root'.format(r)
#             r +=1
# 
#             if os.path.exists(fname.replace('/Feb','/'+p[1]+'Feb')): continue
#             if not os.path.exists(fname) or time.time() - os.path.getmtime(fname) < 10: break
# 
#             readSignal3(argX=fname+';'+p[1])
# 
#             if len(p)>2 and r>p[2]: break

#     check_calib()
#     test_Feb09('sp3_')
#     test_Feb09('sp2_')
#     test_Feb09b('sp3a_')
#     test_Feb09b('sp3b_')
#     test_Feb06c('sp2_')
