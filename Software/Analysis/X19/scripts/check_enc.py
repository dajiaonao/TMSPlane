#!/usr/bin/env python3
from glob import glob
from ROOT import TFile, TChain, TGraphErrors, gPad, gDirectory, TCanvas
from array import array
import os
tmsDir = os.getenv('HOME')+'/work/repos/TMSPlane'
# import sys
# sys.path.append(tmsDir+'/Software/Control/src')


def checkENC1(ch, ich, tag, vPulse=2., fout=None):
    n1 = ch.Draw("val[{0:d}]".format(ich),'tag=={0:d}'.format(tag),'goff')
#     hx = gPad.GetPrimitive('htemp')
    hx = gDirectory.Get('htemp')
    r = hx.Fit('gaus','S')
    fun1 = hx.GetFunction('gaus')
    enc = vPulse*741*fun1.GetParameter(2)/fun1.GetParameter(1)
    if fout:
        fout.write('\n{0:d} {1:d} {2:.3f} {3:g} {4} {5} {6} {7} {8:.2g} {9:d} {10:.1f}'.format(ich, tag, vPulse,hx.GetEntries(), fun1.GetParameter(1), fun1.GetParError(1), fun1.GetParameter(2), fun1.GetParError(2), r.Prob(), r.Status(), enc))
    return enc, r.Prob(), fun1.GetParameter(1)

def checkENC2(ch, ich, vPulse=2., fout=None, cut=''):
    tag = -1
    n1 = ch.Draw("Q[{0:d}]".format(ich),cut,'goff')
    hx = gDirectory.Get('htemp')
    r = hx.Fit('gaus','S')
    fun1 = hx.GetFunction('gaus')
    hx.Draw()
    iPulse = int(vPulse*1000)
    gPad.SaveAs(f'ch{ich}_{iPulse}mV.png')
    enc = vPulse*10*741*fun1.GetParameter(2)/fun1.GetParameter(1)
    enc_err = enc*( (fun1.GetParError(1)/fun1.GetParameter(1))**2 + (fun1.GetParError(2)/fun1.GetParameter(2))**2 )**0.5
    if fout:
        fout.write('\n{0:d} {1:d} {2:.3f} {3:g} {4} {5} {6} {7} {8:.2g} {9:d} {10:.1f}'.format(ich, tag, vPulse,hx.GetEntries(), fun1.GetParameter(1), fun1.GetParError(1), fun1.GetParameter(2), fun1.GetParError(2), r.Prob(), r.Status(), enc))
    #return enc, enc_err, fun1.GetParameter(1), fun1.GetParError(1), r.Prob(), fun1.GetParameter(1)
    return vPulse, enc, enc_err, fun1.GetParameter(1), fun1.GetParError(1)

def test():
    ch1 = TChain('tree1')
    ch1.Add(tmsDir+'/Software/Control/src/C3_tt6_valid1.root')
    ch1.Show(0)
    nCh = 19

    with open('C3_tt6_valid1_enc.ttl','w') as fout:
        fout.write('ch/I:tag/I:v/f:Nevt/f:mean/F:meanErr/F:sigma/F:sigmaErr/F:prob/F:status/I:enc/F')
        for i in range(nCh):
            for j in range(10):
                checkENC1(ch1, i, j, 2.0, fout)
#         checkENC1(ch1, 1, 3, 2.0, fout)

def checkC7_Oct08():
    with open('C7_enc_trig5thre0d005_test_DC50.ttl','w') as fout:
        fout.write('ch/I:tag/I:v/f:Nevt/I:mean/F:meanErr/F:sigma/F:sigmaErr/F:prob/F:status/I:enc/F')
#/data/TMS_data/Processed/Oct08_TMS/trig5thre0d005_test_DC50_PP3000_data_0.root
        for f in glob('/data/TMS_data/Processed/Oct08_TMS/trig5thre0d005_test_DC50_PP*_data_0.root'):
            print(f.split('_')[5])
            v = float(f.split('_')[5][2:])*0.001
            print(f'processing {f}, with v = {v}')
            f1 = TFile(f,'read')
            t1 = f1.Get('reco')
            checkENC2(t1, 5, v, fout)

def checkC7_Oct08_TGraph():
    lresult = []
    for f in glob('/data/TMS_data/Processed/Oct08_TMS/trig5thre0d005_test_DC50_PP*_data_0.root'):
        print(f.split('_')[5])
        v = float(f.split('_')[5][2:])*0.001
        print(f'processing {f}, with v = {v}')
        f1 = TFile(f,'read')
        t1 = f1.Get('reco')
        lresult.append(checkENC2(t1, 5, v))
        print(len(lresult))

    n = len(lresult)
    x = array('f',[lresult[i][0]*10*741 for i in range(n)])
    ex = array('f',[0 for i in range(n)])
    yenc = array('f',[lresult[i][1] for i in range(n)])
    eyenc = array('f',[lresult[i][2] for i in range(n)])
    ymean = array('f',[lresult[i][3] for i in range(n)])
    eymean = array('f',[lresult[i][4] for i in range(n)])

    grenc = TGraphErrors(n,x,yenc,ex,eyenc)
    cenc = TCanvas("cenc","cenc",0,0,800,600)
    henc = cenc.DrawFrame(0,20,30000,25)
    grenc.Draw("P same")
    henc.GetXaxis().SetTitle("N [e^{-}]")
    henc.GetYaxis().SetTitle("ENC [e^{-}]")

    cenc.SaveAs("enc.png")

    grmean = TGraphErrors(n,x,ymean,ex,eymean)
    cmean = TCanvas("cmean","cmean",0,0,800,600)
    hmean = cmean.DrawFrame(0,0,30000,0.9)
    grmean.Draw("P same")
    grmean.Fit('pol1',"","",0,22000)
    hmean.GetXaxis().SetTitle("N [e^{-}]")
    hmean.GetYaxis().SetTitle("V_{out}[V]")

    cmean.SaveAs("mean.png")

    a = input("aaa")

if __name__ == "__main__":
#     test()
    checkC7_Oct08_TGraph()
