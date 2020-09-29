#!/usr/bin/env python3
from scipy.signal import find_peaks, peak_prominences
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob, sys
mpl.rc('image', cmap='gray')
mpl.rcParams['text.usetex'] = True

def getinput(filename, i0=5000, ishift1=-200, ishift2=1200):
    i0 = int(i0)
    iFrom = i0+ishift1
    iEnd = i0 + ishift2
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

        timelap = float(pars[b'WFID'].split(b',')[3].split(b'/')[0][1:6])
        timelap *=10
        date = pars[b':DATE'].decode("utf-8").strip('"')
        time = pars[b':TIME'].decode("utf-8").strip('"')

        wav = pars[b':CURVE'][10:]
        wav += f1.read()[:-1]

    wav = wav[iFrom:iEnd]
    wav1 = [signIt(int(x)) for x in wav[::2]] if pars[b'BIT_NR'] == b'16' else [int(x) for x in wav]
    wav1 = [int(x)*0.2 for x in wav]

    return wav1


class WaveformGeter:
    def __init__(self, ishift1=-200, ishift2=1200, debug=False):
        self.ishift1 = ishift1
        self.ishift2 = ishift2
        self.debug = debug
        self.A = None
        self.W = 500
        self.width = (2,600)
        self.proms3Cut = 25
        self.histData = None
        
    def get_auto(self, filename, ith=1, AA=None):
        ishift1=self.ishift1
        ishift2=self.ishift2
        debug=self.debug

        wav = None
        ### get data first
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
    #         print(pars)
            ymult = 1000*float(pars[b'YMULT']) ### default unit is V, and we want to use mV
    #         print(ymult)

            timelap = float(pars[b'WFID'].split(b',')[3].split(b'/')[0][1:6])
            timelap *=10
            date = pars[b':DATE'].decode("utf-8").strip('"')
            time = pars[b':TIME'].decode("utf-8").strip('"')

            wav = pars[b':CURVE'][10:]
            wav += f1.read()[:-1]

        wav1 = [int(x) for x in wav]
    #     arwav2 = map(int, wav) ### convert them to numbers
        arwav2 = np.asarray(wav1)

        ### now find the peaks
        peaks, properties = find_peaks(arwav2, height=None, width=self.width, wlen=self.W, prominence=2, distance=160) 
        promsall = peak_prominences(arwav2, peaks, wlen=self.W)
        promxmins = promsall[1]

        pks = arwav2[peaks]
        proms3 = pks - arwav2[promxmins]

    #     plt.plot(peaks, proms3, "o")
        if debug:
            plt.hist(proms3[proms3>self.proms3Cut], bins=range(0,256))
            plt.show()
    #     ret = plt.hist(proms3[proms3>20], bins=range(0,256))
        self.histData = np.histogram(proms3[proms3>self.proms3Cut], bins=range(0,256))
#         print(ret)

    #     print("Arrays for the max element:",result)
    #     print("List for the maximum value indexes:",result[0])
    # 
    #     ipeaks = np.asarray(range(0, len(proms3)))
    #     pksA = ipeaks[proms3==result[0]]
    #     print(proms3[pksA])
    #     plt.show()

        xx = AA
        arr = self.histData[0]
        if xx is None: xx = self.A
        if xx is None:
            amax = np.max(arr)
            print(f"max is {amax}")
            conditon = (arr == amax)
            results = np.where(conditon)

            xx = results[0]
        yy = arr[xx]

        xxv = xx[-1]
        ### find the one gives max
        cpeaks = peaks[proms3==xxv]
        print(f"Find {yy} events with A={xxv}")
        i0 = cpeaks[ith]
        print(i0)

        x0 = wav1[i0+ishift1]
        thr = 0.1*xxv
        while wav1[i0]-x0>thr: i0 -= 1

        iFrom = i0+ishift1
        iEnd = i0 + ishift2

        x0 = wav1[iFrom]
        wav2 = [(x-x0)*ymult for x in wav1[iFrom:iEnd]]
    #     plt.plot(wav2)
    #     plt.show()
        return wav2

