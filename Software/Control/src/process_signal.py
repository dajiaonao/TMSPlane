#!/usr/bin/env python
from SignalChecker import SignalChecker

from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor
from array import array

from multiprocessing import Pool
from glob import glob
import os, time, re

def readSignal2(inRoot, oTag=None, freq=1000, runPattern='.*_data_(\d+).root'):
    if oTag is None:
        oTag = readSignal2.oTag
    print "Starting", inRoot, oTag
#     return

    run = -1
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            run = int(m.group(1))
    print run

    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
#     for x in [50, 150, 200, -1.]: sp1.fltParam.push_back(x)
#     for x in [50, 150, 200, 2500]: sp1.fltParam.push_back(x)
    for x in [50, 15, 50, 2500]: sp1.fltParam.push_back(x)

    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    dn = 2500%n1 ## 2500 is the expected position of the signal
#     while ip+dn < sp1.nSamples:
#         sp1.sRanges.push_back((ip, min(ip+n1, sp1.nSamples)))
#         ip += n1

    sp1.sRanges.push_back((0, 400))

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))
    dataT = array('i',[0])

    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)
    tree1.SetBranchAddress('T',dataT)

    fout1 = TFile(os.path.dirname(inRoot)+'/'+oTag+os.path.basename(inRoot),'recreate')
    tup1 = TNtuple('tup1',"filter analysis tuple",'run:sID:ch:B:dB:im:idx:A:T')

    for ievt in range(tree1.GetEntries()):
        tree1.GetEntry(ievt)

        sp1.measure_pulse(data1)
        for i in range(sp1.nAdcCh):
            itmp = sp1.nMeasParam*i
            for j in range(sp1.nMeasParam/2-1):
                tup1.Fill(run, ievt, i, sp1.measParam[itmp], sp1.measParam[itmp+1], j, sp1.measParam[itmp+2*j+2], sp1.measParam[itmp+2*j+3], dataT[0]-788947200)

    tup1.Write()
    fout1.Close()

def readSignal(inRoot, outText, freq=1000):
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
    for x in [50, 150, 200, -1.]: sp1.fltParam.push_back(x)

    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    dn = 2500%n1 ## 2500 is the expected position of the signal
#     while ip+dn < sp1.nSamples:
#         sp1.sRanges.push_back((ip, min(ip+n1, sp1.nSamples)))
#         ip += n1

    sp1.sRanges.push_back((0, 400))
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
#     p.map(check_Jan22bx, glob('data/fpgaLin/Jan24a_C2_*.root'))
    p.map(check_Jan22bx, glob('data/fpgaLin/Jan25a_C2_*.root'))

def test_Feb06c(oTag):
    p = Pool(6)

    files = sorted([f for f in glob('data/fpgaLin/Feb06c_data_*.root') if not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))], key=lambda f:os.path.getmtime(f))
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print "dropping the latest file, which probably is still being written:", files[-1]
        files.pop()

#     p.map(check_Jan22bx, files)
#     p.map(check_Jan22by, files)
    p.map(readSignal2, files)
# readSignal2.oTag = 'sp2_'

def test_Feb09(oTag):
    p = Pool(6)

    files = sorted([f for f in glob('data/fpgaLin/Feb09*_data_*.root') if not os.path.exists(f.replace('/Feb','/'+oTag+'Feb'))], key=lambda f:os.path.getmtime(f))
    if time.time() - os.path.getmtime(files[-1]) < 10:
        print "dropping the latest file, which probably is still being written:", files[-1]
        files.pop()

#     p.map(check_Jan22bx, files)
#     p.map(check_Jan22by, files)
    p.map(readSignal2, files)
readSignal2.oTag = 'sp2_'


def check_Jan22by(fname):
    tag = 'sp_'
    print "Starting", fname, tag
    readSignal2(fname, tag, 1000)

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
#     test_Jan22b()
#     readSignal(inRoot = 'data/fpgaLin/Jan22a_C2_100mV_f500.root', outText='data/fpgaLin/Jan22a_C2_100mV_f500.dat', freq=500)
#     readSignal(inRoot = 'data/fpgaLin/Feb05a_noise_dc_ch19.root', outText='data/fpgaLin/Feb05a_noise_dc_ch19.dat', freq=100)
#     readSignal(inRoot = 'data/fpgaLin/Feb06a_noise_dc_ch19.root', outText='data/fpgaLin/Feb06a_noise_dc_ch19.dat', freq=100)
#     readSignal2(inRoot = 'data/fpgaLin/Feb06c_data_50.root', oTag='t1_')
#     readSignal2(inRoot = 'data/fpgaLin/Feb09a_data_1.root', oTag='sp0_')
#     readSignal(inRoot = 'data/fpgaLin/Feb06b_data_1.root', outText='data/fpgaLin/Feb06b_data_1.dat', freq=100)
#     check_calib()
    test_Feb09('sp2_')
#     test_Feb06c('sp2_')
