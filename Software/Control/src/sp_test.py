#!/usr/bin/env python

from ctypes import *
from sigproc import SigProc 
from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor
from array import array

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
inRoot = 'data/fpgaLin/Jan21b_C2_100mV_f1000.root'
fout1 = TFile(inRoot,'read')
tree1 = fout1.Get('tree1')
tree1.SetBranchAddress('adc',data1)

i = 2
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
