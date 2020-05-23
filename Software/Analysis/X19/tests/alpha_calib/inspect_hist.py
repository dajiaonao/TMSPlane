#!/usr/bin/env python3
import glob
import os
from ROOT import TH1F, TChain, gDirectory, TCanvas

class HistMaker:
    '''This class is used to make some basic histograms from a root file made by oscilloscope_signal_check.py.'''
    def __init__(self):
        self.promsCfg = 'proms2(128,0,128)'
        self.dtCfg = 'dt(200,0,20000)'
        self.widthCfg = 'width(200,0,400)'

    def make_hists(self, fname, tag='test_'):
        tree1 = TChain("tree")
        tree1.Add(fname)

        tree1.Draw(f"proms2>>{tag}{self.promsCfg}","","goff")
        h_pm = gDirectory.Get(f'{tag}proms2')

        tree1.Draw(f"dt>>{tag}{self.dtCfg}","","goff")
        h_dt = gDirectory.Get(f'{tag}dt')

        tree1.Draw(f"width>>{tag}{self.widthCfg}","","goff")
        h_wd = gDirectory.Get(f'{tag}width')

        return h_pm, h_dt, h_wd

def loopMonitor(rPattern, refRootFiles=[]):
    '''Keep showing the newest histogram in hdir, and the reference histograms if the reference root file is given'''

    dsList = []
    hm1 = HistMaker()
    ### get the reference histogram is given
    for i in range(len(refRootFiles)):
        dsList.append(hm1.make_hists(refRootFiles[i],f'ref{i}_'))

    ### get the fname of the latest
    files = glob.glob(rPattern)
    lastFile = files[0]
    for f in files:
        if os.path.getmtime(f) - os.path.getmtime(lastFile) > 0 and time.time() - os.path.getmtime(f) > 10: lastFile = f

    ### get this list
    hNew = hm1.make_hists(lastFile,f'test_')

    ### make the plots
    nHist = len(hNew)
    c1 = TCanvas('c1','c1',1000,400)
    c1.Divide(nHist)

    for i in range(nHist):
        c1.cd(i+1)
        hNew[i].Draw('PLC')
        for h in dsList: h[i].Draw('PLC same')

    c1.Update()
    a = input('jjj')


def test():
    hm1 = HistMaker()
    h1 = hm1.make_hists("TPCHV2kV_PHV0V_air3_126.root")

    c1 = TCanvas('c1','c1',1000,400)
    c1.Divide(3)
    c1.cd(1)
    h1[0].Draw()
    c1.cd(2)
    h1[1].Draw()

    c1.cd(3)
    h1[2].Draw()

    c1.Update()
    a = input('jjj')

if __name__ == '__main__':
#     test()
    loopMonitor('./TPC*.root', ["TPCHV2kV_PHV0V_air3_126.root"])