def showShapes():
    dir1 = '/data/TMS_data/raw/Jul30a_tek/'
    getF = lambda x: dir1+'filtered_HV_alphaOn_C3_Fd500_Fc'+x+'.isf' 

    xs = [0.5*x for x in range(-200, 1200)]
    plt.plot(xs, getinput(getF("100_pulse80mV1Hz_61"), 1.37225e7+28), label='100 V')
    plt.plot(xs, getinput(getF("200_pulse80mV1Hz_58"), 9.0984e6+72), label='200 V')
    plt.plot(xs, getinput(getF("300_pulse80mV1Hz_53"), 8.721e6-30), label='300 V')
    plt.plot(xs, getinput(getF("400_pulse80mV1Hz_55"), 9.4765e6+51), label='400 V')
    plt.plot(xs, getinput(getF("500_pulse80mV1Hz_42"), 9.3171e6+42), label='500 V')
    plt.plot(xs, getinput(getF("700_pulse80mV1Hz_49"), 1.3051e7+565), label='700 V')
    plt.plot(xs, getinput(getF("1000_pulse80mV1Hz_46"), 1.36215e7+40), label='1000 V')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()

def check_shapes_500V():
    dir1 = '/data/TMS_data/raw/Jul30a_tek/'
    getF = lambda x: dir1+'filtered_HV_alphaOn_C3_Fd500_Fc'+x+'.isf' 
    xs = [0.5*x for x in range(-200, 1200)]

    wg1 = WaveformGeter()
    plt.plot(xs, wg1.get_auto(getF("100_pulse80mV1Hz_61"), 2), label='100 V')
    plt.plot(xs, wg1.get_auto(getF("200_pulse80mV1Hz_58"), 3), label='200 V')
    plt.plot(xs, wg1.get_auto(getF("300_pulse80mV1Hz_53"), 5), label='300 V')
    plt.plot(xs, wg1.get_auto(getF("400_pulse80mV1Hz_55"), 7), label='400 V')
    plt.plot(xs, wg1.get_auto(getF("500_pulse80mV1Hz_42"), 11), label='500 V')
    plt.plot(xs, wg1.get_auto(getF("700_pulse80mV1Hz_49"), 13), label='700 V')
    plt.plot(xs, wg1.get_auto(getF("1000_pulse80mV1Hz_46"), 17), label='1000 V')


    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def check_shapes_Jun30a_Fc1500V():
    dir1 = '/data/TMS_data/raw/Jun30a_tek/'
    getF = lambda x: dir1+'HV_alphaOn_Focusing_'+x+'.isf'

    wg1 = WaveformGeter()
    wg1.A = 63

    xs = [0.5*x for x in range(-200, 1200)]

    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_240'), 19), label='1500V, 240')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_250'), 19), label='1500V, 250')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_260'), 13), label='1500V, 260')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_271'), 13), label='1500V, 271')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_280'), 13), label='1500V, 280')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def check_shapes_Jun30a_Fc1500V_samefile():
    dir1 = '/data/TMS_data/raw/Jun30a_tek/'
    getF = lambda x: dir1+'HV_alphaOn_Focusing_'+x+'.isf'

    wg1 = WaveformGeter()
    wg1.A = 63

    xs = [0.5*x for x in range(-200, 1200)]

    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_280'), 19, 63), label='1500V, 63')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_280'), 19, 53), label='1500V, 53')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_280'), 17, 43), label='1500V, 43')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_280'), 3, 33,),label='1500V, 33')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_280'), 2, 23), label='1500V, 23')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def check_shapes_Aug10a():
    dir1 = '/data/TMS_data/raw/Aug10a_tek/'
    getF = lambda x: dir1+'filtered_HV_alphaOn_C3_DongwenFd'+x+'.isf'

    wg1 = WaveformGeter()
    wg1.A = None

    xs = [0.5*x for x in range(-200, 1200)]

    plt.plot(xs, wg1.get_auto(getF('1800_IsegFc1200_pulse50mV1Hz_12'), 11), label='1200V, max')
    plt.plot(xs, wg1.get_auto(getF('1800_IsegFc1500_pulse80mV1Hz_10'), 119), label='1500V, max')
    plt.plot(xs, wg1.get_auto(getF('1800_IsegFc2000_pulse80mV1Hz_3'), 39), label='2000V, max')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def check_shapes_Aug10a_drift():
    dir1 = '/data/TMS_data/raw/Aug10a_tek/'
    getF = lambda x: dir1+'filtered_HV_alphaOn_C3_DongwenFd'+x+'.isf'
    getF2 = lambda x: dir1+'filtered_HV_alphaOn_C3_'+x+'.isf'

    wg1 = WaveformGeter()
    wg1.A = None

    xs = [0.5*x for x in range(-200, 1200)]

    plt.plot(xs, wg1.get_auto(getF2('IsegFd382_pulse80mV1Hz_33'), 39), label='382VD, max')
    plt.plot(xs, wg1.get_auto(getF2('IsegFd1800_pulse80mV1Hz_24'), 39), label='1800VD, max')
    plt.plot(xs, wg1.get_auto(getF('1350_IsegFc1500_pulse80mV1Hz_1'), 119), label='1350V, max')
    plt.plot(xs, wg1.get_auto(getF('1800_IsegFc2000_pulse80mV1Hz_3'), 39), label='1800V, max')
    plt.plot(xs, wg1.get_auto(getF('382_IsegFc571_pulse50mV1Hz_15'), 39), label='382V, max')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")



