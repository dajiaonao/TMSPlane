#!/usr/bin/env python36
import sys
from array import array
from rootUtil3 import waitRootCmdX
from ROOT import gROOT, gStyle, TFile, TChain, Double, TH3F, TH2F, TCanvas, kGray, TH2Poly
gROOT.LoadMacro("sp.C+")
# gROOT.LoadMacro("helix.C+")
gROOT.LoadMacro('HoneycombS.C+')
from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent, hex_l2XY, HoneycombS

def display_test(inRoot = 'data/fpgaLin/Feb27a_data_40.root', ievt=0):
    '''To test the event reconstruction'''
    gStyle.SetOptStat(0)
    gROOT.ProcessLine('.L Pal.C')
    gStyle.SetPalette(55)
    gStyle.SetPadRightMargin(0.15)
    gStyle.SetPadTopMargin(0.02)

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
            print(e.trigID, len(e.sigs))
            h3.Reset()
            h2.Reset()
            showEvent(e, h3, h2)

            cx.cd(1)
#             h3.Draw('BOX2')
#             h3.Draw()
#             h3.SetMarkerStyle(20)
#             h3.SetMarkerSize(1)
            h3.Draw('COLZ')
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


def display_test2():
    '''Read from processed data'''
    gStyle.SetOptStat(0)
    gStyle.SetPadRightMargin(0.15)
    gStyle.SetOptTitle(0)

    run = 83
    evt = 297
    tID = 4
    excludedList = [2,8]
   
    fin1 = TFile('/data/repos/TMSPlane2/Software/Analysis/X19/scripts/calib_out.root','read')
    calib_grs = [fin1.Get('calib_gr_'+str(ix)) for ix in range(19)]

#  run             = 29
#  evt             = 0
#  tID             = 0
#  Q               = 0.0282204, 
#                   0.0200366, -0.000138506, 0.000286522, 0.00122995, 0.000404397, 
#                   0.00961004, 0.000345967, -1.27568e-05, 0.000101391, 0.00217787, 
#                   0.000266498, 0.000962823, -0.000143464, 0.000192873, -0.000813449, 
#                   -0.000736686, 0.000771247, 0.00134848, 0.0470856
#  im              = 210, 
#                   206, 167, 88, 247, 208, 206, 454, 322, 186, 176, 
#                   210, 239, 280, 221, 88, 205, 245, 278, 138
#  w2              = 217, 
#                   217, 0, 21, 89, 242, 223, 78, 0, 26, 85, 
#                   43, 76, 0, 14, 0, 0, 96, 79, 49

    ch = TChain('reco')
    ch.Add('/data/Samples/TMSPlane/fpgaLin/Mar08D1a/tpx01a_Mar08D1a_data_*.root')

    cut = f"run=={run}&&evt=={evt}&&tID=={tID}"
    print(cut)
    n1 = ch.Draw("Q:im-im[19]",cut,"goff")

#     Q = array('f',[0]*19)
#     ch.SetBranchAddress('Q',Q)
#     ch.SetBranchAddress('T',self.dataT)
    Q = ch.GetV1()
    im = ch.GetV2()
#     for i in range(n1):
#         print(i, Q[i],im[i])

    Unit = 0.2
    CF_uSize = -50
    CF_dSize = 200
    h3 = TH3F('h3','h3;x [cm];y [cm];t [ps]',9,-1.8,1.8,9,-1.8,1.8,100,Unit*CF_uSize,Unit*CF_dSize)
    h3b = h3.Clone('h3b') 
    h2 = TH2F('h2','h2;t [ps];Channel;Q',(CF_uSize+CF_dSize),Unit*CF_uSize,Unit*CF_dSize,20,0,20)

    hc = TH2Poly()
    hc.SetTitle('TMS19Plane')
    hc.GetXaxis().SetTitle('x [cm]')
    hc.GetYaxis().SetTitle('y [cm]')
    hc.GetZaxis().SetTitle('N_{e}')
    HoneycombS(hc,0.8,19)
    hc2 = hc.Clone('hc2')

    cx = TCanvas('cx','cx', 1500,700)
    cx.Divide(2,1)

#     dd = array('d', [0,0])
    X,Y = Double(0),Double(0)
    for i in range(19):

#             continue
        hex_l2XY(0.8,i, X,Y)
#         print(i,X,Y)
        Qi = calib_grs[i].Eval(Q[i])
        imi = im[i]*Unit
        if i in excludedList:
            Qi = -999
            imi = 999
        else:
            hc.Fill(X,Y,Qi)

        print(i, Qi, imi)
        h3.Fill(X,Y,imi, Qi)
        h3b.Fill(X,Y,Unit*CF_uSize,Qi)
        h2.Fill(imi,i, Qi)
        hc2.Fill(X,Y,i)

    cx.cd(1)
    h3b.SetFillColor(17);
    h3b.SetLineColor(kGray);
    h3b.Draw('box1')
    h3.Draw('box2 same')
    cx.cd(2)
    h2.Draw('colz')
    cx.cd()

    waitRootCmdX()

    cy = TCanvas()
    cy.SetLeftMargin(0.13)
    cy.cd()
#     hc.GetZaxis().SetRangeUser(-1,1200)
    hc.Draw('colz')
    hc2.Draw('text same')
    waitRootCmdX()

    return

def main():
    fname = sys.argv[1] if len(sys.argv)>1 else 'data/fpgaLin/Feb27a_data_40.root'
    ievt = int(sys.argv[2]) if len(sys.argv)>2 else 0
    display_test(fname, ievt)

if __name__ == '__main__':
#     display_test()
    display_test2()
#     main()
