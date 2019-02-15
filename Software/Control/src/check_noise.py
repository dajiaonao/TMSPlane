#!/usr/bin/env python
from ROOT import *
import numpy as np
from math import sqrt, exp
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from ctypes import *
from array import array


gROOT.LoadMacro("dPhi.C+")
from ROOT import dPhi

class var:
    def __init__(self, N=16384):
        self.sumx = 0
        self.sumx2 = 0
        self.nx = 0
        self.norm = 1. if N is None else 1./sqrt(N)
    def add(self,x, n=1):
        self.sumx += x*n
        self.sumx2 += x*x*n
        self.nx += n
    def value(self):
        m = self.sumx/self.nx
        ### see https://docs.scipy.org/doc/numpy-1.15.0/reference/routines.fft.html about the 1/sqrt(n_sample) normalization
        return self.norm*m, self.norm*sqrt(self.sumx2/self.nx - m*m)

def test8():
    '''Check the effect of the low pass filter'''
    plotFun = plt.loglog
#     plotFun = plt.semilogy
    plotT = False

    ### first get a waveform
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Feb09b_data_190.root')

    ievt = 20
    n = ch1.Draw('adc[19]','Entry$=={0:d}'.format(ievt),'goff')
    v1 = ch1.GetV1()
    var0 = [v1[i] for i in range(n)]
    nx = 1./sqrt(n)

    ### seccond, do a fft transform
    sp = np.fft.rfft(var0, n)
    fv = [np.abs(a)*nx for a in sp]

    fx = np.arange(len(fv))
    fx[0] = 0.01
    print fx[:10]
    if not plotT: plotFun(fx, fv, label='Orignal')


    ### third, check the filtered
    from ROOT import gROOT
    gROOT.LoadMacro("sp.C+")
    from ROOT import Filter_ibl, Filter_ibb


    v1f = array('f',var0)
#     fl1 = Filter_ibl(n)
    fl1 = Filter_ibb(n)

#     fl1.setup(-4,3.535e-3, 3.665e-3)
#     fl1.setup(-4,3.601e-3, 3.602e-3)
    fl1.setup(-4, 3.6005e-3, 3.6025e-3)
#     fl1.setup(2,3e-3)
    fl1.apply(v1f)
    vf1 = np.array([fl1.outWav[i] for i in range(n)])

    sp1 = np.fft.rfft(vf1, n)
    fv1 = [np.abs(a)*nx for a in sp1]
    if not plotT: plotFun(fx, fv1, label='Filtered')

#     fl1.setup(2,3e-2)
    F1 = 0.00360107421875
    sk = 0.0015
#     fl1.setup(-4,F1*(1.-sk),F1*(1.+sk))
    fl1.setup(-4, 3.6005e-3, 3.6025e-3)
#     fl1.setup(-4, 3.599e-3, 3.605e-3)
#     fl1.setup(-4,2e-3, 9e-3)
    fl1.apply(v1f)
    vf2 = np.array([fl1.outWav[i] for i in range(n)])

    sp2 = np.fft.rfft(vf2, n)
    fv2 = [np.abs(a)*nx for a in sp2]
    if not plotT: plotFun(fx, fv2, label='Filtered2')

    if plotT:
        plt.plot(var0, label='Orignal')
