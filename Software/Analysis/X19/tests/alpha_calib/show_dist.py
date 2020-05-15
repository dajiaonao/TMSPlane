#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from ROOT import TGraphErrors, gStyle, gPad, TLatex, TFile, TCanvas
from rootUtil3 import waitRootCmdX, useNxStyle, savehistory
uA = 1000000.

def get_dv(fname, info1=None):
    lines = None
    with open(fname,'r') as fin1:
        lines = fin1.readlines()
    if lines is None:
        print("Error")
        return

    dictx = {}
    for line in lines:
        line = line.rstrip().split()
        v = int(line[4])
        try:
            dictx[v].append(float(line[1])*uA)
        except KeyError:
            dictx[v] = [float(line[1])*uA]

    list1 = []
    for k in dictx.keys():
        mean = np.mean(dictx[k])
        list1 += [f-mean for f in dictx[k]]

    plt.plot(list1)
    if info1 is not None:
        max1 = max(list1)
        plt.text(0,max1*0.95, info1)
    plt.grid(True)
    plt.show()


def get_graph(fname,rf=1,dv=5):
    lines = None
    with open(fname,'r') as fin1:
        lines = fin1.readlines()
    if lines is None:
        print("Error")
        return

    dictx = {}
    values = []
    for line in lines:
        line = line.rstrip().split()
        v = int(line[4])
        try:
            dictx[v].append(float(line[1]))
        except KeyError:
            dictx[v] = [float(line[1])]

    gr1 = TGraphErrors()
    i = 0
    for k in dictx.keys():
        if len(dictx[k])<10: continue
        print(k, np.mean(dictx[k]), np.std(dictx[k]))
        gr1.SetPoint(i,rf*k/1000.,-np.mean(dictx[k])*1000000.)
        gr1.SetPointError(i, dv/1000., np.std(dictx[k])*1000000.)
        i += 1

    return gr1

def show_dv():
    get_dv('/data/Samples/TMSPlane/HVCheck/R2_pico0.dat','pico0')
    get_dv('/data/Samples/TMSPlane/HVCheck/R2_pico1.dat','pico1')
    get_dv('/data/Samples/TMSPlane/HVCheck/R2_pico2.dat','pico2')
    get_dv('/data/Samples/TMSPlane/HVCheck/R2_pico3.dat','pico3')
#     get_dv('/data/Samples/TMSPlane/HVCheck/R1_pico1.dat','picometer1')
#     get_dv('/data/Samples/TMSPlane/HVCheck/R1_pico8.dat','picometer8')
#     get_dv('/data/Samples/TMSPlane/HVCheck/R_Dongwen.dat','Dongwen')
#     get_dv('/data/Samples/TMSPlane/HVCheck/R_iseg.dat','Iseg')
#     get_dv('/data/Samples/TMSPlane/HVCheck/R_picometer.dat','picometer')

def get_grs():
    gr0 = get_graph('/data/Samples/TMSPlane/HVCheck/R_Dongwen.dat')
    gr1 = get_graph('/data/Samples/TMSPlane/HVCheck/R_iseg.dat')
    gr2 = get_graph('/data/Samples/TMSPlane/HVCheck/R_picometer.dat', rf=-1, dv=0.05)

    gr2.SetLineColor(4)
    gr2.SetMarkerColor(4)
    gr1.SetLineColor(2)
    gr1.SetMarkerColor(2)
    gr1.Draw('AP')
    gr2.Draw('P SAME')
    gr0.Draw('P SAME')

    waitRootCmdX()

    fout1 = TFile('fout1.root','recreate')
    fout1.cd()
    gr0.Write('gr0')
    gr1.Write('gr1')
    gr2.Write('gr2')
    fout1.Close()

