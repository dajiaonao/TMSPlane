#!/usr/bin/env python36
import matplotlib.pyplot as plt
from array import array
from ROOT import gROOT
gROOT.LoadMacro("sp.C+")
from ROOT import filters_trapezoidal
# from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent
import numpy as np


def find_H0(values, thre):
    vHx = []
    v_max = None
    for v in values:
        if v>thre:
            if v_max is None or v>v_max: v_max = v
        else:
            if v_max:
                vHx.append(v_max)
                v_max = None
    return vHx

def find_H(values, thre, fall=0.9):
    vHx = []
    v_max = None
    v_w = 0
    n_raise = 0

    for v in values:
        if v>thre:
            v_w += 1
            if v_max is None or v>v_max:
                v_max = v
                n_raise += 1
            elif v < v_max*fall:
                if n_raise> 20: vHx.append((v_max,v_w))
                v_max = None
                v_w = 0
                n_raise = 0
        else:
            if v_max:
                if n_raise> 20: vHx.append((v_max,v_w))
                v_max = None
                v_w = 0
                n_raise = 0
    return vHx

def test1():
    print("test")
    dir1 = '/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun26a/'
    INTVAL = 200

    try:
        for ievt in range(2000):
            if ievt % INTVAL == 0: print(f'{ievt} events processed')

            vlaues = None
            with open(dir1+'evt_Jun26a_{0:d}.dat'.format(ievt)) as f1:
                values = [float(l.rstrip().split()[1]) for l in f1.readlines()]
#             print(np.std(values[:2000]))
            vv = np.std(values[:2000])
            if vv>0.0035: continue


            NP = len(values)
            inWav = array('f',values)
            outWav = array('f',[0.]*NP)

            filters_trapezoidal(NP,inWav,outWav,500,2000,3125)
            ret = find_H(outWav,0.008,0.8)
            print(ret)

#               print(values[:10])
    #         plt.plot(values)
            plt.plot(outWav)
            plt.show()
    except KeyboardInterrupt:
        pass



def run1():
    dir1 = '/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun26a/'
    INTVAL = 200
    NEVT = 2000

    try:
        with open('check2.dat','w') as fout1:
            fout1.write('evt/I:inst/I:A/F:W/I')
            for ievt in range(NEVT):
                if ievt % INTVAL == 0: print(f'{ievt} events processed')

                vlaues = None
                with open(dir1+'evt_Jun26a_{0:d}.dat'.format(ievt)) as f1:
                    values = [float(l.rstrip().split()[1]) for l in f1.readlines()]
#                 print(np.std(values[:2000]))
                vv = np.std(values[:2000])
                if vv>0.0035: continue


                NP = len(values)
                inWav = array('f',values)
                outWav = array('f',[0.]*NP)

                filters_trapezoidal(NP,inWav,outWav,500,2000,3125)
                ret = find_H(outWav,0.005, 0.9)

                if ret:
                    for i in range(len(ret)):
                        fout1.write('\n'+str(ievt)+' '+str(i)+' '+str(ret[i][0])+' '+str(ret[i][1]))

    #             print(find_H(outWav,0.01))
        #         print(values[:10])
    #             plt.plot(values)
    #             plt.plot(outWav)
    #             plt.show()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
#     test()
#     test1()
    run1()