#         plt.plot(vf1, label='Filtered1')
#         plt.plot(vf2, label='Filtered2')


    if plotT:
        for i in range(50,70): sp[i] = sp[50]
        vf3 = np.fft.irfft(sp)
        plt.plot(vf3, label='rc')


    ### show the plots
    plt.xlabel('Frequency [kHz]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()


def test7():
    '''Compare signal and background, 1 channel, average of multiple samples, based on test2()'''
    plotFun = plt.loglog

    ### first check the exponential

    n = 16384
    var0 = [0.7]*n
    for i in range(101,n):
        var0[i] = 0.7+0.05*exp(-i/2500.)

    nx = 1./sqrt(n)
    sp = np.fft.rfft(var0, n)
#     fv = [np.abs(a)*nx for a in sp]
    fv = [np.angle(a) for a in sp]
#     plotFun(np.arange(len(fv)), fv, 'go', label='Ideal signal')
#     plt.plot(np.arange(len(var0)), var0, 'go')
    plt.plot(np.arange(len(fv)), fv, 'go')

#     plt.show()
#     return


    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Feb09b_data_190.root')

    fs = None
    for ievt in range(ch1.GetEntries()):
        n = ch1.Draw('adc[19]','Entry$=={0:d}'.format(ievt),'goff')
        v1 = ch1.GetV1()
        var1 = [v1[i] for i in range(n)]

        sp = np.fft.rfft(var1, n)
        if fs is None:
            fs = [var() for i in range(sp.size)]
        for i in range(sp.size):
            fs[i].add(np.abs(sp[i]))

    fv = [a.value()[0] for a in fs]
    plotFun(np.arange(len(fs)), fv, 'bo', label='Noise')


    ch2 = TChain('tree1')
    ch2.Add('data/fpgaLin/Feb09b_data_8.root')

    fs2 = None
    for ievt in range(ch2.GetEntries()):
        n = ch2.Draw('adc[19]','Entry$=={0:d}'.format(ievt),'goff')
        v2 = ch2.GetV1()
        var2 = [v2[i] for i in range(n)]

        sp = np.fft.rfft(var2, n)
        if fs2 is None:
            fs2 = [var() for i in range(sp.size)]
        for i in range(sp.size):
            fs2[i].add(np.abs(sp[i]))

    fv2 = [a.value()[0] for a in fs2]
    plotFun(np.arange(len(fs2)), fv2, 'ro', label='Obs signal')

    plt.xlabel('Frequency [kHz]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()


def test6():
    '''Check the low and high frequency'''
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')

    fs1 = None
    n1 = 16384
    fMax = 2500. ### 2500 kHz, the maximum frequency is sampling_rate/2

    ich = 12
    for ievt in range(ch1.GetEntries()):
        n = ch1.Draw('adc[{0:d}]'.format(ich),'Entry$=={0:d}'.format(ievt),'goff')
        v1 = ch1.GetV1()
        var1 = [v1[i] for i in range(n1)]

        sp1 = np.fft.rfft(var1, n1)
        if fs1 is None: fs1 = [var(N=n1) for i in range(sp1.size)]
        for i in range(sp1.size): fs1[i].add(np.abs(sp1[i]))

    fv1 = [a.value()[0] for a in fs1]
    plotFun = plt.semilogy
#     plotFun = plt.loglog
    color=iter(cm.rainbow(np.linspace(0,1,5)))
    for ip in range(5):
        p = ip+1
        pMax = fMax/p
        v = pow(10, ip)
        plotFun(np.arange(0, pMax, pMax/len(fv1)), [a*v for a in fv1], c=next(color), label='F/{0:d}'.format(p))

    plt.xlabel('Frequency [kHz]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.annotate("Ch {0:d}".format(ich), xy=(0.1, 0.95), xycoords='axes fraction')

    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()

def test5():
    '''Check one channel, for mutiple samples, compare the effect of different sample size'''
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')

    color=iter(cm.rainbow(np.linspace(0,1,3)))

    fs1 = None
    fs2 = None
    fs3 = None

    n1 = 16384
    n2 = 16381
    n3 = 10000
    fMax = 2500. ### 2500 kHz, the maximum frequency is sampling_rate/2

    for ievt in range(ch1.GetEntries()):
        n = ch1.Draw('adc[12]','Entry$=={0:d}'.format(ievt),'goff')
        v1 = ch1.GetV1()
        var1 = [v1[i] for i in range(n1)]

        sp1 = np.fft.rfft(var1, n1)
        if fs1 is None: fs1 = [var(N=n1) for i in range(sp1.size)]
        for i in range(sp1.size): fs1[i].add(np.abs(sp1[i]))

        sp2 = np.fft.rfft(var1, n2)
        if fs2 is None: fs2 = [var(N=n2) for i in range(sp2.size)]
        for i in range(sp2.size): fs2[i].add(np.abs(sp2[i]))

        sp3 = np.fft.rfft(var1, n3)
        if fs3 is None: fs3 = [var(N=n3) for i in range(sp3.size)]
        for i in range(sp3.size): fs3[i].add(np.abs(sp3[i]))

    fv1 = [a.value()[0] for a in fs1]
    fv2 = [a.value()[0] for a in fs2]
    fv3 = [a.value()[0] for a in fs3]
    plt.semilogy(np.arange(0, fMax, fMax/len(fv1)), fv1, c=next(color), label='N={0:d}'.format(n1))
    plt.semilogy(np.arange(0, fMax, fMax/len(fv2)), fv2, c=next(color), label='N={0:d}'.format(n2))
    plt.semilogy(np.arange(0, fMax, fMax/len(fv3)), fv3, c=next(color), label='N={0:d}'.format(n3))
#     plt.loglog(np.arange(0, fMax, fMax/len(fv1)), fv1, c=next(color), label='N={0:d}'.format(n1))
#     plt.loglog(np.arange(0, fMax, fMax/len(fv2)), fv2, c=next(color), label='N={0:d}'.format(n2))
#     plt.loglog(np.arange(0, fMax, fMax/len(fv3)), fv3, c=next(color), label='N={0:d}'.format(n3))

    plt.xlabel('Frequency [kHz]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()

def test4():
    '''Save the frequency spectra to a root file for detailed analysis'''
    nAdcCh = 20
    nSamples = 16384 
    data1 = array('f',[0]*(nSamples*nAdcCh))

    inRoot = 'data/fpgaLin/Feb01a_noise_dc.root'
    fin1 = TFile(inRoot,'read')
    tree1 = fin1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    cRange = range(nAdcCh)
#     cRange = [2,3]
    nCh = len(cRange)
    nx = 8193 # 16384/2+1, 

    outRootName = 'data/fpgaLin/Feb01a_noise_FerqSpectra.root'
    data2 = array('f',[0]*(nx*nAdcCh)) 
    T = array('i',[0])
    fout1 = TFile(outRootName,'recreate')
    tree2 = TTree('tree2',"data: {0:d} channel, {1:d} samples".format(nCh, nx))
    tree2.Branch('T',T,'T/i')
    tree2.Branch('freq',data2, "freq[{0:d}][{1:d}]/F".format(nCh, nx))

    nEvt = tree1.GetEntries()
    INTV = 1000 if nEvt>10000 else max(nEvt/10, 1)
    for ievt in range(nEvt):
        if ievt%INTV==0: print ievt, ' events processed'
        tree1.GetEntry(ievt)

        for ich in cRange:
            var1 = data1[nSamples*ich:nSamples*(ich+1)]
            sp = np.fft.rfft(var1, nSamples)

            for i in range(nx): data2[ich*nx+i] = np.abs(sp[i])

        tree2.Fill()

    tree2.Write()
    fout1.Close()

def test3b():
    '''Process mutiple channels and show them on a (scaled) plot'''
    nAdcCh = 20
    nSamples = 16384 
    data1 = array('f',[0]*(nSamples*nAdcCh))
    fMax = 2500. ### 2500 kHz, the maximum frequency is sampling_rate/2

    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')
#     ch1.Add('data/fpgaLin/Feb01a_noise_dc.root')
    ch1.SetBranchAddress('adc',data1)

    cRange = range(nAdcCh)
#     cRange = [2,13]
    fs = [None]*nAdcCh
    color=iter(cm.rainbow(np.linspace(0,1,len(cRange))))

#     plotFun = plt.semilogy
    plotFun = plt.loglog

    nEvt = ch1.GetEntries()
#     nEvt = 30
    INTV = 1000 if nEvt>10000 else max(nEvt/10, 1)
    for ievt in range(nEvt):
        if ievt%INTV==0: print ievt, ' events processed'
        ch1.GetEntry(ievt)

        for ich in cRange:
            var1 = data1[nSamples*ich:nSamples*(ich+1)]
            sp = np.fft.rfft(var1, nSamples)

            if fs[ich] is None:
                fs[ich] = [var() for i in range(sp.size)]
            for i in range(sp.size):
                fs[ich][i].add(np.abs(sp[i]))

    for ich in cRange:
        fv = [a.value()[0]*pow(10,ich) for a in fs[ich]]
#         fe = [a.value()[1]/a.value()[0] for a in fs[ich]]
        plotFun(np.arange(0, fMax, fMax/len(fv)), fv, label=r'Ch {0:d} ($\times 10^{{{0:d}}}$)'.format(ich), c=next(color))
#         plt.semilogy(np.arange(len(fs)), fe, label='{0:d} error'.format(ich), c=next(color))

    plt.xlabel('Frequency [kHz]')
    plt.ylabel('Amplitude')
    plt.grid(True)

    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()

def test3():
    '''Process mutiple channels and show them on a (scaled) plot'''
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')
#     ch1.Add('data/fpgaLin/Feb01a_noise_dc.root')

#     for ich in [2,3,4,5,12,17]:
    n = 2*2
    color=iter(cm.rainbow(np.linspace(0,1,n)))
#     for ich in range(20):
    for ich in [2,3]:
        fs = None
        for ievt in range(ch1.GetEntries()):
            n = ch1.Draw('adc[{0:d}]'.format(ich),'Entry$=={0:d}'.format(ievt),'goff')
            v1 = ch1.GetV1()
            var1 = [v1[i] for i in range(n)]

            sp = np.fft.rfft(var1, n)
            if fs is None:
                fs = [var() for i in range(sp.size)]
            for i in range(sp.size):
                fs[i].add(np.abs(sp[i]))

        fv = [a.value()[0]*pow(10,ich) for a in fs]
        fe = [a.value()[1]/a.value()[0] for a in fs]
        plt.semilogy(np.arange(len(fs)), fv, label='{0:d}'.format(ich), c=next(color))
        plt.semilogy(np.arange(len(fs)), fe, label='{0:d} error'.format(ich), c=next(color))
        print ich, 'done'

    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()


def test2():
    '''Check one channel, for mutiple samples'''
    ch1 = TChain('tree1')
#     ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')
    ch1.Add('data/fpgaLin/Feb09b_data_190.root')

    fs = None
    for ievt in range(ch1.GetEntries()):
        n = ch1.Draw('adc[19]','Entry$=={0:d}'.format(ievt),'goff')
        v1 = ch1.GetV1()
        var1 = [v1[i] for i in range(n)]

        sp = np.fft.rfft(var1, n)
        if fs is None:
            fs = [var() for i in range(sp.size)]
        for i in range(sp.size):
            fs[i].add(np.abs(sp[i]))

    fv = [a.value()[0] for a in fs]
    fe = [a.value()[1] for a in fs]
#     plt.loglog(np.arange(len(fs)), fv, 'bo')
#     plotFun = plt.semilogx
    plotFun = plt.loglog
    plotFun(np.arange(len(fs)), fv, 'bo')
    plt.show()

def test2b():
    '''Check one channel, for mutiple samples'''
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')

    ch2 = TChain('tree1')
#     ch2.Add('data/fpgaLin/Jan25a_C2_225mV_f1000.root')
    ch2.Add('data/fpgaLin/Feb09b_data_0.root')

    color=iter(cm.rainbow(np.linspace(0,1,10)))
    fs = None
    fp = None
    iref = 0
    ich = 2
    for ievt in range(ch1.GetEntries()):
        n = ch1.Draw('adc[{0:d}]'.format(ich),'Entry$=={0:d}'.format(ievt),'goff')
        v1 = ch1.GetV1()
        var1 = [v1[i] for i in range(n)]

        sp = np.fft.rfft(var1, n)
        aRef = np.angle(sp[iref])
        if fs is None:
            fs = [var() for i in range(sp.size)]
            fp = [var() for i in range(sp.size)]
        for i in range(sp.size):
            fs[i].add(np.abs(sp[i]))
            fp[i].add(dPhi(np.angle(sp[i]), aRef))

    ievt = 10
    n = ch2.Draw('adc[{0:d}]'.format(ich),'Entry$=={0:d}'.format(ievt),'goff')
    v1 = ch2.GetV1()
    var1 = [v1[i] for i in range(n)]

    sp = np.fft.rfft(var1, n)

    fv = [a.value()[0] for a in fs]
    fe = [a.value()[1] for a in fs]
    fv2 = [np.abs(a)/sqrt(n) for a in sp]
    fe2 = [(fv2[i]-fv[i])/fe[i] for i in range(len(fv2))]
    fp2 = [(fv2[i]-fv[i])/fe[i] for i in range(len(fv2))]
#     plt.loglog(np.arange(len(fs)), fv, 'bo')
#     plotFun = plt.semilogy
#     plotFun = plt.loglog
    plotFun = plt.semilogx
#     plotFun(np.arange(len(fs)), fv2, label='Signal', c=next(color))
    plotFun(np.arange(len(fs)), fe2, label='Derivation', c=next(color))
#     plotFun(np.arange(len(fs)), fv, label='Noise', c=next(color))


    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()


def test1():
    '''Check one channel, using one sample'''
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Feb09b_data_189.root')
#     ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')
#     ch1.Add('data/fpgaLin/Jan25a_C2_225mV_f1000.root')

    n = ch1.Draw('adc[19]','Entry$==995','goff')
    v1 = ch1.GetV1()
    var1 = [v1[i] for i in range(n)]

    print n
    print var1[:10]
    print var1[-10:]
    sp = np.fft.rfft(var1, n)
#     freq = np.fft.fftfreq(int(n))
    print sp.size
    freq = np.arange(sp.size)

#     plt.plot(freq, sp.real, freq, sp.imag)
#     plt.plot(freq, sp.real)
#     plt.loglog(freq, sp.real, 'bo')
    plt.loglog(freq, np.abs(sp), 'bo')
#     plt.plot(freq, sp.imag)
    plt.show()

if __name__ == '__main__':
#     test3b()
    test2b()
#     test1()
#     test2()
#     test7()
#     test8()
#     test6()