def check_shapes_Jun30a():
    dir1 = '/data/TMS_data/raw/Jun30a_tek/'
    getF = lambda x: dir1+'HV_alphaOn_Focusing_'+x+'.isf'


    xs = [0.5*x for x in range(-200, 1200)]
    wg1 = WaveformGeter()

    plt.plot(xs, wg1.get_auto(dir1+'HV_alphaOn_total_Vd2000Vb_100.isf', 31), label='2000V')
#     plt.plot(wg1.get_auto(getF('Vd2000V_Vc2000V_130'), 13), label='2000V, 2000V')
#     plt.plot(wg1.get_auto(getF('Vd1500V_Vc1500V_189'), 9), label='1500V, 1500V')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc1500Vb_240'), 9), label='1500V, 1500bV')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc2000Vb_300'), 9), label='1500V, 2000bV')
    plt.plot(xs, wg1.get_auto(getF('Vd1500V_Vc2300Vb_311'), 3), label='1500V, 2300bV')
#     plt.plot(wg1.get_auto(getF('Vd1500V_Vc2300Vb_311'), 3, debug=True), label='2300 V')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def getFn(dir1,i, ith=0):
    fs = glob.glob(dir1+f'*_{i}.isf')
    print(dir1+f'*_{i}.isf')

    if fs:
        if len(fs)>0: print(fs)
        return fs[ith]
    return None

def check_shapes_Aug13a():
    dir1 = '/data/TMS_data/raw/Aug13a_tek/'
    ## /data/TMS_data/raw/Aug13a_tek/filtered_HV_alphaOn_C4_setelevenOafter_continue_DongwenFd1500_IsegFd1500_pulse80mV1Hz_672.isf
    getF = lambda x: dir1+'filtered_HV_alphaOn_C4_setelevenOafter_continue_DongwenFd1500_IsegFd1500_pulse80mV1Hz_'+x+'.isf'


    xs = [0.5*x for x in range(-200, 1200)]
    wg1 = WaveformGeter()

#     plt.plot(xs, wg1.get_auto(getF('100'), 92), label='100')
#     plt.plot(xs, wg1.get_auto(getF('600'), 92), label='600')
#     plt.plot(xs, wg1.get_auto(dir1+'filtered_HV_alphaOn_C4_setten0_IsegFd1500_pulse80mV1Hz_22.isf', 92), label='Drift 22')
#     plt.plot(xs, wg1.get_auto(dir1+'filtered_HV_alphaOn_C4_settenO_pulse80mV500Hz_19.isf', 92), label='Pulse')

#     plt.plot(xs, wg1.get_auto(getFn(dir1,30), 192), label='30')
#     plt.plot(xs, wg1.get_auto(getFn(dir1,600), 192), label='600')
    plt.plot(xs, wg1.get_auto(getFn(dir1,1000), 192), label='1000, focus1')
    plt.plot(xs, wg1.get_auto(getFn(dir1,1200), 192), label='1200, drift1')
