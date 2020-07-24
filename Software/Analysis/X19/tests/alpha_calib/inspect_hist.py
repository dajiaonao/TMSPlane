#!/usr/bin/env python3
import glob
import os
import time
from ROOT import TH1F, TChain, gDirectory, TCanvas, TLegend

class HistMaker:
    '''This class is used to make some basic histograms from a root file made by oscilloscope_signal_check.py.'''
    def __init__(self):
#         self.promsCfg = 'proms2(128,0,128)'
        self.promsVar = 'proms3'
        self.promsCfg = 'proms3(256,0,256)'
        self.dtCfg = 'dt(200,0,20000)'
        self.widthCfg = 'width(200,0,400)'

    def make_hists(self, fname, tag='test_'):
        tree1 = TChain("tree")
        tree1.Add(fname)

        tree1.Draw(f"{self.promsVar}>>{tag}{self.promsCfg}","","goff")
        h_pm = gDirectory.Get(f'{tag}proms3')

        tree1.Draw(f"dt>>{tag}{self.dtCfg}","","goff")
        h_dt = gDirectory.Get(f'{tag}dt')

        tree1.Draw(f"width>>{tag}{self.widthCfg}","","goff")
        h_wd = gDirectory.Get(f'{tag}width')

        return h_pm, h_dt, h_wd

def loopMonitor(rPattern, refRootFiles=[], promsVarX=None):
    '''Keep showing the newest histogram in hdir, and the reference histograms if the reference root file is given'''

    dsList = []
    hm1 = HistMaker()
    if promsVarX is not None:
        hm1.promsVar = promsVarX[0]
        hm1.promsCfg = promsVarX[1]
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
#     loopMonitor('/data/TMS_data/Processed/Jun30a_p1/*.root', ['/data/TMS_data/Processed/Jun25a_p1/*_280.root', '/data/TMS_data/Processed/Jun25a_p1/*_295.root'])
#     loopMonitor('/data/TMS_data/Processed/Jun30a_p1/*.root', ['/data/TMS_data/Processed/Jun30a_p1/*_297.root','/data/TMS_data/Processed/Jun25a_p1/*_280.root'])
#     loopMonitor('/data/TMS_data/Processed/Jul16a_p1/*.root', ['/data/TMS_data/Processed/Jul16a_p1/HV_*_212.root','/data/TMS_data/Processed/Jul16a_p1/HV_alphaOn_*_254.root','/data/TMS_data/Processed/Jul16a_p1/HV_alphaOn_Fd1500V_211.root'])
#     loopMonitor('/data/TMS_data/Processed/Jul22a_p1/*.root', ['/data/TMS_data/Processed/Jul16d_p1/*_11.root','/data/TMS_data/Processed/Jul16d_p2/goodOnes/*_75.root'], promsVarX=('proms3*0.2','proms3(250,0,50)'))
#     loopMonitor('/data/TMS_data/Processed/Jul22a_p1/*.root', ['/data/TMS_data/Processed/Jul22a_p1/*_40.root', '/data/TMS_data/Processed/Jul22a_p1/*_35.root', '/data/TMS_data/Processed/Jul22a_p1/*_53.root', '/data/TMS_data/Processed/Jul22a_p1/*_102.root'], promsVarX=('proms3*0.2','proms3(250,0,50)'))
    loopMonitor('/data/TMS_data/Processed/Jul24a_p1/*.root', ['/data/TMS_data/Processed/Jul23a_p1/*_0.root','/data/TMS_data/Processed/Jul22a_p1/*_40.root', '/data/TMS_data/Processed/Jul22a_p1/*_78.root'], promsVarX=('proms3*0.2','proms3(150,0,30)'))
#     loopMonitor('/data/TMS_data/Processed/Jul16a_p1/*.root', ['/data/TMS_data/Processed/Jul16a_p1/HV_*_212.root','/data/TMS_data/Processed/Jul16a_p1/HV_alphaOn_Fd1500V_211.root'])
#     loopMonitor('/data/TMS_data/Processed/Jul16c_p1/*.root', ['/data/TMS_data/Processed/Jul16c_p1/HV_*_0.root','/data/TMS_data/Processed/Jul16c_p1/*_31.root'], promsVarX=('proms3*2','proms3(50,0,100)'))
#     loopMonitor('/data/TMS_data/Processed/Jul16a_p1/*.root', ['/data/TMS_data/Processed/Jul12a_p1/filtered_10mVpp_2us_1000Hz_0.root','/data/TMS_data/Processed/Jul12a_p1/filtered_20mVpp_150us_200Hz_*.root'])

