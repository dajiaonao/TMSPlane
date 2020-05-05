#!/usr/bin/env python3
### Draw various plots
from ROOT import TH1F, TChain, gStyle, TLegend
from rootUtil3 import waitRootCmdX, useNxStyle

def getHist(fname,var,h0,tag,cut='',style=None,opt=''):
    t1 = TChain("tree")
    if isinstance(fname, list):
        for fn in fname: t1.Add(fn)
    else: t1.Add(fname)

    h1 = h0.Clone(tag)
    print(h1.GetName())
    t1.Draw(var+">>"+h1.GetName(),cut,opt)

    return h1

def compare_HV():
    dir1 = 'Jan19_prom2/'
    N = 150
    h0 = TH1F("h0","Proms;Proms [count];Entries",N,0,N)
    var = "proms2"

    ds_list = {}
    patt=dir1+'TPCHV2kV_PHV0V_air3_{0:d}.root'
    ds_list[1000] = [patt.format(idx) for idx in range(130,136)]
    ds_list[1001] = [patt.format(idx) for idx in range(194,209)]
    ds_list[800] = [patt.format(idx) for idx in range(138,146)]
    ds_list[600] = [patt.format(idx) for idx in range(148,156)]
    ds_list[400] = [patt.format(idx) for idx in range(158,169)]
    ds_list[200] = [patt.format(idx) for idx in range(171,181)]
    ds_list[100] = [patt.format(idx) for idx in range(183,192)]
    ds_list[500] = [patt.format(idx) for idx in range(211,220)]
    ds_list[300] = [patt.format(idx) for idx in range(222,229)]
    print(ds_list[1000])

    hlist = []
    lg = TLegend(0.2,0.5,0.4,0.88)
    for v in sorted(ds_list,reverse=True):
        hx = getHist(ds_list[v],var,h0,f'HV{v}V',opt='norm')
        hlist.append(hx)
        lg.AddEntry(hx,hx.GetName(),'l')
    
    hlist[0].Draw('PLC hist')
    for h in hlist[1:]: h.Draw('PLC hist same')
    lg.Draw()

    waitRootCmdX()

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
    compare_HV()
#     compare_Proms2()
#     compare_dt()
