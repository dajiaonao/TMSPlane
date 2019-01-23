#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
from array import array

from ROOT import *
gROOT.LoadMacro("sp.C+")

from ROOT import SignalProcessor


def main():
    inRoot = sys.argv[1]      if len(sys.argv)>1 else "test.root"
    ich    = int(sys.argv[2]) if len(sys.argv)>2 else 0
    sp1 = SignalProcessor()
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20
    sp1.fltParam.clear()
    for x in [500, 150, 200, -1.]: sp1.fltParam.push_back(x)

    freq = 1000
    n1 = int(1/(0.2*freq*0.000001))
    sp1.sRanges.clear()
    ip = 0
    dn = 2500%n1 ## 2500 is the expected position of the signal
    while ip+dn < sp1.nSamples:
        sp1.sRanges.push_back((ip, min(ip+n1, sp1.nSamples)))
        ip += n1

    data1 = array('f',[0]*(sp1.nSamples*sp1.nAdcCh))

    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    ### range
    eRange = None
    if len(sys.argv)>3:
        lx = []
        r = sys.argv[3].split(',')
        for ri in r:
            si = ri.find('-')
            if si == -1:
                lx.append(int(ri))
            else:
                end = tree1.GetEntries() if si==len(ri)-1 else int(ri[si+1:])
                lx += range(int(ri[:si]), end)
        eRange = lx
    else: eRange = range(tree1.GetEntries())

    ### plotting
    plt.ion()
    plt.show()

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('time (s)')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('exp', color='b')
    ax1.tick_params('y', colors='b')
    ax2 = ax1.twinx()
    ax2.set_ylabel('sin', color='r')
    ax2.tick_params('y', colors='r')

#     for i in range(10):
    for i in eRange:
        print i
        tree1.GetEntry(i)
        sp1.measure_pulse(data1,ich)

        ax1.clear()
        ax1.plot(data1[sp1.nSamples*ich:sp1.nSamples*(ich+1)])
        ax2.clear()
        ax2.plot([sp1.scrAry[i] for i in range(sp1.nSamples)], 'r.')
        fig.tight_layout()
        plt.draw()
        plt.pause(0.001)
        x = raw_input("Press [enter] to continue.")
        if x=='q': break

if __name__ == '__main__':
    main()
