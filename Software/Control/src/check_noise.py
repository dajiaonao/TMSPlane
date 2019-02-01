#!/usr/bin/env python
from ROOT import *
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

class var:
    def __init__(self):
        self.sumx = 0
        self.sumx2 = 0
        self.nx = 0
    def add(self,x, n=1):
        self.sumx += x*n
        self.sumx2 += x*x*n
        self.nx += n
    def value(self):
        m = self.sumx/self.nx
        return m, sqrt(self.sumx2/self.nx - m*m)

def test3():
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')

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
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')

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
    plt.semilogy(np.arange(len(fs)), fv, 'bo')
    plt.show()


def test1():
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Jan31a_noise_dc.root')

    n = ch1.Draw('adc[12]','Entry$==50','goff')
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
    test3()
