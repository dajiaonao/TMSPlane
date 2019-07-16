#!/usr/bin/env python36
import matplotlib.pyplot as plt
from array import array
from ROOT import gROOT, TChain, TFile
gROOT.LoadMacro("sp.C+")
from ROOT import filters_trapezoidal
# from ROOT import SignalProcessor, Event, Sig, showEvents, showEvent
import numpy as np
import glob


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

def find_H1(values, thre, fall=0.9):
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

def find_H(values, thre, fall=0.9, iRef=-2600):
    vHx = []
    v_max = None
    v_w = 0
    n_raise = 0

    idx = 0
    for v in values:
        if v>thre:
            v_w += 1
            if v_max is None or v>v_max:
                v_max = v
                n_raise += 1
            elif v < v_max*fall:
                if n_raise> 20:
                    if idx+iRef >=0: v_max -= values[idx+iRef]
                    vHx.append((v_max,v_w,idx))
                v_max = None
                v_w = 0
                n_raise = 0
        else:
            if v_max:
                if n_raise> 20:
                    if idx+iRef >=0: v_max -= values[idx+iRef]
                    vHx.append((v_max,v_w,idx))
                v_max = None
                v_w = 0
                n_raise = 0
        idx += 1
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

def check2(fname):
    print("test")
    INTVAL = 200

    plt.ion()
    plt.show()
    fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))
    ax1.set_xlabel('time index')
    ax1.set_ylabel('U [V]', color='b')
    ax1.tick_params('y', colors='b')
    ax2 = ax1.twinx()
    ax2.set_ylabel('U [V]', color='r')
    ax2.tick_params('y', colors='r')


    f1 = TFile(fname,'read')
    tree1 = f1.Get('tree1')

    NP = 62500
    inWav = array('f',[0.]*NP)
    outWav = array('f',[0.]*NP)
    tree1.SetBranchAddress('val1',inWav)


    NEVT = tree1.GetEntries()
    ievt = 0
    while ievt < NEVT:
        try:
            if ievt % INTVAL == 0: print(f'{ievt} events processed')

            tree1.GetEntry(ievt)

            filters_trapezoidal(NP,inWav,outWav,500,2000,3125)
            ret = find_H(outWav,0.008,0.8)
            print(ret)

            values = inWav

            ax1.clear()
            ax2.clear()
            ax1.plot(inWav, label='Raw', color='b')
            ax2.plot(outWav, label='Filtered', color='r')
            ylim1 = ax1.get_ylim()
            ylim2 = ax2.get_ylim()

            x1 = min(ylim1[0], ylim2[0]+values[0])
            x2 = max(ylim1[1], ylim2[1]+values[0])
            ax1.set_ylim(x1,x2)
            ax2.set_ylim(x1-values[0],x2-values[0])

            fig.tight_layout()
            plt.draw()
            plt.legend()
            plt.grid(True)
            plt.pause(0.001)

            ievt += 1
            a = input("next:")
            if a == 'q': break
            elif len(a)==0: continue
            elif a[0] == 'e':
                try:
                    ax = int(a[1:])
                    ievt = ax
                except ValueError:
                    continue

        except KeyboardInterrupt:
            break
def check1():
    print("test")
    dir1 = '/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27g/'
    INTVAL = 200

    plt.ion()
    plt.show()
    fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))
    ax1.set_xlabel('time index')
    ax1.set_ylabel('U [V]', color='b')
    ax1.tick_params('y', colors='b')
    ax2 = ax1.twinx()
    ax2.set_ylabel('U [V]', color='r')
    ax2.tick_params('y', colors='r')

    try:
        for ievt in range(2000):
            if ievt % INTVAL == 0: print(f'{ievt} events processed')

            vlaues = None
            with open(dir1+'evt_Jun27g_{0:d}.dat'.format(ievt)) as f1:
                values = [float(l.rstrip().split()[1]) for l in f1.readlines() if len(l)>0 and l[0]!='#']
#                 values = [float(l.rstrip().split()[1]) for l in f1.readlines()]
            vv = np.std(values[:2000])
            print(vv)
