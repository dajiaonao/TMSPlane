#!/usr/bin/env python3
### Draw various plots
from ROOT import TH1F, TChain, gStyle, gPad
from rootUtil3 import waitRootCmdX, useNxStyle

def getHist(fname,var,h0,tag,cut='',style=None):
    t1 = TChain("tree")
    t1.Add(fname)

    h1 = h0.Clone(tag)
    h1.SetTitle(tag)
    print(h1.GetName())
    t1.Draw(var+">>"+h1.GetName(),cut)

    return h1

def compare_dt2():
    xEnd = 20000*0.000001
    h0 = TH1F("h0","dt;dt [s];Entries",100,0,xEnd)

    var = "dt*0.0000005"
    dir1 = 'Jan19_prom2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air3_66[0-9].root",var,h0,"air3_666")
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air4_35[0-9].root",var,h0,"air4_352")

    xFitStart = 500*0.000001
    h1.Fit('expo','','', xFitStart,xEnd)
    h2.Fit('expo','','', xFitStart,xEnd)

    h1.SetLineColor(2)
    h1.SetMarkerColor(2)
    h1.SetMarkerStyle(20)
    h2.SetLineColor(4)
    h2.SetMarkerColor(4)
    h2.SetMarkerStyle(25)

    fun1 = h1.GetFunction('expo')
    fun1.SetLineColor(6)
    fun2 = h2.GetFunction('expo')
    fun2.SetLineColor(3)

    h1.Draw('E PLC PMC')
    h2.Draw("E PLC PMC sames")
    waitRootCmdX()


def compare_dt():
    xEnd = 20000
    h0 = TH1F("h0","dt;dt [#mu s];Entries",100,0,xEnd)

    var = "dt*0.5"
    dir1 = 'Jan19_prom2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air3_66[0-9].root",var,h0,"air3_666")
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air4_35[0-9].root",var,h0,"air4_352")

    xFitStart = 500
    h1.Fit('expo','','', xFitStart,xEnd)
    h2.Fit('expo','','', xFitStart,xEnd)

    h1.Draw('E PLC PMC')
    h2.Draw("E PLC PMC sames")
    waitRootCmdX()


def compare_Proms2b():
    N = 40
    h0 = TH1F("h0","Proms;Proms [count];Entries",N,0,N)

    var = "proms2"
    cut = 'proms2>0&&proms2<40'
    dir1 = 'Jan19_prom2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air3_66[0-9].root",var,h0,"air3_666",cut=cut)
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air4_35[0-9].root",var,h0,"air4_352",cut=cut)

    h2.Draw('PLC PMC')
    h1.Draw("PLC PMC same")

    gPad.BuildLegend()
    print("h1:{0:.1f}, h2:{1:.1f}".format(h1.Integral(2,100), h2.Integral(2,100)))
    print("h1:{0:.1f}, h2:{1:.1f}".format(h1.GetMean(), h2.GetMean()))

    waitRootCmdX()


def compare_Proms2():
    N = 100
    h0 = TH1F("h0","Proms;Proms [count];Entries",N,0,N)

    var = "proms2"
    cut = 'proms2>0&&proms2<40'
    dir1 = 'Jan19_prom2/'
    h1 = getHist(dir1+"TPCHV2kV_PHV0V_air3_66[0-9].root",var,h0,"air3_666",cut=cut)
    h2 = getHist(dir1+"TPCHV2kV_PHV0V_air4_35[0-9].root",var,h0,"air4_352",cut=cut)

    h2.Draw('PLC PMC')
    h1.Draw("PLC PMC same")

    gPad.BuildLegend()
    print("h1:{0:.1f}, h2:{1:.1f}".format(h1.Integral(2,100), h2.Integral(2,100)))
    print("h1:{0:.1f}, h2:{1:.1f}".format(h1.GetMean(), h2.GetMean()))

    waitRootCmdX()


def compare_Proms():
    h0 = TH1F("h0","Proms;Proms [count];Entries",70,0,70)

#     dir1 = 'p2/'
    dir1 = 'Jan19_prom2/'
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
#     compare_Proms()
#     compare_Proms2()
    compare_Proms2b()
#     compare_dt2()
