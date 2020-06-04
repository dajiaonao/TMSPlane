#!/usr/bin/env python3
### Draw various plots
from ROOT import TH1F, TChain, gStyle, gPad, TLegend, TRatioPlot
from rootUtil3 import waitRootCmdX, useNxStyle

def getHist(fname,var,h0,tag,cut='',style=None,opt=''):
    t1 = TChain("tree")
    if isinstance(fname, list):
        for fn in fname: t1.Add(fn)
    else: t1.Add(fname)

    h1 = h0.Clone(tag)
    h1.SetTitle(tag)
    print(h1.GetName())
    t1.Draw(var+">>"+h1.GetName(),cut,opt)

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


class Check_May28:
    def __init__(self):
        self.dir1 = '/data/TMS_data/Processed/May27a/'

    def compare_proms2(self):
        N = 256
        h0 = TH1F("h0","Proms;Proms [count];Entries",N,0,N)

        var = "proms2"
        cut = 'proms2>10&&proms2<250'
        h1 = getHist(self.dir1+"HVscan_scan_500V_*.root",var,h0,"HV 500 V",cut=cut)
        h2 = getHist(self.dir1+"HVscan_scan_2000V_*.root",var,h0,"HV 2000 V",cut=cut)
        h3 = getHist(self.dir1+"HVscan_scan_1500V_*.root",var,h0,"HV 1500 V",cut=cut)
        h4 = getHist(self.dir1+"HVscan_scan_100V_*.root",var,h0,"HV 100 V",cut=cut)
        h5 = getHist(self.dir1+"HVscan_scan_300V_*.root",var,h0,"HV 300 V",cut=cut)
        h6 = getHist(self.dir1+"HVscan_scan_800V_*.root",var,h0,"HV 800 V",cut=cut)

        h1.Draw('PLC PMC')
        h2.Draw("PLC PMC same")
        h3.Draw("PLC PMC same")
        h4.Draw("PLC PMC same")
        h5.Draw("PLC PMC same")
        h6.Draw("PLC PMC same")

        gPad.BuildLegend()
        print("h1:{0:.1f}, h2:{1:.1f}".format(h1.Integral(2,100), h2.Integral(2,100)))
        print("h1:{0:.1f}, h2:{1:.1f}".format(h1.GetMean(), h2.GetMean()))

        waitRootCmdX()

class Check_May31:
    def __init__(self):
        self.dir1 = '/data/TMS_data/Processed/May31a_cut20/'

    def compare_proms2(self):
        N = 256
        h0 = TH1F("h0","Proms;Proms [count];Entries",N,0,N)

        var = "proms2"
        cut = 'proms2>0&&proms2<250'
        h1 = getHist(self.dir1+"HV_alphaOn_rampAr_1000V_5[0-9].root",var,h0,"HV 1000 V, 5x",cut=cut)
        h2 = getHist(self.dir1+"HV_alphaOn_rampAr_1000V_17[0-9].root",var,h0,"HV 1000 V, 17x",cut=cut)
        h3 = getHist(self.dir1+"HV_alphaOn_recheckAr_1000V_19[0-9].root",var,h0,"HV 1000 V, recheck",cut=cut)
#         h4 = getHist(self.dir1+"HVscan_scan_100V_*.root",var,h0,"HV 100 V",cut=cut)
#         h5 = getHist(self.dir1+"HVscan_scan_300V_*.root",var,h0,"HV 300 V",cut=cut)
#         h6 = getHist(self.dir1+"HVscan_scan_800V_*.root",var,h0,"HV 800 V",cut=cut)

        h1.Draw('PLC PMC')
        h2.Draw("PLC PMC same")
        h3.Draw("PLC PMC same")
