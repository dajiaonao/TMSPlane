#!/usr/bin/env python3.6
# %load ./notebook_starter.py
import os
tmsDir = os.getenv('HOME')+'/work/repos/TMSPlane'
import sys
sys.path.append(tmsDir+'/Software/Control/src')
from rootUtil3 import waitRootCmdX, get_default_fig_dir

from notebook_test import test, get_spectrum
from rootHelper import getRDF
# import matplotlib.pyplot as plt
# import numpy as np
from ROOT import gPad, gDirectory, gStyle, TCanvas, TGraph, TLine, gROOT
gStyle.SetPalette(55)

dir1 = tmsDir+'/Software/Control/src/data/fpgaLin/'
dir2 = tmsDir+'2/Software/Analysis/X19/scripts/'

sDir = get_default_fig_dir()
autoSave = False
if gROOT.IsBatch():
    autoSave = True

# plt.rc('figure', figsize=(15, 6))

# from IPython.core.display import display, HTML
# display(HTML("<style>.container { width:100% !important; }</style>"))
# 
# import ROOT
# ROOT.enableJSVis()

c = TCanvas('c1','c1',1000,600)
c.SetRightMargin(0.05)
c.SetLeftMargin(0.1)

nCh = 19
nAdcCh = 20

# d1,ch1 = getRDF(dir1+'Apr22T1a/tpx01a_Apr22T1a_data_*.root', treename='reco')
d1,ch1 = getRDF(dir1+'Apr22T1a/tpx01a_Apr22T1a_data_*.root', treename='reco')
ch1.SetMarkerColor(2)


# ch1.SetMarkerStyle(20)
# ch1.SetMarkerColor(2)
line = TLine()
line.SetLineColor(4)
line.SetLineStyle(2)
line.SetLineWidth(2)

mark_runs = [505, 535, 545, 786, 952, 1213]

for i in range(19):
#     ch1.Draw("Q[{0:d}]:run*1000+evt".format(i),"run>=400&&Q[{0:d}]<0.5&&(w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950)==0".format(i))
#     ch1.Draw("Q[{0:d}]:run*1000+evt".format(i),"run>=500&&Q[{0:d}]<0.5&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950".format(i))
#     ch1.Draw("Q[{0:d}]:run*1000+evt".format(i),"run>=400&&Q[{0:d}]<0.5".format(i))
    ch1.Draw("Q[{0:d}]:run*1000+evt".format(i),"run>=400&&Q[{0:d}]<400".format(i))
#     ch1.Draw("Q[{0:d}]:run*1000+evt".format(i),"run>=500&&run<510&&Q[{0:d}]<0.5".format(i))
    for r in mark_runs: line.DrawLine(r*1000, -1, r*1000, 1)
#     gPad.Draw()
    waitRootCmdX(sDir+'raw_signal_chan{0:d}'.format(i), autoSave)

# gPad.Update()
# a = input("xx")
