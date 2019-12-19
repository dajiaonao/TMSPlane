#!/usr/bin/env python3
from rootUtil3 import waitRootCmdX, useNxStyle
from ROOT import gROOT, gStyle, TFile, TChain, Double, TH3F, TH2F, TCanvas, kGray, TH2Poly
gROOT.LoadMacro('HoneycombS.C+')
from ROOT import hex_l2XY, HoneycombS

def draw_normal():
    useNxStyle()
    gStyle.SetPaintTextFormat('.0f')
    gStyle.SetPadRightMargin(0.15)

    hc = TH2Poly()
    hc.SetTitle('TMS19Plane')
    hc.GetXaxis().SetTitle('x [cm]')
    hc.GetYaxis().SetTitle('y [cm]')
    hc.GetZaxis().SetTitle('Id')
    HoneycombS(hc,0.8,19)

    gROOT.ProcessLine('.x Pal3.C')

    X,Y = Double(0),Double(0)
    for i in range(19):
        hex_l2XY(0.8,i, X,Y)
        hc.Fill(X,Y,i+0.01)

    c = TCanvas('c','c',2122,183,723,663)
    hc.Draw('colz')
    hc.Draw('text same')

    waitRootCmdX()

def draw_status(sT=None):
    useNxStyle()
    gStyle.SetPaintTextFormat('.0f')
    gStyle.SetPadRightMargin(0.15)
    nCh = 19

    hc = TH2Poly()
    hc.SetTitle('TMS19Plane')
    hc.GetXaxis().SetTitle('x [cm]')
    hc.GetYaxis().SetTitle('y [cm]')
    hc.GetZaxis().SetTitle('Id')
    HoneycombS(hc,0.8,19)

    hc_c = hc.Clone('hc_c')

    gROOT.ProcessLine('.x Pal3.C')
    
    value = sT if sT is not None else [i for i in range(nCh)]

    X,Y = Double(0),Double(0)
    for i in range(nCh):
        hex_l2XY(0.8,i, X,Y)
        hc.Fill(X,Y,value[i])
        hc_c.Fill(X,Y,i+0.01)

    c = TCanvas('c','c',2122,183,723,663)
    hc.Draw('colz')
    hc_c.Draw('text same')

    waitRootCmdX()



if __name__ == '__main__':
    draw_normal()
#     draw_status([10,10,2,8,1,9,
#         1,0,2,9,0,
#         10,10,0,6,8,
#         0,3,2])
