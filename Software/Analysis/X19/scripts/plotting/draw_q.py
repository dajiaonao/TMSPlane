#!/usr/bin/env python36
import sys
sys.path.append('/home/dzhang/work/repos/TMSPlane/Software/Control/src')
from rootHelper import getRDF
from rootUtil3 import waitRootCmdX, useNxStyle

from ROOT import gPad, gDirectory, gStyle, TCanvas, TGraph, RDF
useNxStyle()
gStyle.SetPalette(55)

dir1 = '/home/dzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/'

d1,ch1 = getRDF(dir1+'Mar08D1a/tpx01a_Mar08D1a_data_*.root', treename='reco')

h0 = RDF.TH2DModel('h1','h1;Run;U_{0} [V]',140,0,140,200,-0.01,0.1)


d1 = d1.Define('Q0','Q[0]')
d2 = d1.Filter('w2[19]>200&&(im[0]-im[19])>900&&(im[0]-im[19])<950')
h1 = d1.Histo2D(h0, 'run','Q0')

h1.SetMarkerStyle(1)
h1.Draw()
waitRootCmdX()
