#!/usr/bin/env python
from SignalChecker import SignalChecker

from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor
from array import array

from multiprocessing import Pool
from glob import glob


def readSignal(inRoot, outText, freq=1000):
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
    for x in [500, 150, 200, -1.]: sp1.fltParam.push_back(x)

    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    dn = 2500%n1 ## 2500 is the expected position of the signal
    while ip+dn < sp1.nSamples:
        sp1.sRanges.push_back((ip, min(ip+n1, sp1.nSamples)))
        ip += n1

#     while ip+n1<sp1.nSamples:
#         sp1.sRanges.push_back((ip, ip+n1))
#         ip += n1

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


def check_Jan22a(f):
    tag1 = 'data/fpgaLin/Jan22a_C2_100mV_'
    readSignal(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f), f)

def testK():
    p = Pool(4)
    p.map(check_Jan22a, [100,200,500,1000])


def check_Jan22b(v):
    tag1 = 'data/fpgaLin/Jan22b_C2_{0:d}mV_f1000'.format(v)
    readSignal(tag1+'.root', tag1+".dat", 1000)

def test_Jan22b():
    p = Pool(6)
#     p.map(check_Jan22b, [50+50*i for i in range(10)])
#     p.map(check_Jan22bx, glob('data/fpgaLin/Jan22b_C2_*5mV*.root'))
    p.map(check_Jan22bx, glob('data/fpgaLin/Jan24a_C2_*.root'))

def check_Jan22bx(fname):
    out = fname[:-5]+'.dat'
    print "Starting", fname, out
    readSignal(fname, out, 1000)

def testJ():
    sc1 = SignalChecker()
    sc1.control_ip_port = "localhost:1024"
    dir1 = 'data/fpgaLin/'
    tag1 = dir1+'Jan22a_C2_100mV_'
    for f in [100,200,500,1000]:
#         setPulse(0.1,f)
#         time.sleep(20)
#         sc1.take_samples2(5000, tag1+"f{0:d}.root".format(f))
#         if f not in [1000]: continue
#         sc1.check_enc2(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f))
        readSignal(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f), f)

def check_calib():
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20

    ### setup the calibration file
    fin1 = TFile('fout_calib.root')
    sp1.corr_spine.clear()
    sp1.corr_TF1.clear()
    sp1.corr_spine.reserve(sp1.nAdcCh)
    sp1.corr_TF1.reserve(sp1.nAdcCh)
    for i in range(sp1.nAdcCh-1):
        sp1.corr_spine.push_back(fin1.Get('gr_calib_ch'+str(i)))
        sp1.corr_TF1.push_back(sp1.corr_spine[i].GetFunction('pol1'))
    
    ## run a test
    for x in sp1.corr_spine[5].GetX():
        t = 1
        print sp1.correction(1,x)*t, sp1.correction(1,x, 1)*t, '|', sp1.correction(5,x)*t, sp1.correction(5,x, 1)*t

if __name__ == '__main__':
#     testJ()
#     testK()
    test_Jan22b()
#     readSignal(inRoot = 'data/fpgaLin/Jan22a_C2_100mV_f500.root', outText='data/fpgaLin/Jan22a_C2_100mV_f500.dat', freq=500)
#     check_calib()
