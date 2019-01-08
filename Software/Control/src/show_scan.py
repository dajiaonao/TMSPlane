#!/usr/bin/env python
from ROOT import *
import sys
from rootUtil import waitRootCmdX, useAtlasStyle, get_default_fig_dir

sDir = get_default_fig_dir()
sTag = "scan2_"
sDirectly = True

useAtlasStyle()
gStyle.SetPadRightMargin(0.16)
t0 = TTree()
dir1 = '/data/cernbox/temp/'
t0.ReadFile(dir1+'scan_out_v2.ttl')

t0.Show(0)

nChan = 19
bestV = [(1,1,None)]*nChan

bestV[6 ]=(1.380, 0.129, 1)
bestV[5 ]=(0.8,   1.057, 1)
bestV[12]=(1.485, 1.546, 1)
bestV[15]=(1.279, 1.246, 1)
bestV[18]=(1.379, 1.546, 1)
bestV[2 ]=(1.059, 0.536, 1)
bestV[0 ]=(1.059, 0.536, 1)

# sys.exit(0)

lt = TLatex()
for i in range(nChan):
# t0.Draw("Vout:VBIASN:VBIASP","Chip==5","colz")
    t0.Draw("VBIASN:VBIASP:Vout","Chip=="+str(i),"colz")

    if bestV[i][2]:
        g1 = TGraph()
        g1.SetMarkerStyle(28)
        g1.SetPoint(0, bestV[i][0], bestV[i][1])
        g1.Draw('Psame')

    lt.DrawLatexNDC(0.2,0.92,"Chip=="+str(i))
    waitRootCmdX(sDir+sTag+str(i)+"_VBIASN_VBIASP", sDirectly)

    ## draw Vout-VBIASN
    t0.Draw("Vout:VBIASN:VBIASP","Chip=="+str(i),"colz")
    if bestV[i][2]:
        g2 = TGraph()
        g2.SetPoint(0, bestV[i][0], 0)
        g2.SetPoint(1, bestV[i][0], 10)
        g2.Draw("Lsame")

    lt.DrawLatexNDC(0.2,0.92,"Chip=="+str(i))
    waitRootCmdX(sDir+sTag+str(i)+"_Vout_VBIASN", sDirectly)

    ## draw Vout-VBIASN
    t0.Draw("Vout:VBIASP:VBIASN","Chip=="+str(i),"colz")
    if bestV[i][2]:
        g3 = TGraph()
        g3.SetPoint(0, bestV[i][1], 0)
        g3.SetPoint(1, bestV[i][1], 10)
        g3.Draw("Lsame")

    lt.DrawLatexNDC(0.2,0.92,"Chip=="+str(i))
    waitRootCmdX(sDir+sTag+str(i)+"_Vout_VBIASP", sDirectly)
