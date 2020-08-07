#!/usr/bin/env python3
from scipy.signal import find_peaks, peak_prominences
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
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

def getinput_auto(filename, ith=1, ishift1=-200, ishift2=1200, debug=False):
#     i0 = int(i0)
#     iFrom = i0+ishift1
#     iEnd = i0 + ishift2

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
    W = 300 
    peaks, properties = find_peaks(arwav2, height=None, width=(20,300), wlen=W, prominence=2, distance=160) 
    promsall = peak_prominences(arwav2, peaks, wlen=W)
    promxmins = promsall[1]

    pks = arwav2[peaks]
    proms3 = pks - arwav2[promxmins]

#     plt.plot(peaks, proms3, "o")
    if debug:
        plt.hist(proms3[proms3>20], bins=range(0,256))
        plt.show()
#     ret = plt.hist(proms3[proms3>20], bins=range(0,256))
    ret = np.histogram(proms3[proms3>20], bins=range(0,256))
#     print(ret)

    arr = ret[0]
    amax = np.max(arr)
    conditon = (arr == amax)
    result = np.where(conditon)
#     print("Arrays for the max element:",result)
#     print("List for the maximum value indexes:",result[0])
# 
#     ipeaks = np.asarray(range(0, len(proms3)))
#     pksA = ipeaks[proms3==result[0]]
#     print(proms3[pksA])
#     plt.show()

#     xx = result[0]
    xx = 63
    ### find the one gives max
    cpeaks = peaks[proms3==xx]
    print(f"Find {amax} events with A={xx}")
    i0 = cpeaks[ith]

    x0 = wav1[i0+ishift1]
    thr = 0.1*xx
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

    plt.plot(xs, getinput_auto(getF("100_pulse80mV1Hz_61"), 2), label='100 V')
    plt.plot(xs, getinput_auto(getF("200_pulse80mV1Hz_58"), 3), label='200 V')
    plt.plot(xs, getinput_auto(getF("300_pulse80mV1Hz_53"), 5), label='300 V')
    plt.plot(xs, getinput_auto(getF("400_pulse80mV1Hz_55"), 7), label='400 V')
    plt.plot(xs, getinput_auto(getF("500_pulse80mV1Hz_42"), 11), label='500 V')
    plt.plot(xs, getinput_auto(getF("700_pulse80mV1Hz_49"), 13), label='700 V')
    plt.plot(xs, getinput_auto(getF("1000_pulse80mV1Hz_46"), 17), label='1000 V')


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
    xs = [0.5*x for x in range(-200, 1200)]

    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc1500Vb_240'), 19), label='1500V, 240')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc1500Vb_250'), 19), label='1500V, 250')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc1500Vb_260'), 13), label='1500V, 260')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc1500Vb_271'), 13), label='1500V, 271')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc1500Vb_280'), 13), label='1500V, 280')

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

    plt.plot(xs, getinput_auto(dir1+'HV_alphaOn_total_Vd2000Vb_100.isf', 31), label='2000V')
#     plt.plot(getinput_auto(getF('Vd2000V_Vc2000V_130'), 13), label='2000V, 2000V')
#     plt.plot(getinput_auto(getF('Vd1500V_Vc1500V_189'), 9), label='1500V, 1500V')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc1500Vb_240'), 9), label='1500V, 1500bV')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc2000Vb_300'), 9), label='1500V, 2000bV')
    plt.plot(xs, getinput_auto(getF('Vd1500V_Vc2300Vb_311'), 3), label='1500V, 2300bV')
#     plt.plot(getinput_auto(getF('Vd1500V_Vc2300Vb_311'), 3, debug=True), label='2300 V')

    plt.xlabel(r"t [$\mu$s]")
    plt.ylabel("U [mV]")
    plt.legend(loc='best')
    plt.tight_layout()

    plt.ion()
    plt.show()

    a = input("Press any key to exit")

def run():
#     showShapes()
#     check_shapes_500V()
#     check_shapes_Jun30a()
    check_shapes_Jun30a_Fc1500V()

if __name__ == '__main__':
#     test()
    run()
