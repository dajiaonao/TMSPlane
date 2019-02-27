#!/usr/bin/env python
# from ROOT import TGraphErrors, TFile, TTree, gDirectory, TGraph2D, TIter
from ROOT import * 
from glob import glob
import os, re
from rootUtil import waitRootCmdX, useNxStyle, get_default_fig_dir
from 

sDir = get_default_fig_dir()
sTag = 'test1_'


def create_calibration_file2(infiles='data/fpgaLin/sp01a_Feb26b_*mV_f1000.dat',outfile='fout_calib1.root'):
    '''Create a root file that contains a TF1 and a TGraph to map the measured voltage to the number of electron'''
    nCh = 20
    gr0 = [TGraphErrors() for j in range(nCh)]
    grs = [TGraphErrors() for j in range(nCh)]
    gEs = [TGraphErrors() for j in range(nCh)]
    vx = [(int(os.path.basename(fname).split('_')[-2][:-2]),fname) for fname in glob(infiles)]

    h_quality = TGraph2D()
    h_ENC = TGraph2D()

    fout = TFile(outfile,'recreate')

    for vi in sorted(vx, key=lambda x:x[0]):
        v = vi[0]
        fname = vi[1] 
        t1 = TChain('tup1')
        t1.Add(fname)

        for ch in range(nCh):
            cut0 = '' if ch==19 else "imean>200&&"
            t1.Draw('A>>h1',cut0+"ch=={0:d}".format(ch),"goff")
            h1 = gDirectory.Get('h1')
            h1.SetName('h'+str(v)+'_ch'+str(ch))

#             r = h1.Fit('gaus','S')
#             h1.Fit('gaus')
# 
#             fun1 = h1.GetFunction('gaus')
# 
            x1 = h1.GetXaxis().GetBinCenter(h1.GetMaximumBin())
            std = h1.GetStdDev()
            fun1 = TF1('fun1','gaus',x1-2.5*std, x1+2.5*std)
# #             fun1.Draw()
# #             waitRootCmdX()
# #             fun1.SetRange(x1-2.5*std, x1+2.5*std)
# #             print x1-2.5*std, x1+2.5*std
            r = h1.Fit(fun1,'RS')

            if (not fun1) or (not r):
                h1.Draw()
                print ch, v
                waitRootCmdX()
#             h1.Draw()
#             waitRootCmdX()

            h1.Write()


            g1 = grs[ch]
            n = g1.GetN()
            g1.SetPoint(n,v,fun1.GetParameter(1))
            g1.SetPointError(n,0,fun1.GetParError(1))

            g2 = gEs[ch]
            g2.SetPoint(n,v,fun1.GetParameter(2))
            g2.SetPointError(n,0,fun1.GetParError(2))

            h_quality.SetPoint(nCh*n+ch, v, ch, r.Chi2())
            h_ENC.SetPoint(nCh*n+ch, v, ch, 7.40*v*fun1.GetParameter(2)/fun1.GetParameter(1))

            g0 = gr0[ch]
            g0.SetPoint(n,fun1.GetParameter(1),v)
            g0.SetPointError(n,fun1.GetParError(1),0)


    for i in range(nCh):
        grs[i].Write('gr_mean_ch'+str(i))
        gEs[i].Write('gr_sigma_ch'+str(i))

        r = gr0[i].Fit('pol1','S')
        h_quality.SetPoint(nCh*len(vx)+i, -1, i, r.Chi2())

        gr0[i].Write('gr_calib_ch'+str(i))

    h_quality.Write('fitQ')
    h_ENC.Write('ENC')
    fout.Close()



def create_calibration_file1(infiles='data/fpgaLin/sp01a_Feb26b_*mV_f1000.dat',outfile='fout_calib1.root'):
    '''Create a root file that contains a TF1 and a TGraph to map the measured voltage to the number of electron'''
    nCh = 20
    gr0 = [TGraphErrors() for j in range(nCh)]
    grs = [TGraphErrors() for j in range(nCh)]
    gEs = [TGraphErrors() for j in range(nCh)]
    vx = [(int(os.path.basename(fname).split('_')[-2][:-2]),fname) for fname in glob(infiles)]

    h_quality = TGraph2D()
    h_ENC = TGraph2D()

    fout = TFile(outfile,'recreate')

    for vi in sorted(vx, key=lambda x:x[0]):
        v = vi[0]
        fname = vi[1] 
        t1 = TChain('tup1')
        t1.Add(fname)

        for ch in range(nCh):
            cut0 = '' if ch==19 else "imean>200&&"
            t1.Draw('A>>h1',cut0+"ch=={0:d}".format(ch),"goff")
            h1 = gDirectory.Get('h1')
            h1.SetName('h'+str(v)+'_ch'+str(ch))

#             r = h1.Fit('gaus','S')
#             h1.Fit('gaus')
# 
#             fun1 = h1.GetFunction('gaus')
# 
            x1 = h1.GetXaxis().GetBinCenter(h1.GetMaximumBin())
            std = h1.GetStdDev()
            fun1 = TF1('fun1','gaus',x1-2.5*std, x1+2.5*std)
