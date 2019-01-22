#!/usr/bin/env python

# from SignalChecker import SignalChecker
from ROOT import *
from rootUtil import waitRootCmdX
from array import array
from sigproc import SigProc 

def getChain(fname, treename='tree1'):
    ch1 = TChain(treename) 
    ch1.Add(fname)
    ch1.SetMarkerStyle(7)
    return ch1

def test1():
    ch1 = getChain('/data/Samples/TMSPlane/root_files/Jan08a_100mV_r30p0us.root')
    ch2 = getChain('/data/Samples/TMSPlane/root_files/Jan08a_100mV_r50p0us.root')
    ch2.SetLineColor(2)
    ch2.SetMarkerColor(2)

    var = lambda x: '(adc[12]+{1:.4f}):(Iteration$-{0:d})*0.2'.format(x[0],x[2])
#     var = lambda x: 'adc[12]:(Iteration$-{0:d})'.format(x[0],x[2])
    cut = lambda x: '&&Iteration$>{0:d}&&Iteration$<{1:d}'.format(x[0],x[1])

    reg1 = (3025,6525,0)
    reg2 = (4000,7500,0.004)
    ch1.Draw(var(reg1),'Entry$==199'+cut(reg1))
    ch2.Draw(var(reg2),'Entry$==199'+cut(reg2),'same')

    waitRootCmdX()

def get_tgraph(ch,entry,inRoot):
    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = s1.generate_adcDataBuf()
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.GetEntry(entry)

    data3 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nSamples)()
    s1.filters_trapezoidal(data1[ch], data3, [100,100,200,10])

    x1 = array('f',range(s1.nSamples))
    g1 = TGraph(s1.nSamples, x1, data3)

    return g1


def test2():
    ch = 12
    entry = 199
    inRoot = '/data/Samples/TMSPlane/root_files/Jan08a_100mV_r30p0us.root'

#     s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
#     data1 = s1.generate_adcDataBuf()
#     fout1 = TFile(inRoot,'read')
#     tree1 = fout1.Get('tree1')
#     tree1.SetBranchAddress('adc',data1)
#     tree1.GetEntry(199)
# 
#     data3 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nSamples)()
#     s1.filters_trapezoidal(data1[ch], data3, [100,100,200,-1])
# 
#     x1 = array('f',range(s1.nSamples))
#     g1 = TGraph(s1.nSamples, x1, data3)
    g1 = get_tgraph(ch,entry,inRoot)
    g1.Draw('AP')

    g2 = get_tgraph(ch,entry,'/data/Samples/TMSPlane/root_files/Jan08a_100mV_r50p0us.root')
    g2.SetMarkerColor(2)
    g2.Draw('Psame')

    waitRootCmdX()


if __name__ == '__main__':
    test1()
#     test2()