#             if vv>0.0035: continue


            NP = len(values)
            inWav = array('f',values)
            outWav = array('f',[0.]*NP)

            filters_trapezoidal(NP,inWav,outWav,500,2000,3125)
            ret = find_H(outWav,0.008,0.8)
            print(ret)


            ax1.clear()
            ax2.clear()
            ax1.plot(values, label='Raw', color='b')
            ax2.plot(outWav, label='Filtered', color='r')
            ylim1 = ax1.get_ylim()
            ylim2 = ax2.get_ylim()

            x1 = min(ylim1[0], ylim2[0]+values[0])
            x2 = max(ylim1[1], ylim2[1]+values[0])
            ax1.set_ylim(x1,x2)
            ax2.set_ylim(x1-values[0],x2-values[0])

            fig.tight_layout()
            plt.draw()
            plt.legend()
            plt.grid(True)
            plt.pause(0.001)

            a = input("next:")
            if a == 'q': break

    except KeyboardInterrupt:
        pass
def run3(files=None, ofname=None, INTVAL = 200):
    '''Same as run1, but use file list instead of file id'''

    ### configuration
    if files is None: files = ['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun26b/evt_Jun26b_*.dat']
    if ofname is None: ofname = 'check2b.dat'

    ### prepare for the loop
    fileList = []
    for fl in files: fileList += glob.glob(fl)
    muteWarning1 = False

    try:
        with open(ofname,'w') as fout1:
            fout1.write('evt/I:inst/I:A/F:W/I:vv/F')
            ifile = 0
            for fname in fileList:
#                 if DEBUG: print(fname)
                ievt = -1
                try:
                    ievt = int(fname.split('_')[-1][:-4])
                except TypeError as e:
                    if not muteWarning1:
#                         print(e,fname, fname.split('_')[-1][:-4], ievt)
                        muteWarning1 = True

                if ifile % INTVAL == 0: print(f'{ifile} events processed')
                ifile += 1

                vlaues = None
                with open(fname,'r') as f1:
                    values = [float(l.rstrip().split()[1]) for l in f1.readlines() if len(l)>0 and l[0]!='#']
#                     values = [float(l.rstrip().split()[1]) for l in f1.readlines()]
#                 print(values[:2000])
#                 print(vv)
#                 if vv>0.0035: continue

                NP = len(values)
                inWav = array('f',values)
                outWav = array('f',[0.]*NP)

                filters_trapezoidal(NP,inWav,outWav,500,2000,3125)
                ret = find_H(outWav,0.005, 0.9)
#                 ret = find_H(outWav,0.008,0.8)
#                 print(ret)

                if ret:
                    vv = ' ' + str(np.std(values[:2000]))
                    for i in range(len(ret)):
                        fout1.write('\n'+str(ievt)+' '+str(i)+' '+str(ret[i][0])+' '+str(ret[i][1])+vv)

    except KeyboardInterrupt:
        pass



def run2(files=None, ofname=None, INTVAL = 200):
    '''Same as run1, but use file list instead of file id'''

    ### configuration
    if files is None: files = ['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun26b/evt_Jun26b_*.dat']
    if ofname is None: ofname = 'check2b.dat'

    ### prepare for the loop
    fileList = []
    for fl in files: fileList += glob.glob(fl)
    muteWarning1 = False

    try:
        with open(ofname,'w') as fout1:
            fout1.write('evt/I:inst/I:A/F:W/I')
            ifile = 0
            for fname in fileList:
#                 if DEBUG: print(fname)
                ievt = -1
                try:
                    ievt = int(fname.split('_')[-1][:-4])
                except TypeError as e:
                    if not muteWarning1:
#                         print(e,fname, fname.split('_')[-1][:-4], ievt)
                        muteWarning1 = True

                if ifile % INTVAL == 0: print(f'{ifile} events processed')
                ifile += 1

                vlaues = None
                with open(fname,'r') as f1:
                    values = [float(l.rstrip().split()[1]) for l in f1.readlines() if len(l)>0 and l[0]!='#']
#                     values = [float(l.rstrip().split()[1]) for l in f1.readlines()]
#                 print(values[:2000])
                vv = np.std(values[:2000])
#                 print(vv)
                if vv>0.0035: continue

                NP = len(values)
                inWav = array('f',values)
                outWav = array('f',[0.]*NP)

                filters_trapezoidal(NP,inWav,outWav,500,2000,3125)
                ret = find_H(outWav,0.005, 0.9)
#                 ret = find_H(outWav,0.008,0.8)
#                 print(ret)

                if ret:
                    for i in range(len(ret)):
                        fout1.write('\n'+str(ievt)+' '+str(i)+' '+str(ret[i][0])+' '+str(ret[i][1]))

    except KeyboardInterrupt:
        pass

