#!/usr/bin/env python

from ROOT import *
from rootUtil import waitRootCmdX, get_default_fig_dir
import glob
from subprocess import call

sDir = get_default_fig_dir()
sTag = 'test_'
sDirectly = False
if gROOT.IsBatch(): sDirectly = True

class timeKeeper:
    def __init__(self):
        self.lt = TLatex()
        self.sTag = sTag
        self.sDir = sDir
        self.autoSave = sDirectly
        self.pSuffix = '.png'

    def getFigures(self,files, cList=[5]):
        nChannels = 19
        head = ':'.join(["F{0:d}F/F".format(x) for x in range(nChannels+1)])
        i = 0
        for f in files:
            t1 = TTree()
            t1.ReadFile(f, head)
            for iC in cList:
                t1.Draw("F{0:d}F:Entry$*0.2*0.001".format(iC))
                h1 = gPad.GetPrimitive('htemp')
                h1.GetYaxis().SetTitle("V_{out} [V]")
                h1.GetXaxis().SetTitle("t [ms]")
                h1.GetYaxis().SetRangeUser(0.8,1.3)
                self.lt.DrawLatexNDC(0.2,0.92, "Chip {1:d}, t = {0:d} s".format(i*10, iC))

                waitRootCmdX(self.sDir+self.sTag+"C"+str(iC)+"_"+str(i)+self.pSuffix, self.autoSave)
            i += 1

    def getGIF(self, pngs, outGIF):
        '''Convert the produced png files to gif to show the time evolution
        convert -loop 0 -delay 100 plot_P4_*.png out_P4.gif
        '''
        cmd = 'convert -loop 0 -delay 100 '+' '.join(pngs)+' '+outGIF
        call(cmd, shell=True)

    def test(self):
#         self.getFigures(['../TS/TSa_{0:d}adc.dat'.format(x) for x in range(150)])
        iC = 5
        figT = self.sTag+"C"+str(iC)
        self.getGIF([self.sDir+'png/'+figT+"_"+str(i)+'.png' for i in range(150)], figT+'.gif')
    def checkChannels(self, chs):
        self.getFigures(['../TS/TSa_{0:d}adc.dat'.format(x) for x in range(150)], chs)
        for iC in chs:
            figT = self.sTag+"C"+str(iC)
            self.getGIF([self.sDir+figT+"_"+str(i)+'.png' for i in range(150)], figT+'.gif')


def test():
    tk1 = timeKeeper()
    tk1.sDir = 'figs_time_check/'
    tk1.sTag = "tChekc_"
#     tk1.test()
    tk1.autoSave = True
    tk1.checkChannels([6,12,18,8])

if __name__ == "__main__":
    gStyle.SetOptTitle(0)
    test()