#         h4.Draw("PLC PMC same")
#         h5.Draw("PLC PMC same")
#         h6.Draw("PLC PMC same")

        gPad.BuildLegend()
        print("h1:{0:.1f}, h2:{1:.1f}".format(h1.Integral(2,100), h2.Integral(2,100)))
        print("h1:{0:.1f}, h2:{1:.1f}".format(h1.GetMean(), h2.GetMean()))

        waitRootCmdX()

    def compare_proms(self, var="proms2", cut='proms2>0&&proms2<250', xtitle='Proms'):
        N = 256
        h0 = TH1F("h0",f"Proms;{xtitle} [count];Entries",N,0,N)

        h1 = getHist(self.dir1+"HV_alphaOn_rampAr_1000V_5[0-9].root",var,h0,"HV 1000 V, 5x",cut=cut)
        h2 = getHist(self.dir1+"HV_alphaOn_rampAr_1000V_17[0-9].root",var,h0,"HV 1000 V, 17x",cut=cut)
        h3 = getHist(self.dir1+"HV_alphaOn_recheckAr_1000V_19[0-9].root",var,h0,"HV 1000 V, recheck",cut=cut)
#         h4 = getHist(self.dir1+"HVscan_scan_100V_*.root",var,h0,"HV 100 V",cut=cut)
#         h5 = getHist(self.dir1+"HVscan_scan_300V_*.root",var,h0,"HV 300 V",cut=cut)
#         h6 = getHist(self.dir1+"HVscan_scan_800V_*.root",var,h0,"HV 800 V",cut=cut)

        h1.Draw('PLC PMC')
        h2.Draw("PLC PMC same")
        h3.Draw("PLC PMC same")
#         h4.Draw("PLC PMC same")
#         h5.Draw("PLC PMC same")
#         h6.Draw("PLC PMC same")

        gPad.BuildLegend()
        print("h1:{0:.1f}, h2:{1:.1f}".format(h1.Integral(2,100), h2.Integral(2,100)))
        print("h1:{0:.1f}, h2:{1:.1f}".format(h1.GetMean(), h2.GetMean()))

        waitRootCmdX()


    def compare_dt2(self, nEnd=20000, nFitStart=400):
        xEnd = 20000*0.000001
        h0 = TH1F("h0","dt;dt [s];Entries",100,0,xEnd)

        var = "dt*0.0000005"
        h1 = getHist(self.dir1+"HV_alphaOn_rampAr_1000V_17[0-9].root",var,h0,"HV 1000 V, 17x")
        h2 = getHist(self.dir1+"HV_alphaOn_recheckAr_1000V_19[0-9].root",var,h0,"HV 1000 V, recheck")

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

    def dt_fit(self, nEnd=20000, nFitStart=500):
        xEnd = nEnd*0.000001
        h0 = TH1F("h0","dt;dt [s];Entries",100,0,xEnd)

        var = "dt*0.0000005"
#         h1 = getHist(self.dir1+"HV_alphaOn_rampAr_1000V_*.root",var,h0,"HV 1000 V, rampAr")
        h1 = getHist(self.dir1+"HV_alphaOn_recheckAr_1000V_*.root",var,h0,"HV 1000 V, recheck")

        xFitStart = nFitStart*0.000001
        h1.Fit('expo','','', xFitStart,xEnd)

#         gStyle.SetFunLineColor(2)
#         h1.SetLineColor(2)
#         h1.SetMarkerColor(2)
#         h1.SetMarkerStyle(20)

        rp1 = TRatioPlot(h1);
        rp1.Draw();
        rp1.GetLowerRefYaxis().SetTitle("Ratio");

        fun1 = h1.GetFunction('expo')
        fun1.SetLineColor(6)
# 
#         h1.Draw('E PLC PMC')
        waitRootCmdX()

def test():
#     a = Check_May28()
    a = Check_May31()
#     a.compare_proms2()
    a.compare_proms(var="proms3", cut='', xtitle='Proms3')
#     a.dir1 = '/data/TMS_data/Processed/May31a_pCut3_45/'
#     a.compare_dt2()
#     a.compare_proms2()
#     a.compare_proms(var="proms3", cut='', xtitle='Proms3')
#     a.dir1 = '/data/TMS_data/Processed/May31a_pCut3_20/'
#     a.dt_fit(nEnd=30000)

if __name__ == '__main__':
    useNxStyle()
    test()
#     compare_Proms()
#     compare_Proms2()
#     compare_Proms2b()
#     compare_dt2()
#     compare_HV()
#     compare_Proms2()
#     compare_dt()
