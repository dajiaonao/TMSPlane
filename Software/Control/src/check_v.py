#!/usr/bin/env python

from ROOT import *
from rootUtil import waitRootCmdX, useNxStyle
from glob import glob
import os
import numpy as nm

def getV(fname):
    f1 = TFile(fname,'read')
    t1 = f1.Get('tree1')
    if not t1: return None

    n1 = t1.Draw("adc[19]","Entry$==20","goff")
    x1 = t1.GetV1()
    vv = [x1[i] for i in range(9000,10000)]
#     print vv
    return nm.mean(vv), nm.std(vv)

def test2():
    infiles = 'data/fpgaLin/Jan28b*.root'
    vx = [(int(os.path.basename(fname).split('_')[2][:-2]),fname) for fname in glob(infiles)]
    
    opt = ''
    c = 1
    gr = TGraphErrors()
    for v in sorted(vx, key=lambda x:x[0], reverse=True):
        a = getV(v[1])
        if a is not None:
            n = gr.GetN()
            gr.SetPoint(n, v[0], a[0])
            gr.SetPointError(n, 0, a[1])
#         break

    fun0 = TF1('fun0','pol1', 0,800)
    fun1 = TF1('fun1','pol1', 0,295)
    fun2 = TF1('fun2','pol1', 295,595)
    fun3 = TF1('fun3','pol1', 595,800)
    fun0.SetLineColor(kGray)
    fun1.SetLineColor(2)
    fun2.SetLineColor(3)
    fun3.SetLineColor(4)

    gr.Fit(fun0,'R')
    gr.Fit(fun1,'R+')
    gr.Fit(fun2,'R+')
    gr.Fit(fun3,'R+')
#     gr.Fit('pol1')
#     fun1 = gr.GetFunction('pol1')
#     fun1.SetLineColor(2)
#     fun1.SetLineStyle(2)

    gStyle.SetOptFit(0)
    gr.Draw('AP')
    h1 = gr.GetHistogram()
    h1.GetXaxis().SetTitle("Input [mV]")
    h1.GetYaxis().SetTitle("Output [V]")

    waitRootCmdX()




def test1():
    infiles = 'data/fpgaLin/Jan28b*.root'
    vx = [(int(os.path.basename(fname).split('_')[2][:-2]),fname) for fname in glob(infiles)]
    
    opt = ''
    c = 1
    for v in sorted(vx, key=lambda x:x[0], reverse=True):
        print v[0], v[1]
        f1 = TFile(v[1],'read')
        t1 = f1.Get('tree1')
        if not t1: continue
        t1.SetMarkerColor(c)
        n1 = t1.Draw("adc[19]:Iteration$","Entry$==10",opt)
        opt = 'same'
        c += 1
    waitRootCmdX()

       

if __name__ == '__main__':
    useNxStyle()
#     test1()
    test2()
