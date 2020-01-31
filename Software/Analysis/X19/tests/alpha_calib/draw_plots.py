#!/usr/bin/env python3
### Draw various plots
from ROOT import TH1F, TChain, gStyle
from rootUtil3 import waitRootCmdX, useNxStyle

def getHist(fname,var,h0,tag,cut='',style=None):
    t1 = TChain("tree")
    t1.Add(fname)

    h1 = h0.Clone(tag)
    print(h1.GetName())
    t1.Draw(var+">>"+h1.GetName(),cut)

    return h1

def compare_dt():
    xEnd = 20000
    h0 = TH1F("h0","dt;dt [#mu s];Entries",100,0,xEnd)

    var = "dt*0.5"
    dir1 = 'Jan19_prom2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air3_66*.root",var,h0,"air3_666")
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air4_35*.root",var,h0,"air4_352")

    xFitStart = 500
    h1.Fit('expo','','', xFitStart,xEnd)
    h2.Fit('expo','','', xFitStart,xEnd)

    h1.Draw('E PLC PMC')
    h2.Draw("E PLC PMC sames")
    waitRootCmdX()

def compare_Proms2():
    N = 100
    h0 = TH1F("h0","Proms;Proms [count];Entries",N,0,N)

    var = "proms2"
    dir1 = 'Jan19_prom2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air3_66*.root",var,h0,"air3_666")
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air4_35*.root",var,h0,"air4_352")

    h2.Draw('PLC PMC')
    h1.Draw("PLC PMC same")

    waitRootCmdX()


def compare_Proms():
    h0 = TH1F("h0","Proms;Proms [count];Entries",70,0,70)

    dir1 = 'p2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air_460.root","proms",h0,"air_460")
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air_594.root","proms",h0,"air_594")
    h3 = getHist(dir1+"TPCHV2kV_PHV0V_air_722.root","proms",h0,"air_722")
    h4 = getHist(dir1+"TPCHV2kV_PHV0V_air3_126.root","proms",h0,"air3_126")
    h5 = getHist(dir1+"TPCHV2kV_PHV0V_air3_2695.root","proms",h0,"air3_2695")

    h1.Draw('PLC PMC')
    h2.Draw("PLC PMC same")
    h3.Draw("same")
    h4.Draw("same")
    h5.Draw("same")

    waitRootCmdX()



if __name__ == '__main__':
    useNxStyle()
    compare_Proms2()
#     compare_dt()