# #             fun1.Draw()
# #             waitRootCmdX()
# #             fun1.SetRange(x1-2.5*std, x1+2.5*std)
# #             print x1-2.5*std, x1+2.5*std
            r = h1.Fit(fun1,'RS')

            if (not fun1) or (not r):
                h1.Draw()
                print ch, v
                waitRootCmdX()
#             h1.Draw()
#             waitRootCmdX()

            h1.Write()


            g1 = grs[ch]
            n = g1.GetN()
            g1.SetPoint(n,v,fun1.GetParameter(1))
            g1.SetPointError(n,0,fun1.GetParError(1))

            g2 = gEs[ch]
            g2.SetPoint(n,v,fun1.GetParameter(2))
            g2.SetPointError(n,0,fun1.GetParError(2))

            h_quality.SetPoint(nCh*n+ch, v, ch, r.Chi2())
            h_ENC.SetPoint(nCh*n+ch, v, ch, 7.40*v*fun1.GetParameter(2)/fun1.GetParameter(1))

            g0 = gr0[ch]
            g0.SetPoint(n,fun1.GetParameter(1),v)
            g0.SetPointError(n,fun1.GetParError(1),0)


    for i in range(nCh):
        grs[i].Write('gr_mean_ch'+str(i))
        gEs[i].Write('gr_sigma_ch'+str(i))

        r = gr0[i].Fit('pol1','S')
        h_quality.SetPoint(nCh*len(vx)+i, -1, i, r.Chi2())

        gr0[i].Write('gr_calib_ch'+str(i))

    h_quality.Write('fitQ')
    h_ENC.Write('ENC')
    fout.Close()



def create_calibration_file(infiles='data/fpgaLin/Jan22b_C2_*mV_f1000.dat',outfile='fout_calib.root'):
    '''Create a root file that contains a TF1 and a TGraph to map the measured voltage to the number of electron'''
    nCh = 19
    gr0 = [TGraphErrors() for j in range(nCh)]
    grs = [TGraphErrors() for j in range(nCh)]
    gEs = [TGraphErrors() for j in range(nCh)]
    vx = [(int(os.path.basename(fname).split('_')[2][:-2]),fname) for fname in glob(infiles)]

    h_quality = TGraph2D()

    fout = TFile(outfile,'recreate')

    for vi in sorted(vx, key=lambda x:x[0]):
        v = vi[0]
        fname = vi[1] 
        t1 = TTree()
        t1.ReadFile(fname)

        for ch in range(nCh):
            t1.Draw('A>>h1',"ch=={0:d}&&A>0.003".format(ch),"goff")
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


def check_calibration(calibFile='fout_calib.root', tag1 = 'Jan22a_'):
    fout = TFile(calibFile,'read')

    nCh = 20
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

        range_y = max_y*1.1
        h2.GetYaxis().SetRangeUser(0,range_y)
        h2.GetXaxis().SetRangeUser(0,max_x)

        lt.DrawLatexNDC(0.2,0.88,"Channel {0:d}".format(ch))


        g1 = fout.Get('gr_calib_ch'+str(ch))
#         g1.Draw('P same')

        g2 = fout.Get('gr_mean_ch'+str(ch))
        g3 = fout.Get('gr_sigma_ch'+str(ch))
        X2 = g2.GetX()
        Y2 = g2.GetY()
        EX2 = g2.GetEX()
        Y3 = g3.GetY()

        g4 = TGraphErrors(g2.GetN(), Y2, X2, Y3, EX2)
        for i in range(g4.GetN()): g4.GetY()[i] *= max_y/max(X2); 

        g4.SetLineColor(4)
        g4.SetMarkerStyle(20)
        g4.Fit('pol1', 'F EX0')
        fun1 = g4.GetFunction('pol1')
        fun1.SetLineColor(kGray)

        canv = gPad
        canv.Update()
        axis2 = TGaxis(canv.GetUxmax(), canv.GetUymin(), canv.GetUxmax(), canv.GetUymax(),0.,max(X2)*1.1,510,"+L"); ##or better line below
        axis2.SetTitle('Input pulse [mV]')
        axis2.Draw(); 

        g4.Draw("Psame")
#         fun1.Draw('same')
        waitRootCmdX(sDir+tag1+'check_ch{0:d}'.format(ch))

def test1():
#     create_calibration_file()
#     create_calibration_file('data/fpgaLin/Jan24a_C2_*mV_f1000.dat','Jan24a_calib.root')
#     create_calibration_file('data/fpgaLin/Jan25a_C2_*mV_f1000.dat','Jan25a_calib.root')
#     create_calibration_file1('data/fpgaLin/sp01a_Feb26b_*mV_f1000.root','Feb26b_calib1.root')
    create_calibration_file1('data/fpgaLin/sp02a_Feb26b_*mV_f1000.root','Feb26b_calib2.root')

def test2():
    useNxStyle()
    gStyle.SetPalette(55)
    gStyle.SetOptFit(0)
    gStyle.SetPadRightMargin(0.1)
    gStyle.SetFuncColor(2)
#     check_calibration('Jan25a_calib.root', 'Jan25a_')
    check_calibration('Feb26b_calib1.root', 'Feb26b_')

if __name__ == "__main__":
    gStyle.SetFuncColor(2)
    test1()
#     test2()

