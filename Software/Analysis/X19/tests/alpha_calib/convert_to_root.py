#!/usr/bin/env python3
import os
from ROOT import TFile, TTree, TDatime
from array import array

def to_root(filenames):
    Nsample = 20000000
    data1 = array('B',[0]*Nsample)
    xIncr = array('f',[0])
    xZero = array('f',[0])
    yMult = array('f',[0])
    yOff = array('f',[0])
    yZero = array('f',[0])
    T = TDatime()

    f2 = TFile("out1.root","recreate")
    t1 = TTree("tr1",'a simple tree')
    t1.Branch('cdx', data1, 'cdx[20000000]/b')
    t1.Branch("xInc", xIncr,'xInc/F')
    t1.Branch("xZero", xZero,'xZero/F')
    t1.Branch("yMult", yMult,'yMult/F')
    t1.Branch("yOff", yOff,'yOff/F')
    t1.Branch("yZero", yZero,'yZero/F')
    t1.Branch("T", T)

    print(t1.GetEntries())

    for filename in filenames:
        if not os.path.exists(filename): continue
        with open(filename,'rb') as f1:
            b0 = f1.read(1024)
            b1i = b0.find(b':CURVE')
            b = b0[:b1i]
            c = b.split(b';')

            b2 = b0[b1i:]
            c += [b2]

            pars = {}
            for v in c:
                a = v.find(b" ")
                pars[v[:a]] = v[a+1:]
            for p in pars: print(p, pars[p])

            wav = pars[b':CURVE'][10:]
            wav += f1.read()[:-1]

            for i in range(Nsample): data1[i] = wav[i]
            xIncr[0] = float(pars[b'XINCR'])
            xZero[0] = float(pars[b'XZERO'])
            yMult[0] = float(pars[b'YMULT'])
            yOff[0] = float(pars[b'YOFF'])
            yZero[0] = float(pars[b'YZERO'])

            T.Set("{} {}".format(pars[b":DATE"].decode().strip('"'), pars[b":TIME"].decode().strip('"')))
            print(T)

        t1.Fill()

    t1.Write()
    f2.Close()

# to_root([f"/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air2_{d}.isf" for d in range(20)])
to_root([f"/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air2_0.isf"])
