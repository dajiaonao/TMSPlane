#!/usr/bin/env python3
import sys
from hv_calc import get_Vd 
from iseg_control import simpleSetHV
from picoammeter_control import run_quasicontinious_recording
import time

pA = 1e-12

def checkPoint(HV, mode=0):
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


def show_results(isDebug=False):
    from run_step_fit import fit_ds
    from glob import glob
    import re,os

    summary_file = 'temp1.ttl'
    dir1 = '/data/TMS_data/raw/Jul24a/' 
    fs = glob('/data/TMS_data/raw/Jul24a/*.dat')

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
        m = re.match(r'Ar_totalI_IsegFd(\d+)_HVscan.*.dat', os.path.basename(fname))
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

            results.append((k, tList_end[k], fr[0], fr[1], fr[2], HV_values[k]))

        ### save results to database
        with open(summary_file,modex) as fout1:
            if modex == 'w': fout1.write('timeId/C:tEnd/F:mean/F:error/F:fitQ/F:HV/I')

            for aa in results:
                fout1.write(f'\n{aa[0]} {aa[1]} {aa[2]} {aa[3]} {aa[4]} {aa[5]}')

#         return


def showScan(fname='temp1.ttl'):
    '''This does not work in python....'''
    from ROOT import TTree, TGraphErrors
    t1 = TTree()
    t1.ReadFile(fname)
    n = t1.Draw("mean:error:HV")
    a = t1.GetV1()
    b = t1.GetV2()
    c = t1.GetV3()

    g1 = TGraphErrors(n, a, b, c)
    g1.Draw()

    a = input("tt")

def test():
    HV = int(sys.argv[1])
    test(HV)

if __name__ == '__main__':
#     test()
#     scan()
    show_results(True)
#     showScan()