# #     plt.plot(xs, wg1.get_auto(getFn(dir1,1701), 192), label='1701')
#     plt.plot(xs, wg1.get_auto(getFn(dir1,1870), 192), label='1870')
    plt.plot(xs, wg1.get_auto(getFn(dir1,2500), 192), label='2500, focus2a')
    plt.plot(xs, wg1.get_auto(getFn(dir1,3000), 192), label='3000, focus2b')
    plt.plot(xs, wg1.get_auto(getFn(dir1,4000), 100), label='4000, focus2c')
    plt.plot(xs, wg1.get_auto(getFn(dir1,4650), 100), label='4650, focus2c')
    plt.plot(xs, wg1.get_auto(getFn(dir1,5200), 200), label='5200, focus2cgasoff')
    plt.plot(xs, wg1.get_auto(getFn(dir1,5258), 200), label='5258, focus2cgasoff')
    plt.plot(xs, wg1.get_auto(getFn(dir1,5500), 200), label='5500, focus2cgasoff')
    plt.plot(xs, wg1.get_auto(getFn(dir1,5579), 200), label='5579, focus2cgasoff')



    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")


def check_shapes_Aug13b():
    dir1 = '/data/TMS_data/raw/Aug13a_tek/'

    xs = [0.5*x for x in range(-200, 1200)]
    wg1 = WaveformGeter()

    evtx  = 1
    for x in sys.argv[1:]:
        ax = x.split(':')
        filex = int(ax[0])
        if len(ax)>1: evtx = int(ax[1])
        plt.figure(1)
        plt.plot(xs, wg1.get_auto(getFn(dir1,filex), evtx), label=f'{filex}:{evtx}')
        plt.figure(2)
        plt.bar(wg1.histData[1][:-1],wg1.histData[0],width=1, alpha=0.6, label=f'{filex}')

    plt.figure(1)
    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.figure(2)
    plt.xlabel(r"Counts")
    plt.ylabel("Entries")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def check_shapes(dir2):
    dir0 = '/data/TMS_data/raw/'
    dir1 = f'{dir0}{dir2}/'

    xs = [0.5*x for x in range(-200, 1200)]
    wg1 = WaveformGeter()

    evtx  = 1
    for x in sys.argv[1:]:
        ax = x.split(':')
        filex = int(ax[0])

        if len(ax)>1 and ax[1]!='': evtx = int(ax[1])
        tag = ax[2]+'/' if len(ax)>2 else ''

        dirx = dir1
        if len(ax)>3:
            dirx = ax[3]
            if dirx[0]!='/': dirx = dir0+dirx
            if dirx[-1]!='/':dirx += '/'

        plt.figure(1)
        plt.plot(xs, wg1.get_auto(getFn(dirx,filex), evtx), label=f'{tag}{filex}:{evtx}')
        plt.figure(2)
        plt.bar(wg1.histData[1][:-1],wg1.histData[0],width=1, alpha=0.3, label=f'{tag}{filex}')

    plt.figure(1)
    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.figure(2)
    plt.xlabel(r"Counts")
    plt.ylabel("Entries")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")



def run():
#     showShapes()
#     check_shapes_500V()
#     check_shapes_Jun30a()
#     check_shapes_Jun30a_Fc1500V()
#     check_shapes_Jun30a_Fc1500V_samefile()
#     check_shapes_Aug10a_drift()
#     check_shapes_Aug10a()
#     if len(sys.argv)>1: check_shapes_Aug13b()
#     else: check_shapes_Aug13a()
#     check_shapes_Aug13a()
#     check_shapes_Aug13b()
#    check_shapes(dir2='Aug13a_tek')
#     check_shapes(dir2='Aug27a_tek')
#     check_shapes(dir2='Aug27b_tek')
#     check_shapes(dir2='Sep20a_tek')
     check_shapes(dir2='Sep29a_tek')
#      check_shapes(dir2='Sep03a_tek')

if __name__ == '__main__':
#     test()
    run()
