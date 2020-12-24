#!/usr/bin/env python3
'''This module is used to check the test pulse results created with the `process_pulse` function in process_signal.py script.
'''
from ROOT import TChain, gPad, TLatex, TGraph
from rootUtil3 import waitRootCmdX

class PulseChecker:
    def __init__(self, flist=[]):
        self.ch1 = TChain('tup1')
        self.pulse_V = 0.2 # Volt
        self.lt = TLatex()
        self.sDir = 'temp1/'
        self.sTag = 'pulse_'

        if isinstance(flist,list):
            for f in flist: self.ch1.Add(f)
        else: self.ch1.Add(flist)

    def check_channel(self, chan):
        '''Check channel 'chan' and return the statistics'''
        self.ch1.Draw("A",f'ch=={chan}')
        h1 = gPad.GetPrimitive("htemp")
        h1.Fit('gaus')
        h1.SetXTitle("U_{Out} [V]")
        h1.SetYTitle("Entries")

        fun1 = h1.GetFunction('gaus')
        mean = fun1.GetParameter(1)
        sigma = fun1.GetParameter(2)
        enc = 7410*self.pulse_V * sigma / mean

        print(f'{mean} {sigma} {enc}')

        self.lt.DrawLatexNDC(0.2, 0.85, f'Channel {chan}')

        gPad.Modified()
        waitRootCmdX(self.sDir+self.sTag+f'ch{chan}')

        return mean, sigma, enc

    def check_all(self, chans):
        gr = TGraph()
        for chan in chans:
            m,s,enc = self.check_channel(chan)
            ip = gr.GetN()
            gr.SetPoint(ip, chan, enc)

        gr.SetMarkerColor(4)
        gr.Draw('AP')
        hgr = gr.GetHistogram()
        hgr.SetXTitle('Channel')
        hgr.SetYTitle('ENC [e^{-}]')
        waitRootCmdX(self.sDir+self.sTag+"enc")


def test():
#     pc1 = PulseChecker('/data/TMS_data/Processed/Dec21_TMS/pulse_C8_Dec21_C8_alpha_pulse_test_Dec211913_data_*.root')
    pc1 = PulseChecker('/data/TMS_data/Processed/Dec24_TMS/pulse_C8_*_data_*.root')

    print(pc1.ch1.GetEntries())
#     pc1.check_channel(0)
    chans = [i for i in range(19) if i not in [3,7,8,18]]
    pc1.check_all(chans)

if __name__ == '__main__':
    test()