def run3(infiles, ofname=None, INTVAL = 200):
    '''Same as run1, but use file list instead of file id'''

    ### configuration
    if ofname is None: ofname = 'check2bx.dat'

    tree1 = TChain('tree1')
    for infile in infiles: tree1.Add(infile)

    NP = 62500
    ### IO configuration
    data1 = array('f',[0]*(NP))
    dataT = array('i',[0])

    tree1.SetBranchAddress('data1',data1)

    outWav = array('f',[0.]*NP)

    try:
        with open(ofname,'w') as fout1:
            fout1.write('evt/I:inst/I:A/F:W/I')
            ifile = 0

            for ievt in range(tree1.GetEntries()):
                if ievt % INTVAL == 0: print(f'{ievt} events processed')

                tree1.GetEntry(ievt)
#                 print(data1[:10])
                if data1[-1] <= -1: print("bad data")

                vv = np.std(data1[:2000])
                if vv>0.0035: continue

                filters_trapezoidal(NP,data1,outWav,500,2000,3125)
                ret = find_H(outWav,0.005, 0.9)

                if ret:
                    for i in range(len(ret)):
                        fout1.write('\n'+str(ievt)+' '+str(i)+' '+str(ret[i][0])+' '+str(ret[i][1]))

    except KeyboardInterrupt:
        pass

def run4(infiles, ofname=None, INTVAL = 200):
    '''Same as run3, but deal with two channles'''

    ### configuration
    if ofname is None: ofname = 'check2bx.dat'

    tree1 = TChain('tree1')
    for infile in infiles: tree1.Add(infile)

    NP = 62500
    dataA = array('f',[0]*(NP))
    ### IO configuration
    data1 = array('f',[0]*(NP))
    data2 = array('f',[0]*(NP))
    dataT = array('i',[0])

    tree1.SetBranchAddress('val1',data1)
    tree1.SetBranchAddress('val3',data2)

    outWav = array('f',[0.]*NP)
    outWav1 = array('f',[0.]*NP)
    outWav2 = array('f',[0.]*NP)

    try:
        with open(ofname,'w') as fout1:
            fout1.write('evt/I:inst/I:A/F:W/I:A1/F:A2/F')
            ifile = 0

            for ievt in range(tree1.GetEntries()):
                if ievt % INTVAL == 0: print(f'{ievt} events processed')

                tree1.GetEntry(ievt)
#                 print(data1[:10])
#                 if data1[-1] <= -1: print("bad data")

                vv = np.std(data1[:2000])
                if vv>0.0035: continue

    
                for i in range(NP): dataA[i] = data1[i]+data2[i]

                filters_trapezoidal(NP,dataA,outWav,500,2000,3125)
                ret = find_H(outWav,0.005, 0.9)

                if ret:
                    filters_trapezoidal(NP,data1,outWav1,500,2000,3125)
                    filters_trapezoidal(NP,data2,outWav2,500,2000,3125)
                    for i in range(len(ret)):
                        idx = ret[i][2]
                        fout1.write('\n'+str(ievt)+' '+str(i)+' '+str(ret[i][0])+' '+str(ret[i][1])+' '+str(outWav1[idx])+' '+str(outWav2[idx]))

    except KeyboardInterrupt:
        pass

def check4(infiles):
    '''do the check based on run 4'''

    tree1 = TChain('tree1')
    for infile in infiles: tree1.Add(infile)

    NP = 62500
    dataA = array('f',[0]*(NP))
    ### IO configuration
    data1 = array('f',[0]*(NP))
    data2 = array('f',[0]*(NP))
    dataT = array('i',[0])

    tree1.SetBranchAddress('val1',data1)
    tree1.SetBranchAddress('val3',data2)

    outWav = array('f',[0.]*NP)
    outWav1 = array('f',[0.]*NP)
    outWav2 = array('f',[0.]*NP)

    fig, axs = plt.subplots(3, 1, sharex=True)
    # Remove horizontal space between axes
    fig.subplots_adjust(hspace=0)

    ax01 = axs[0]
#     ax01.set_xlabel('time index')
#     ax01.set_ylabel('U [V]', color='b')
    ax01.tick_params('y', colors='b')
    ax02 = ax01.twinx()
#     ax02.set_ylabel('U [V]', color='r')
    ax02.tick_params('y', colors='r')

    ax11 = axs[1]
#     ax11.set_xlabel('time index')
#     ax11.set_ylabel('U [V]', color='b')
    ax11.tick_params('y', colors='b')
    ax12 = ax11.twinx()
