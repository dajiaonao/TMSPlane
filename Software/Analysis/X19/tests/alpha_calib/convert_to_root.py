#!/usr/bin/env python3
import os
from ROOT import TFile, TTree, TDatime, TObjString
from array import array
from multiprocessing import Process, Pool
from glob import glob
import re

def to_root(filenames, outroot='temp.root'):
    Nsample = 20000000
    data1 = array('B',[0]*Nsample)
#     xIncr = array('f',[0])
#     xZero = array('f',[0])
#     yMult = array('f',[0])
#     yOff = array('f',[0])
#     yZero = array('f',[0])
    idx = array('i',[0])
    T = TDatime()

    f2 = TFile(outroot,"recreate")
    t1 = TTree("tr1",'a simple tree')
    t1.Branch('data', data1, 'data[20000000]/b')
#     t1.Branch("xInc", xIncr,'xInc/F')
#     t1.Branch("xZero", xZero,'xZero/F')
#     t1.Branch("yMult", yMult,'yMult/F')
#     t1.Branch("yOff", yOff,'yOff/F')
#     t1.Branch("yZero", yZero,'yZero/F')
    t1.Branch("idx", idx,'idx/I')
    t1.Branch("T", T)


    meta = None

    for filename in filenames:
        if not os.path.exists(filename): continue
        print(f"Processing {filename}")

        idx[0] = -1
        try:
            idx[0] = int(os.path.basename(filename).split('_')[-1][:-4])
        except:
            pass

        with open(filename,'rb') as f1:
            b0 = f1.read(1024)
            a1i = b0.find(b":WFMOUTPRE")
            b1i = b0.find(b':CURVE')
            a = b0[a1i:b1i] # :WFMOUTPRE info
            b = b0[:a1i] # DATA, TIME
            c = b.split(b';')

            b2 = b0[b1i:]
            c += [b2]

            if meta != a:
                metaT = TObjString(os.path.basename(filename)+a.decode())
                metaT.Write(f"meta_{t1.GetEntries()}")
                meta = a

            pars = {}
            for v in c:
                a = v.find(b" ")
                pars[v[:a]] = v[a+1:]
#             for p in pars: print(p, pars[p])

            wav = pars[b':CURVE'][10:]
            wav += f1.read()[:-1]

            for i in range(Nsample): data1[i] = wav[i]
#             xIncr[0] = float(pars[b'XINCR'])
#             xZero[0] = float(pars[b'XZERO'])
#             yMult[0] = float(pars[b'YMULT'])
#             yOff[0] = float(pars[b'YOFF'])
#             yZero[0] = float(pars[b'YZERO'])

            T.Set("{} {}".format(pars[b":DATE"].decode().strip('"'), pars[b":TIME"].decode().strip('"')))
#             print(T)

        t1.Fill()

    t1.Write()
    f2.Close()

def test():
#     to_root([f"/home/TMSTest/PlacTests/TMSPlane/data/fpgaLin/raw/Jan15a/TPCHV2kV_PHV0V_air4_10.isf"])
# to_root([f"/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air_{d}.isf" for d in range(1000)], "TPCHV2kV_PHV0V_air.root")
#     to_root([f"/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air_640.isf"])
    to_root([f"/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air_{640+d}.isf" for d in range(10)]+[f"/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air_{d}.isf" for d in range(10)])

def process_files(inDir, outDir, tag, doAll=False, oTag='s'):
    ### check output dir
    if not os.path.exists(outDir): os.makedirs(outDir)

    ### start the merge
    si = -1
    while True:
        si += 1
        fout = f"{outDir}{tag}{oTag}{si}.root"
        if os.path.exists(fout): continue
        
        fin_last = inDir+f"{tag}{si*1000+999}.isf"
        if not os.path.exists(inDir+f"{tag}{si*1000}.isf"):
            if si==0:print(inDir+f"{tag}{si*1000}.isf not found...")
            break

        if os.path.exists(fin_last) or doAll:
            fs = [inDir+f"{tag}{d}.isf" for d in range(si*1000, (si+1)*1000) if os.path.exists(inDir+f"{tag}{d}.isf")]
            print(f"will merge {fs[0]}...{fs[-1]} to {fout}")
            to_root(fs, fout)

def process_air4():
    print("Hello, Hello")
    inDir = '/home/TMSTest/PlacTests/TMSPlane/data/fpgaLin/raw/Jan15a/'
    outDir = '/home/TMSTest/PlacTests/TMSPlane/data/fpgaLin/merged/Jan15a/'
    tag = 'TPCHV2kV_PHV0V_air4_'

    ### check output dir
    if not os.path.exists(outDir): os.makedirs(outDir)

    ### start the merge
    si = -1
    while True:
        si += 1
        fout = f"{tag}s{si}.root"
        if os.path.exists(fout): continue
        
        fin_last = inDir+f"{tag}{si*1000+999}.isf"
        if not os.path.exists(fin_last): break

        fs = [inDir+f"{tag}{d}.isf" for d in range(si*1000, (si+1)*1000)]
        print(f"will merge {fs[0]}...{fs[-1]} to {fout}")
        to_root([inDir+f"{tag}{d}.isf" for d in range(si*1000, (si+1)*1000)], fout)

def multiprocess(inDir, outDir, tag, doAll=False, oTag='s'):
    p=Process(target=process_files, args=(inDir, outDir, tag, doAll, oTag))
    p.start()

    return p
