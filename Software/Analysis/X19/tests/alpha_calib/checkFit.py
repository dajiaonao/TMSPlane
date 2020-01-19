#!/usr/bin/env python3
from ROOT import TChain, TGraphErrors, TF1

fun1 = TF1("fun1","[4]+[0]*(exp(-(x-[3])/[1]) - exp(-(x-[3])/[2]))", 0, 1000)
fun1.SetParameter(0,30)
fun1.SetParameter(1,300)
fun1.SetParameter(2,200)
fun1.SetParameter(3,0)

# gr1.Fit(fun1)
# fun1.Draw()


ch1 = TChain("tr1")
ch1.Add('/data/Samples/TMSPlane/data/merged/Jan15a/TPCHV2kV_PHV0V_air3_t0.root')

ch1.SetEstimate(20000000)
ch1.Draw("data:Iteration$","Entry$==126","goff")
v1 = ch1.GetV1()

gr1 = TGraphErrors()
N = 910
for i in range(1000):
    gr1.SetPoint(i, i, v1[N+i])
    gr1.SetPointError(i, 0, 0.5)

gr1.SetMarkerColor(4)
gr1.Draw("AP")

fun1.SetParameter(4,v1[N])
gr1.Fit(fun1)

a = input()
