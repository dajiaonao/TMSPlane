#!/usr/bin/env python
from ROOT import TGraphErrors, TFile, TTree, gDirectory, TGraph2D
from glob import glob
import os

def create_calibration_file():
    '''Create a root file that contains a TF1 and a TGraph to map the measured voltage to the number of electron'''
    nCh = 19
    gr0 = [TGraphErrors() for j in range(nCh)]
    grs = [TGraphErrors() for j in range(nCh)]
    gEs = [TGraphErrors() for j in range(nCh)]
    vx = [int(os.path.basename(fname).split('_')[2][:-2]) for fname in glob('data/fpgaLin/Jan22b_C2_*mV_f1000.dat')]

    h_quality = TGraph2D()

    for v in sorted(vx):
        fname = 'data/fpgaLin/Jan22b_C2_{0:d}mV_f1000.dat'.format(v)
        t1 = TTree()
        t1.ReadFile(fname)

        for ch in range(nCh):
            t1.Draw('A>>h1',"ch=={0:d}".format(ch),"goff")
            h1 = gDirectory.Get('h1')
            h1.SetName('h'+str(v)+'_ch'+str(ch))
            r = h1.Fit('gaus','0S')
            fun1 = h1.GetFunction('gaus')


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


    fout = TFile('fout_calib.root','recreate')
    for i in range(nCh):
        grs[i].Write('gr_mean_ch'+str(i))
        gEs[i].Write('gr_sigma_ch'+str(i))

        gr0[i].Fit('pol1','C')
        gr0[i].Write('gr_calib_ch'+str(i))

    h_quality.Write('fitQ')
    fout.Close()


def test1():
    print "testing"
    create_calibration_file()

if __name__ == "__main__":
    test1()
