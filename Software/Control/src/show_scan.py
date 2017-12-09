#!/usr/bin/env python
from ROOT import *
from rootUtil import waitRootCmdX, useAtlasStyle, get_default_fig_dir

sDir = get_default_fig_dir()
sTag = "scan2_"
sDirectly = True

useAtlasStyle()
gStyle.SetPadRightMargin(0.16)
t0 = TTree()
t0.ReadFile('scan_out_v2.ttl')

t0.Show(0)

lt = TLatex()
for i in range(19):
# t0.Draw("mu:VBIASN:VBIASP","Chip==5","colz")
    t0.Draw("VBIASN:VBIASP:mu","Chip=="+str(i),"colz")
    lt.DrawLatexNDC(0.2,0.92,"Chip=="+str(i))
    waitRootCmdX(sDir+sTag+str(i)+"_VBIASN_VBIASP", sDirectly)
    t0.Draw("mu:VBIASN:VBIASP","Chip=="+str(i),"colz")
    lt.DrawLatexNDC(0.2,0.92,"Chip=="+str(i))
    waitRootCmdX(sDir+sTag+str(i)+"_mu_VBIASN", sDirectly)
    t0.Draw("mu:VBIASP:VBIASN","Chip=="+str(i),"colz")
    lt.DrawLatexNDC(0.2,0.92,"Chip=="+str(i))
    waitRootCmdX(sDir+sTag+str(i)+"_mu_VBIASP", sDirectly)
