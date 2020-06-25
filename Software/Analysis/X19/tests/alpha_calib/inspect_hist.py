#!/usr/bin/env python3
import glob
import os
import time
from ROOT import TH1F, TChain, gDirectory, TCanvas, TLegend

class HistMaker:
    '''This class is used to make some basic histograms from a root file made by oscilloscope_signal_check.py.'''
    def __init__(self):
#         self.promsCfg = 'proms2(128,0,128)'
        self.promsCfg = 'proms2(256,0,256)'
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

    c1 = None
    while True:
        try:
            ### get the fname of the latest
            files = glob.glob(rPattern)
            lastFile = files[0]
            for f in files:
                if os.path.getmtime(f) - os.path.getmtime(lastFile) > 0 and time.time() - os.path.getmtime(f) > 10: lastFile = f

            ### get this list
            hNew = hm1.make_hists(lastFile,f'test_')

            lg = TLegend(0.6,0.7,0.8,0.9)
            lg.SetBorderSize(0)
            lg.SetFillStyle(0)

            ### create canvas if it's not there yet
            if c1 is None:
                nHist = len(hNew)
                c1 = TCanvas('c1','c1',1000,400)
                c1.Divide(nHist)

            ### show the plots
            for i in range(nHist):
                c1.cd(i+1)
                hNew[i].Draw('PLC')
                for h in dsList: h[i].Draw('PLC same')
                hNew[i].Draw('same')

                if i==1:
                    lg.AddEntry(hNew[i],"new",'l')
                    for h in dsList:
                        lg.AddEntry(h[i], 'Ref'+h[i].GetName(), 'l')
                    lg.Draw()

            c1.Update()

            time.sleep(10)
    #         a = input('jjj')
        except KeyboardInterrupt:
            break


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
#     loopMonitor('h_May26a/*.root', ["TPCHV2kV_PHV0V_air3_126.root"])
#     loopMonitor('/data/TMS_data/Processed/Jun25a_p1/*.root', ['h_May31a_r1/*_180.root', '/data/TMS_data/Processed/Jun25a_p1/*_295.root'])
    loopMonitor('/data/TMS_data/Processed/Jun25a_p1/*.root', ['/data/TMS_data/Processed/Jun25a_p1/*_280.root', '/data/TMS_data/Processed/Jun25a_p1/*_295.root'])

