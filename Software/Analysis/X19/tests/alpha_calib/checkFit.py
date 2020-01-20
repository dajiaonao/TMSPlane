#!/usr/bin/env python3
from ROOT import TChain, TGraphErrors, TF1, gPad, gStyle
from rootUtil3 import waitRootCmdX,useNxStyle
gStyle.SetOptFit(1111)
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetPadRightMargin(0.02)
gStyle.SetPadTopMargin(0.06)
# useNxStyle()
# gStyle.SetMarkerSize(0)

fun_def_code='''
double sShape(double *x, double *par){
   return x>par[3]?par[4]+par[0]*par[1]/(par[1]-par[2])*(exp(-(x-par[3])/par[1]) - exp(-(x-par[3])/par[2])):par[4];
}
'''

# fun1 = TF1("fun1","[4]+[0]*(exp(-(x-[3])/[1]) - exp(-(x-[3])/[2]))", 0, 1000)
fun1 = TF1("fun1","[4]+(x>[3]?[0]*[1]/([1]-[2])*(exp(-(x-[3])/[1]) - exp(-(x-[3])/[2])):0.)", 0, 1000)
fun1.SetParameter(0,30)
fun1.SetParameter(1,300)
fun1.SetParameter(2,200)
fun1.SetParameter(3,0)

fun1.SetParName(0,"A")
fun1.SetParName(1,"#tau_{d}")
fun1.SetParName(2,"#tau_{i}")
fun1.SetParName(3,"t_{0}")
fun1.SetParName(4,"b")

# gr1.Fit(fun1)
# fun1.Draw()


ch1 = TChain("tr1")
ch1.Add('/data/Samples/TMSPlane/data/merged/Jan15a/TPCHV2kV_PHV0V_air3_t0.root')

ch1.SetEstimate(20000000)
ch1.Draw("data:Iteration$","Entry$==126","goff")
v1 = ch1.GetV1()

gr1 = TGraphErrors()
# N = 910
# N = 500
# N = 134400
N = 1151200
L = 1800
xUnit = 0.5
yUnit = 0.4
for i in range(L):
    gr1.SetPoint(i, i*xUnit, v1[N+i]*yUnit)
    gr1.SetPointError(i, 0*xUnit, 0.5*yUnit)

gr1.SetMarkerColor(4)
gr1.SetLineColor(4)
gr1.Draw("AP")

fun1.SetParameter(4,v1[N]*yUnit)
gr1.Fit(fun1,'','',0,L*xUnit)

gr1.GetXaxis().SetTitle("t [#mus]")
gr1.GetYaxis().SetTitle("U_{Out} [mV]")

gPad.Update()

waitRootCmdX()
# a = input()
