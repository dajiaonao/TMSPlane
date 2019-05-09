#!/usr/bin/env python36

from rootUtil3 import waitRootCmdX, useNxStyle

import sys
sys.path.append('/home/dzhang/work/repos/TMSPlane/Software/Control/src')
from rootHelper import getRDF

from ROOT import gROOT, gInterpreter, RDF, gStyle, TLegend, gPad, TCanvas, kGray
from ROOT import gROOT, gStyle, TFile, TChain, Double, TH3F, TH2F, TCanvas, kGray, TH2Poly
gROOT.LoadMacro('HoneycombS.C+')
from ROOT import hex_l2XY, HoneycombS

useNxStyle()
gStyle.SetPalette(70)
gStyle.SetPaintTextFormat('.0f')
gStyle.SetPadRightMargin(0.15)
gStyle.SetPadTickX()
gStyle.SetPadTickY()

dir1 = '/home/dzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/'

d1,ch1 = getRDF(dir1+'Mar08D1a/tpx01a_Mar08D1a_data_*.root', treename='reco')

xcode = '''
TFile* fin1 = new TFile("/data/repos/TMSPlane2/Software/Analysis/X19/scripts/calib_out.root","read");
auto* calib_gr_0 = (TGraphErrors*)fin1->Get("calib_gr_0");
auto* calib_gr_1 = (TGraphErrors*)fin1->Get("calib_gr_1");
auto* calib_gr_2 = (TGraphErrors*)fin1->Get("calib_gr_2");
auto* calib_gr_3 = (TGraphErrors*)fin1->Get("calib_gr_3");
auto* calib_gr_4 = (TGraphErrors*)fin1->Get("calib_gr_4");
auto* calib_gr_5 = (TGraphErrors*)fin1->Get("calib_gr_5");
auto* calib_gr_6 = (TGraphErrors*)fin1->Get("calib_gr_6");
auto* calib_gr_7 = (TGraphErrors*)fin1->Get("calib_gr_7");
auto* calib_gr_8 = (TGraphErrors*)fin1->Get("calib_gr_8");
auto* calib_gr_9 = (TGraphErrors*)fin1->Get("calib_gr_9");
auto* calib_gr_10 = (TGraphErrors*)fin1->Get("calib_gr_10");
auto* calib_gr_11 = (TGraphErrors*)fin1->Get("calib_gr_11");
auto* calib_gr_12 = (TGraphErrors*)fin1->Get("calib_gr_12");
auto* calib_gr_13 = (TGraphErrors*)fin1->Get("calib_gr_13");
auto* calib_gr_14 = (TGraphErrors*)fin1->Get("calib_gr_14");
auto* calib_gr_15 = (TGraphErrors*)fin1->Get("calib_gr_15");
auto* calib_gr_16 = (TGraphErrors*)fin1->Get("calib_gr_16");
auto* calib_gr_17 = (TGraphErrors*)fin1->Get("calib_gr_17");
auto* calib_gr_18 = (TGraphErrors*)fin1->Get("calib_gr_18");

const size_t nCh = 19;
std::vector< TGraphErrors* > calib_grs{calib_gr_0,calib_gr_1,calib_gr_2,calib_gr_3,calib_gr_4,calib_gr_5,calib_gr_6,calib_gr_7,calib_gr_8,calib_gr_9,calib_gr_10,calib_gr_11,calib_gr_12,calib_gr_13,calib_gr_14,calib_gr_15,calib_gr_16,calib_gr_17,calib_gr_18};

double getCorrVal(float a, int ich){return calib_grs[ich]->Eval(a);}
double getSum(double a0, double a1, double a2, double a3, double a4, double a5, double a6, double a7, double a8, double a9, double a10, double a11, double a12, double a13, double a14, double a15, double a16, double a17, double a18){return a0+a1+a3+a4+a5+a6+a7+a9+a10+a11+a12+a13+a14+a15+a16+a17+a18;}

double getSum2(double a0, double a1){return a0+a1;}
//double getSum2b(){return cQ0+cQ1;}
'''
gInterpreter.Declare(xcode)


d2 = d1
nCh = 19
for i in range(nCh):
    d2 = d2.Define('cQ{0}'.format(i),'getCorrVal(Q[{0:d}],{0:d})'.format(i))

excludeCh = [2,8]
# d2.Define('Etot','+'.join(['cQ{0:d}'.format(i) for i in range(nCh) if i not in excludeCh]))
# print('+'.join(['cQ{0:d}'.format(i) for i in range(nCh) if i not in excludeCh]))

d2 = d2.Define('sum2', 'getSum2(cQ0,cQ1)')

d2 = d2.Filter('&&'.join(['cQ{0:d}<10000'.format(i) for i in range(nCh)]))
d2 = d2.Filter('w2[19]<60&&run>40')

# d2 = d2.Define('sum2', 'getSum2b()')
d2 = d2.Define('E', 'getSum('+','.join(['cQ{0:d}'.format(i) for i in range(nCh)])+')')

h0 = RDF.TH1DModel('h1','h1;E;N',100,-1000,6000)

gStyle.SetFuncColor(2)

nCh = 19
ch_excluded = [2,8]

tQ = [None]*nCh
for i in range(19):
    tQ[i] = None if i in ch_excluded else d2.Sum('cQ'+str(i))

hc = TH2Poly()
hc.SetTitle('TMS19Plane')
hc.GetXaxis().SetTitle('x [cm]')
hc.GetYaxis().SetTitle('y [cm]')
hc.GetZaxis().SetTitle('N_{e}')
HoneycombS(hc,0.8,19)
hc2 = hc.Clone('hc2')

gROOT.ProcessLine('.x Pal3.C')

vQ = [-1]*nCh
X,Y = Double(0),Double(0)
for i in range(19):
    if tQ[i]: vQ[i] = tQ[i].GetValue()

    hex_l2XY(0.8,i, X,Y)
    hc.Fill(X,Y,vQ[i])
    hc2.Fill(X,Y,i+0.01)

print(vQ)

# c = TCanvas('c','c',700,600)
c = TCanvas('c','c',2122,183,723,663)
hc.Draw('colz')
hc2.Draw('text same')

waitRootCmdX()
