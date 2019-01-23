#!/usr/bin/env python
from SignalChecker import SignalChecker

from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor
from array import array

def readSignal(inRoot, outText, freq=1000):
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
    for x in [500, 150, 200, -1.]: sp1.fltParam.push_back(x)

    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    while ip+n1<sp1.nSamples:
        sp1.sRanges.push_back((ip, ip+n1))
        ip += n1

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))

#     inRoot = 'data/fpgaLin/Jan21b_C2_100mV_f1000.root'
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    with open(outText,'w') as fout:
        fout.write(':'.join(['sID/I', 'ch/I', 'B/F','dB/F', 'im/I','idx/I','A/F']))

        for ievt in range(tree1.GetEntries()):
            tree1.GetEntry(ievt)

            sp1.measure_pulse(data1)
            for i in range(sp1.nAdcCh):
                itmp = sp1.nMeasParam*i
                for j in range(sp1.nMeasParam/2-1):
                    fout.write('\n'+' '.join([str(ievt), str(i), str(sp1.measParam[itmp]), str(sp1.measParam[itmp+1]), str(j), str(int(sp1.measParam[itmp+2*j+2])), str(sp1.measParam[itmp+2*j+3])]))


def testJ():
    sc1 = SignalChecker()
    sc1.control_ip_port = "localhost:1024"
    dir1 = 'data/fpgaLin/'
    tag1 = dir1+'Jan22a_C2_100mV_'
    for f in [100,200,500,1000]:
#         setPulse(0.1,f)
#         time.sleep(20)
#         sc1.take_samples2(5000, tag1+"f{0:d}.root".format(f))
        if f not in [1000]: continue
        sc1.check_enc2(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f))

if __name__ == '__main__':
#     testJ()
#     readSignal(inRoot = 'data/fpgaLin/Jan21b_C2_100mV_f1000.root', outText='temp1.dat')
    readSignal(inRoot = 'data/fpgaLin/Jan22a_C2_100mV_f1000.root', outText='temp1.dat')