def processJan19():
#     process_files('/data/Samples/TMSPlane/Jan15a/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHV2kV_PHV0V_air4_', doAll=True, oTag='t')
#     process_files('/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15b/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHVoff_PHVvary_gasoff0_', doAll=True, oTag='t')
    process_files('/run/media/dzhang/Backup\ Plus/TMS_data/Jan15b/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHVoff_PHVvary_gasoff0_', doAll=True, oTag='t')
    process_files('/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15d/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHVoff_gasOff_Pulse_5mV', doAll=True, oTag='t')
#     a = []
#     a.append(multiprocess('/data/Samples/TMSPlane/Jan15a/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHV2kV_PHV0V_air4_', doAll=True, oTag='t'))
#     a.append(multiprocess('/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15b/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHVoff_PHVvary_gasoff0_', doAll=True, oTag='t'))
#     a.append(multiprocess('/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15d/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHVoff_gasOff_Pulse_', doAll=True, oTag='t'))
# 
#     for p in a: p.join()


def to_root_single_arg(argx):
    to_root(argx[1], argx[0])

def sortDir(pattern,outDir, tag='s', prallel=True):
    dic1 = {}
    for f in glob(pattern):
        f0 = os.path.basename(f)
#         print(f0)
        m = re.match("(.*)_(\d+).isf", f0)
        if m is None:
            print(f"problem with {f0}")
            continue
        try:
            dic1[m.group(1)].append((f, int(m.group(2))))
        except KeyError:
            dic1[m.group(1)] = [(f, int(m.group(2)))]

    if outDir[-1] != '/': outDir+='/'
    if not os.path.exists(outDir): os.makedirs(outDir) 

    jobList = []
    for k in dic1:
#         print(k, len(dic1[k]), sorted(dic1[k], key=lambda x: x[1]))
        print('merging', k, len(dic1[k]))
        fs2 = sorted(dic1[k], key=lambda x: x[1])
        fs = [x[0] for x in fs2]
        
        nStart = 0
        nFs = len(fs)
        while nStart<nFs:
            nEnd = nStart + 1000
            if nEnd>nFs:nEnd = nFs
            fs1 = fs[nStart:nEnd]
            nStartx = fs2[nStart][1]
            nEndx = fs2[nEnd-1][1]
            fout = outDir+f'{k}_{tag}{nStartx}_{nEndx}.root'

            print(f"outfile: {fout}")
#             print(fs1)
            if prallel: jobList.append((fout, fs1))
            else: to_root(fs1, fout)

            nStart = nEnd

    ### submit jobs 
    if jobList:
        p = Pool(3)
        ret = p.map(to_root_single_arg, jobList)
 
if __name__ == '__main__':
#     process_air4()
#     process_files('/data/Samples/TMSPlane/Jan15a/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHV2kV_PHV0V_air3_', doAll=True, oTag='t') # t is the letter after s
#     process_files('/data/Samples/TMSPlane/Jan15a/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHV2kV_PHV0V_air_', doAll=True, oTag='t') # t is the letter after s
#     process_files('/data/Samples/TMSPlane/Jan15a/','/data/Samples/TMSPlane/merged/Jan15a/','TPCHV2kV_PHV0V_air2_', doAll=True, oTag='t') # t is the letter after s
#     test()
#     processJan19()
#     sortDir("/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15d/*.isf", "/data/Samples/TMSPlane/merged/Jan15a/", 't')
#     sortDir("/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15b/TPCHVoff_PHVvary_*.isf", "/data/Samples/TMSPlane/merged/Jan15a/", 't')
#     sortDir("/home/dzhang/work/repos/TMSPlane/data/raw2/Jan15a/TPC*_air*.isf", "/data/Samples/TMSPlane/merged/Jan15a/", 'n')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Aug13a_tek/*.isf", "/run/media/TMSTest/TMSdisk2/raw2/merged/Aug13a_tek/", 'n')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Sep03a_tek/*.isf", "/run/media/TMSTest/TMSdisk2/raw2/merged/Sep03a_tek/", 'n')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Aug27a_tek/*.isf", "/run/media/TMSTest/TMSdisk2/raw2/merged/Aug27a_tek/", 'n')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Sep29a_tek/*.isf", "/run/media/TMSTest/TMSdisk2/raw2/merged/Sep29a_tek/", 'n')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Aug13a_tek/*.isf", "/run/media/TMSTest/TMSdisk2/raw2/merged/Aug13a_tek/", 'n')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Aug31a_tek/*.isf", "/run/media/TMSTest/TMSDisk3/raw3/merged3/Aug31a_tek/", '')
#     sortDir("/data/TMS_data/raw2/Jul16a_tek/*.isf", "/run/media/TMSTest/TMSDisk3/raw3/merged3/Jul16a_tek/", '')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Sep10a_tek/*.isf", "/run/media/TMSTest/TMSdisk2/raw2/merged/Sep10a_tek/", '')
#     sortDir("/run/media/TMSTest/TMSdisk2/raw2/Sep20a_tek/*.isf", "/run/media/TMSTest/TMSDisk3/raw3/merged3/Sep20a_tek/", '')
#     for d in ['Aug10a_tek','Aug27b_tek','Jul13a_tek','Jul16b_tek','Jul16c_tek','Jul16d_tek','Jul16e_tek','Jul17a_tek','Jul21a_tek','Jul22a_tek','Jul23a_tek','Jul24a_tek','Jul30a_tek','Jun24a_tek','Jun30a_tek','Sep24a_tek','Sep30a_tek']:
#         sortDir(f"/run/media/TMSTest/TMSdisk2/raw2/{d}/*.isf", f"/run/media/TMSTest/TMSdisk2/raw2/merged/{d}/", '')
    for d in ['Aug13a_tek','Oct05a_tek']:
        sortDir(f"/data/TMS_data/raw3/{d}/*.isf", f"/run/media/TMSTest/TMSdisk2/raw2/merged/{d}/", '')