def check_graph2(fname='/data/Samples/TMSPlane/HVCheck/R_Dongwen.dat', info1='Dongwen', fitfun='pol3'):
    lines = None
    rf = 1
    dv = 5
    print(info1[:4])
    if info1[:4]=='pico':
        rf = -1
        dv = 0.05

    with open(fname,'r') as fin1:
        lines = fin1.readlines()
    if lines is None:
        print("Error")
        return

    dictx = {}
    values = []
    for line in lines:
        line = line.rstrip().split()
        v = int(line[4])
        try:
            dictx[v].append(float(line[1]))
        except KeyError:
            dictx[v] = [float(line[1])]

    gr1 = TGraphErrors()
    i = 0
    for k in dictx.keys():
        print(k, np.mean(dictx[k]), np.std(dictx[k]))
        gr1.SetPoint(i,rf*k/1000.,-np.mean(dictx[k])*1000000.)
        gr1.SetPointError(i, dv/1000., np.std(dictx[k])*1000000.)
        i += 1

    gr1.Fit(fitfun,"","S")

    c1 = TCanvas("c1","c1",1400,900)
    c1.Divide(2,1)
    c1.cd(1)
    gr1.Draw('AP')
    h1 = gr1.GetHistogram()
    h1.GetXaxis().SetTitle('U [kV]')
    h1.GetYaxis().SetTitle('I [#muA]')

    lt = TLatex()
    lt.DrawLatexNDC(0.2,0.92,info1)


    c1.cd(2)
    gr2 = TGraphErrors()
    fun1 = gr1.GetFunction(fitfun)
    for i in range(gr1.GetN()):
        x = gr1.GetPointX(i)
        y = gr1.GetPointY(i)
        gr2.SetPoint(i,x,y-fun1.Eval(x))
        gr2.SetPointError(i,gr1.GetErrorX(i),gr1.GetErrorY(i))
    gr2.Draw()
    h2 = gr2.GetHistogram()
    h2.GetXaxis().SetTitle('U [kV]')
    h2.GetYaxis().SetTitle('#DeltaI [#muA]')

    c1.cd()
    gPad.Update()
    waitRootCmdX()


def check_graph(fname='/data/Samples/TMSPlane/HVCheck/R_Dongwen.dat', info1='Dongwen', fitfun='pol3'):
    lines = None
    rf = 1
    dv = 5
    rf = -1
    dv = 0.05

#     info1 = 'Iseg'
#     info1 = 'Dongwen'
    with open(fname,'r') as fin1:
#     with open('/data/Samples/TMSPlane/HVCheck/R_iseg.dat','r') as fin1:
    #     with open('/data/Samples/TMSPlane/HVCheck/R_picometer.dat','r') as fin1:
        lines = fin1.readlines()
    if lines is None:
        print("Error")
        return

    dictx = {}
    values = []
    for line in lines:
        line = line.rstrip().split()

#         print(line[4],line[1])
        v = int(line[4])
        try:
            dictx[v].append(float(line[1]))
        except KeyError:
            dictx[v] = [float(line[1])]

#     values = dictx[240]
#     plt.plot(values)
#     plt.show()
#     gStyle.SetOptStat(1111)
#     gStyle.SetLineColor(2)

    gr1 = TGraphErrors()
    i = 0
    for k in dictx.keys():
        print(k, np.mean(dictx[k]), np.std(dictx[k]))
        gr1.SetPoint(i,rf*k/1000.,-np.mean(dictx[k])*1000000.)
        gr1.SetPointError(i, dv/1000., np.std(dictx[k])*1000000.)
        i += 1

#     gr1.Fit('pol1',"","S")
    gr1.Fit(fitfun,"","S")
    gr1.Draw('AP')
    h1 = gr1.GetHistogram()
    h1.GetXaxis().SetTitle('U [kV]')
    h1.GetYaxis().SetTitle('I [#muA]')
#     gr1.Draw('AP')
#     fun1 = gr1.GetFunction('pol3')
#     fun1.SetLineColor(2)
#     fun1.Draw('same')
# 
    lt = TLatex()
    lt.DrawLatexNDC(0.2,0.92,info1)
    gPad.Update()
    waitRootCmdX()

if __name__ == '__main__':
    savehistory('./')
    useNxStyle()
    gStyle.SetFuncColor(2)
#     check_graph('/data/Samples/TMSPlane/HVCheck/R1_pico1.dat','pico1',fitfun='pol1')
#     check_graph('/data/Samples/TMSPlane/HVCheck/R1_pico8.dat','pico8',fitfun='pol1')
#     check_graph('/data/Samples/TMSPlane/HVCheck/R2_pico0.dat','pico0',fitfun='pol1')
#     check_graph('/data/Samples/TMSPlane/HVCheck/R2_pico1.dat','pico1',fitfun='pol1')
#     check_graph2('/data/Samples/TMSPlane/HVCheck/R2_pico0.dat','pico0',fitfun='pol1')
#     check_graph2('/data/Samples/TMSPlane/HVCheck/R2_pico1.dat','pico1',fitfun='pol1')
#     check_graph2('/data/Samples/TMSPlane/HVCheck/R2_pico3.dat','pico3',fitfun='pol1')
    show_dv()
#     test()
