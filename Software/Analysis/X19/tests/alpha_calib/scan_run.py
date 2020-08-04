#!/usr/bin/env python3
import sys
from hv_calc import get_Vd, checkConfig3, checkConfig3b 
from iseg_control import simpleSetHV
from picoammeter_control import run_quasicontinious_recording
import time

pA = 1e-12

def checkPointC(HV, rawHV, mode=0, out_dir='/data/TMS_data/raw/Jul24a/', tag='HVscan'):
    v1 = rawHV
    ### Set iseg to the value
    simpleSetHV(int(v1))
    time.sleep(10)
    if mode == 1: return 1

    ### run picoammber to 
    run_quasicontinious_recording(out_dir+f'{tag}_IsegFd{HV:.0f}.dat',extraStr=f" {HV:.0f} {v1:.0f}", nrps=1000, nRead=1)
    if mode == 1: return 1

    return 0



def checkPoint(HV, mode=0, out_dir='/data/TMS_data/raw/Jul24a/', tag='HVscan'):
    ### get the raw HV value
    v1 = checkConfig3(HV, show=False)
    print(v1)

    ### Set iseg to the value
    simpleSetHV(int(v1))
    time.sleep(10)
    if mode == 1: return 1

    ### run picoammber to 
    run_quasicontinious_recording(out_dir+f'{tag}_IsegFd{HV:.0f}.dat',extraStr=f" {HV:.0f} {v1:.0f}", nrps=1000, nRead=1)
    if mode == 1: return 1

    return 0



def checkPoint_v0(HV, mode=0):
    dir1 = '/data/TMS_data/raw/Jul24a/'

    ### get the raw HV value
    v1 = get_Vd(HV)
    print(v1)

    ### Set iseg to the value
    simpleSetHV(int(v1))
    time.sleep(10)
    if mode == 1: return 1

    ### run picoammber to 
    run_quasicontinious_recording(dir1+f'Ar_totalI_IsegFd{HV:.0f}_HVscanRound2.dat',extraStr=f" {HV:.0f} {v1:.0f}", nrps=1000, nRead=1)
    if mode == 1: return 1

    return 0

def scan():
#     for p in [700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300, 1400, 1500]:
#     for p in range(1600,2600,100):
    for p in [20,40,60,80,120,200,500]:
        print(f"On HV point {p}")
#         continue

        r = checkPoint(p, 0)
        if r != 0: break
        time.sleep(10)

    simpleSetHV('OFF')

def scan_Aug01():
#     for p in [700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300, 1400, 1500]:
    for p in range(1600,2600,100):
#     for p in [20,40,60,80,100,120,150,200,250,300,350,400,450,500,550,600,650]:
#     for p in [120, 150]:
        print(f"On HV point {p}")

        r = checkPoint(p, 0, out_dir='/data/TMS_data/raw/Aug01a/', tag='Air_totalI_HVscan')
        if r != 0: break
        time.sleep(10)

    simpleSetHV('OFF')

def scan_Aug01b():
    for p in range(1600,2600,100):
        print(f"On HV point {p}")

        ### get the raw HV value
        v1 = checkConfig3b(p, show=False)
        print(f'{p}->{v1}')

        r = checkPointC(p, v1, 0, out_dir='/data/TMS_data/raw/Aug01a/', tag='Air_totalI_HVscan')
        if r != 0: break
        time.sleep(10)

    simpleSetHV('OFF')

def show_results(in_dir='/data/TMS_data/raw/Jul24a/', summary_file = 'temp1.ttl', isDebug=False):
    from run_step_fit import fit_ds
    from glob import glob
    import re,os

    fs = glob(in_dir+'*.dat')

    results_exist = []
    ### get values from database
    get_values = lambda fs: (fs[0], float(fs[1]), float(fs[2]), float(fs[3]), float(fs[4]), int(fs[5]))
    modex = 'w'
    if os.path.exists(summary_file):
        modex = 'a'
        with open(summary_file,'r') as fin1:
            results_exist += [get_values(line.rstrip().split()) for line in fin1.readlines() if len(line.split())>1]
    elif summary_file is not None:
        outdir = os.path.dirname(summary_file)
        if not os.path.exists(outdir): os.makedirs(outdir)

    flist = [a[0] for a in results_exist]

    #'/data/TMS_data/raw/Jul24a/Ar_totalI_IsegFd1300_HVscan.dat'
    for fname in fs:
#         m = re.match(r'Ar_totalI_IsegFd(\d+)_HVscan.dat', os.path.basename(fname))
        m = re.match(r'Air_totalI_HVscan_IsegFd(\d+).dat', os.path.basename(fname))
#         m = re.match(r'Ar_totalI_IsegFd(\d+)_HVscan.*.dat', os.path.basename(fname))
        if m is None:
            print(fname)
            continue

        ### get data from file
        dList = {}
        tList_start = {}
        tList_end = {}
        HV_values = {}
        with open(fname,'r') as fin1:
            lines = fin1.readlines()

        for line in lines:
            fs = line.split()

            try:
                dList[fs[0]].append(float(fs[1])/pA)
            except KeyError:
                dList[fs[0]] = [float(fs[1])/pA]
                tList_start[fs[0]] = float(fs[2])

            tList_end[fs[0]] = float(fs[2])
            HV_values[fs[0]] = int(fs[7])

        ### process data
        results = [] 
        for k,v in dList.items():
            if k in flist: continue
            fr = fit_ds(v, show=isDebug, check=isDebug)

            if fr is None:
                print(k, fr)
                continue
            results.append((k, tList_end[k], fr[0], fr[1], fr[2], HV_values[k]))

        ### save results to database
        with open(summary_file,modex) as fout1:
            if modex == 'w': fout1.write('timeId/C:tEnd/F:mean/F:error/F:fitQ/F:HV/I')

            for aa in results:
                fout1.write(f'\n{aa[0]} {aa[1]} {aa[2]} {aa[3]} {aa[4]} {aa[5]}')

#         return


def showScan(fname='temp1.ttl'):
    '''This does not work in python....'''
    from ROOT import TTree, TGraphErrors, gStyle, gPad
    gStyle.SetOptTitle(0)

    t1 = TTree()
    t1.ReadFile(fname)
    print(t1.GetEntries())
    n = t1.Draw("abs(mean):error:HV:0.*HV","","goff")
    v1 = t1.GetV1()
    v2 = t1.GetV2()
    v3 = t1.GetV3()
    v4 = t1.GetV4()

    g1 = TGraphErrors(n, v3, v1, v4, v2)
    g1.Draw('AP')
    h1 = g1.GetHistogram()
    h1.GetXaxis().SetTitle("Drift HV [V]")
    h1.GetYaxis().SetTitle("Current [pA]")
    gPad.Update()

    a = input("tt")

def test():
    HV = int(sys.argv[1])
    test(HV)

if __name__ == '__main__':
#     test()
#     scan()
#     scan_Aug01()
#     scan_Aug01b()
#     show_results(True)
#     show_results(in_dir='/data/TMS_data/raw/Aug01a/',summary_file='/data/TMS_data/Processed/Aug01a/HVscan_summary.ttl', isDebug=False)
    showScan('/data/TMS_data/Processed/Aug01a/HVscan_summary.ttl')
