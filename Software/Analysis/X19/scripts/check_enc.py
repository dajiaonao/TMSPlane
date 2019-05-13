#!/usr/bin/env python36

from ROOT import TChain, TGraphErrors, gPad, gDirectory
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
        fout.write('\n{0:d} {1:d} {2:.3f} {3:.1f} {4} {5} {6} {7} {8:.2g} {9:d} {10:.1f}'.format(ich, tag, vPulse,hx.GetEntries(), fun1.GetParameter(1), fun1.GetParError(1), fun1.GetParameter(2), fun1.GetParError(2), r.Prob(), r.Status(), enc))
    return enc, r.Prob(), fun1.GetParameter(1)

def test():
    ch1 = TChain('tree1')
    ch1.Add(tmsDir+'/Software/Control/src/C3_tt6_valid1.root')
    ch1.Show(0)
    nCh = 19

    with open('C3_tt6_valid1_enc.ttl','w') as fout:
        fout.write('ch/I:tag/I:v/f:Nevt/I:mean/F:meanErr/F:sigma/F:sigmaErr/F:prob/F:status/I:enc/F')
        for i in range(nCh):
            for j in range(10):
                checkENC1(ch1, i, j, 2.0, fout)
#         checkENC1(ch1, 1, 3, 2.0, fout)

if __name__ == "__main__":
    test()
