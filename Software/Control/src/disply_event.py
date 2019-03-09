#!/usr/bin/env python
import sys
from array import array
from rootUtil import waitRootCmdX
from ROOT import *
gROOT.LoadMacro("sp.C+")
from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent

def display_test(inRoot = 'data/fpgaLin/Feb27a_data_40.root', ievt=0):
    '''To test the event reconstruction'''
    gStyle.SetOptStat(0)
    gROOT.ProcessLine('.L Pal.C')
    gStyle.SetPalette(55)
    gStyle.SetPadRightMargin(0.15)

#     from ROOT import Pal2
#     Pal2()

    data1 = array('f',[0]*(16384*20))
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    ### here comes the constructor
    sp1 = SignalProcessor()
    sp1.nAdcCh=20
    sp1.IO_adcData = data1
    sp1.CF_chan_en.clear()
    for i in range(20): sp1.CF_chan_en.push_back(1)

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
#     for i in range(tree1.GetEntries()):
    while ievt>=0:
        tree1.GetEntry(ievt)
        sp1.reco()

        for e in sp1.IO_evts:
            print e.trigID, len(e.sigs)
            h3.Reset()
            h2.Reset()
            showEvent(e, h3, h2)

            cx.cd(1)
#             h3.Draw('BOX2')
            h3.Draw()
            cx.cd(2)
            t = h2.GetBinContent(h2.GetMaximumBin())*1.06
            h2.GetZaxis().SetRangeUser(-0.05*t,t*0.95)
            h2.Draw('colz')
#             h2.Draw('axis same')

            cx.cd(0)
#             gPad.Update()
#             a = raw_input("x:")
            waitRootCmdX(cx)
        ievt += 1

def main():
    fname = sys.argv[1] if len(sys.argv)>1 else 'data/fpgaLin/Feb27a_data_40.root'
    ievt = int(sys.argv[2]) if len(sys.argv)>2 else 0
    display_test(fname, ievt)

if __name__ == '__main__':
#     display_test()
    main()
