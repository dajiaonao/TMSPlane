#!/usr/bin/env python
import numpy as np
from math import sqrt

def test():
    print("testing")

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

def get_spectrum(ch1):
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
    return fs

if __name__ == '__main__':
    test()
