#!/usr/bin/env python36

from rootUtil3 import waitRootCmdX, useNxStyle

import sys
sys.path.append('/home/dzhang/work/repos/TMSPlane/Software/Control/src')
from rootHelper import getRDF

from ROOT import gROOT, gInterpreter, RDF, gStyle, TLegend, gPad, TCanvas

useNxStyle()
gStyle.SetPalette(55)

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

# excludeCh = [2,8]
# d2.Define('Etot','+'.join(['cQ{0:d}'.format(i) for i in range(nCh) if i not in excludeCh]))
# print('+'.join(['cQ{0:d}'.format(i) for i in range(nCh) if i not in excludeCh]))

d2 = d2.Define('sum2', 'getSum2(cQ0,cQ1)')

d2 = d2.Filter('&&'.join(['cQ{0:d}<10000'.format(i) for i in range(nCh)]))
d2 = d2.Filter('w2[19]<60')

# d2 = d2.Define('sum2', 'getSum2b()')
d2 = d2.Define('E', 'getSum('+','.join(['cQ{0:d}'.format(i) for i in range(nCh)])+')')

h0 = RDF.TH1DModel('h1','h1;E;N',100,-1000,6000)

h1 = d2.Histo1D(h0,'E')
h1.Draw('PLC')

# h1_0 = d2.Histo1D(h0,'cQ0')
# h1_0.Draw('same PLC')
# 
# h1_1 = d2.Histo1D(h0,'cQ1')
# h1_1.Draw('same PLC')

hList = []
# lg = TLegend(0.8,0.6,0.9,0.95)
# lg.SetFillStyle(0)
# for ich in range(nCh):
#     hx = d2.Histo1D(h0,f'cQ{ich}')
#     hx.Draw('PLC same')
#     lg.AddEntry(hx.GetValue(),f'Ch {ich}')
#     hList.append(hx)
#     gPad.Update()
# 
# lg.Draw()

c = TCanvas('c1','c1',1200,800)
c.Divide(5,4)
c.cd(1)
h1.Draw('PLC')

for ich in range(nCh):
    c.cd(2+ich)
    hx = d2.Histo1D(h0,f'cQ{ich}')
    hx.Draw()
    hList.append(hx)
    c.Update()

c.cd(0)
# a = input("A:")
waitRootCmdX()
