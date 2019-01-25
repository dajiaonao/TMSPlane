#!/usr/bin/env python
# from ROOT import TGraphErrors, TFile, TTree, gDirectory, TGraph2D, TIter
from ROOT import * 
from glob import glob
import os, re
from rootUtil import waitRootCmdX, useNxStyle, get_default_fig_dir

sDir = get_default_fig_dir()
sTag = 'test1_'

def create_calibration_file():
    '''Create a root file that contains a TF1 and a TGraph to map the measured voltage to the number of electron'''
    nCh = 19
    gr0 = [TGraphErrors() for j in range(nCh)]
    grs = [TGraphErrors() for j in range(nCh)]
    gEs = [TGraphErrors() for j in range(nCh)]
    vx = [int(os.path.basename(fname).split('_')[2][:-2]) for fname in glob('data/fpgaLin/Jan22b_C2_*mV_f1000.dat')]

    h_quality = TGraph2D()

    fout = TFile('fout_calib.root','recreate')

    for v in sorted(vx):
        fname = 'data/fpgaLin/Jan22b_C2_{0:d}mV_f1000.dat'.format(v)
        t1 = TTree()
        t1.ReadFile(fname)

        for ch in range(nCh):
            t1.Draw('A>>h1',"ch=={0:d}".format(ch),"goff")
            h1 = gDirectory.Get('h1')
            h1.SetName('h'+str(v)+'_ch'+str(ch))
            r = h1.Fit('gaus','S')
            fun1 = h1.GetFunction('gaus')
            h1.Write()


            g1 = grs[ch]
            n = g1.GetN()
            g1.SetPoint(n,v,fun1.GetParameter(1))
            g1.SetPointError(n,0,fun1.GetParError(1))

            g2 = gEs[ch]
            g2.SetPoint(n,v,fun1.GetParameter(2))
            g2.SetPointError(n,0,fun1.GetParError(2))

            h_quality.SetPoint(nCh*n+ch, v, ch, r.Chi2())

            g0 = gr0[ch]
            g0.SetPoint(n,fun1.GetParameter(1),v)
            g0.SetPointError(n,fun1.GetParError(1),0)


    for i in range(nCh):
        grs[i].Write('gr_mean_ch'+str(i))
        gEs[i].Write('gr_sigma_ch'+str(i))

        r = gr0[i].Fit('pol1','S')
        h_quality.SetPoint(nCh*len(vx)+i, -1, ch, r.Chi2())

        gr0[i].Write('gr_calib_ch'+str(i))

    h_quality.Write('fitQ')
    fout.Close()


def check_calibration():
    fout = TFile('fout_calib.root','read')

    nCh = 19
    nxt = TIter(fout.GetListOfKeys())
   
    hxs = [[] for i in range(nCh)]
    while True:
        k = nxt()
        if not k: break

#         print k.GetName()
        m = re.match('h(\d+)_ch(\d+)', k.GetName())
        if m:
#             print m.group(1),m.group(2)
            hxs[int(m.group(2))].append((int(m.group(1)), k.ReadObj()))

    lt = TLatex()
    h2 = TH1F("h2","h2;Raw measurement [V];Entries",100,0,0.2)
    for ch in range(nCh):
        h2.Draw()
        max_x = -1
        max_y = -1
        for x in sorted(hxs[ch], key=lambda x: x[0]):
            x[1].SetFillStyle(0)
            x[1].SetLineWidth(2)
            x[1].Draw('hist PLC same')
            max_y = max(max_y, x[1].GetBinContent(x[1].GetMaximumBin()))
            max_x = max(max_x, x[1].GetXaxis().GetXmax())

        h2.GetXaxis().SetRangeUser(0,max_x)
        h2.GetYaxis().SetRangeUser(0,max_y*1.1)

        lt.DrawLatexNDC(0.2,0.88,"Channel {0:d}".format(ch))

        tag1 = 'Jan22a_'
        waitRootCmdX(sDir+tag1+'check_ch{0:d}'.format(ch))

def test1():
    print "testing"
    create_calibration_file()

if __name__ == "__main__":
#     test1()
    useNxStyle()
    gStyle.SetPalette(55)
    check_calibration()