#     ax12.set_ylabel('U [V]', color='r')
    ax12.tick_params('y', colors='r')

    ax21 = axs[2]
#     ax21.set_xlabel('time index')
#     ax21.set_ylabel('U [V]', color='b')
    ax21.tick_params('y', colors='b')
    ax22 = ax21.twinx()
#     ax22.set_ylabel('U [V]', color='r')
    ax22.tick_params('y', colors='r')


    try:
        for ievt in range(tree1.GetEntries()):
            tree1.GetEntry(ievt)

            vv = np.std(data1[:2000])
            if vv>0.0035: continue

    
            for i in range(NP): dataA[i] = data1[i]+data2[i]

            filters_trapezoidal(NP,dataA,outWav,500,2000,3125)
            ret = find_H(outWav,0.005, 0.9)

            if ret:
                filters_trapezoidal(NP,data1,outWav1,500,2000,3125)
                filters_trapezoidal(NP,data2,outWav2,500,2000,3125)

            ax01.clear()
            ax02.clear()
            ax01.plot(dataA, label='Raw', color='b')
            ax02.plot(outWav, label='Filtered', color='r')
            ylim1 = ax01.get_ylim()
            ylim2 = ax02.get_ylim()
            x1 = min(ylim1[0], ylim2[0]+dataA[0])
            x2 = max(ylim1[1], ylim2[1]+dataA[0])
            ax01.set_ylim(x1,x2)
            ax02.set_ylim(x1-dataA[0],x2-dataA[0])
            ax01.set_ylabel('U [V]', color='b')
            ax02.set_ylabel('U [V]', color='r')


            ax11.clear()
            ax12.clear()
            ax11.plot(data1, label='Raw', color='b')
            ax12.plot(outWav1, label='Filtered', color='r')
            ylim1 = ax11.get_ylim()
            ylim2 = ax12.get_ylim()
            x1 = min(ylim1[0], ylim2[0]+data1[0])
            x2 = max(ylim1[1], ylim2[1]+data1[0])
            ax11.set_ylim(x1,x2)
            ax12.set_ylim(x1-data1[0],x2-data1[0])
            ax11.set_ylabel('U [V]', color='b')
            ax12.set_ylabel('U [V]', color='r')


            ax21.clear()
            ax22.clear()
            ax21.plot(data2, label='Raw', color='b')
            ax22.plot(outWav2, label='Filtered', color='r')
            ylim1 = ax21.get_ylim()
            ylim2 = ax22.get_ylim()
            x1 = min(ylim1[0], ylim2[0]+data2[0])
            x2 = max(ylim1[1], ylim2[1]+data2[0])
            ax21.set_ylim(x1,x2)
            ax22.set_ylim(x1-data2[0],x2-data2[0])
            ax21.set_xlabel('time index')
            ax21.set_ylabel('U [V]', color='b')
            ax22.set_ylabel('U [V]', color='r')

            plt.draw()
            plt.legend()
            plt.grid(True)
            plt.pause(0.001)

            a = input()
            if a == 'q': break

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
                    values = [float(l.rstrip().split()[1]) for l in f1.readlines() if len(l)>0 and l[0]!='#']

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
#     run1()
#     run2()
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27d/*.dat'],ofname='check1c_Jun27d.dat')
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27a/*.dat'],ofname='check1c_Jun27a.dat')
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27b/*.dat'],ofname='check1c_Jun27b.dat')
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27c/*.dat'],ofname='check1c_Jun27c.dat')
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27e/*.dat'],ofname='check1c_Jun27e.dat')
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27g/*.dat'],ofname='check1c_Jun27g.dat')
#     run3(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27f/*.dat'],ofname='check1c_Jun27f.dat')
#     run4(infiles=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jul12a_pulse/Jul12a_pulse_*.root'],ofname='check1a_Jul12a.dat')
#     check1()
#     check2("/data/Samples/TMSPlane/CCNU_tests/plate_data/Jul11a_pulse/Jul11a_pulse_0.root")
    check4(["/data/Samples/TMSPlane/CCNU_tests/plate_data/Jul11a_pulse/Jul11a_pulse_0.root"])

    ### debug
#     run2(files=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jun27g/*_0.dat'],ofname='temp1.dat')
#     run3(infiles=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jul05a.root'],ofname='Jul05a_out.dat')
#     run3(infiles=['/data/Samples/TMSPlane/CCNU_tests/plate_data/Jul05b.root'],ofname='Jul05b_out.dat')
