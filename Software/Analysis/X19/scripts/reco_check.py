#!/usr/bin/env python3
'''This module use the configuration from the reco_config.py and show the results'''
import sys
import numpy as np
from ROOT import gROOT, TChain
gROOT.LoadMacro("sp.C+")
from ROOT import SignalProcessor
import array
from reco_config import apply_config
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import artist
from matplotlib.ticker import FormatStrFormatter
import tkinter as tk
# from ctypes import *

class DataPanelGUILite(object):
    # @param [in] dataFigSize (w, h) in inches for the data plots figure assuming dpi=72
    def __init__(self, dataFigSize=(13, 12.5), visibleChannels=None, guiI=True):
        self.nAdcCh = 20
        self.adcDt =  0.2
        self.nSamples = 16384
        self.adcData = array.array('f',[0]*(self.nSamples*self.nAdcCh))
        self.sp = None
        self.yx = {}

        # frame for plotting
        self.dataInfo = None
        self.dataInfoText = None
        self.dataPlotsFrame = tk.Frame()
        self.dataPlotsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.dataPlotsFigure = Figure(figsize=dataFigSize, dpi=72)
        self.dataPlotsFigure.subplots_adjust(left=0.1, right=0.9, top=0.98, bottom=0.05, hspace=0, wspace=0)
        if visibleChannels == None or len(visibleChannels) == 0:
            visibleChannels = [i for i in range(self.nAdcCh-1)]
        # x-axis is shared
        dataPlotsSubplotN = self.dataPlotsFigure.add_subplot(
            len(visibleChannels)+1, 1, len(visibleChannels)+1, xlabel='t [us]', ylabel='[V]')
        self.dataPlotsSubplots = {}
        for i in range(len(visibleChannels)):
            self.dataPlotsSubplots[visibleChannels[i]] = self.dataPlotsFigure.add_subplot(
                len(visibleChannels)+1, 1, i+1, sharex=dataPlotsSubplotN)
        for i,a in list(self.dataPlotsSubplots.items()):
            artist.setp(a.get_xticklabels(), visible=False)
            self.yx[i] = a.twinx()
        self.dataPlotsSubplots[self.nAdcCh-1] = dataPlotsSubplotN
        self.yx[self.nAdcCh-1] = dataPlotsSubplotN.twinx()

        self.dataPlotsCanvas = FigureCanvasTkAgg(self.dataPlotsFigure, master=self.dataPlotsFrame)
        self.dataPlotsCanvas.draw()
        self.dataPlotsCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.dataPlotsToolbar = NavigationToolbar2Tk(self.dataPlotsCanvas, self.dataPlotsFrame)
        self.dataPlotsToolbar.update()
        self.dataPlotsCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        if self.adcData is not None: self.plot_data()

    def on_key_event(self, event):
        print(('You pressed {:s}'.format(event.key)))
        print((event.key, event.key=='r'))
        key_press_handler(event, self.dataPlotsCanvas, self.dataPlotsToolbar)

    def plot_data(self):
        # self.dataPlotsFigure.clf(keep_observers=True)
        vx = [None]*self.nAdcCh

        for i,a in list(self.dataPlotsSubplots.items()):
            a.cla()
#         for i,a in list(self.dataPlotsSubplots.items()):
            if i == self.nAdcCh-1:
                a.set_xlabel('t [us]')
                a.set_ylabel('[V]')
                continue
            artist.setp(a.get_xticklabels(), visible=False)
            a.set_ylabel("#{:d}".format(i), rotation=0)
        x = [self.adcDt * i for i in range(self.nSamples)]
        for i,a in list(self.dataPlotsSubplots.items()):
            a.locator_params(axis='y', tight=True, nbins=4)
            a.yaxis.set_major_formatter(FormatStrFormatter('%7.4f'))
            a.set_xlim([0.0, self.adcDt * self.nSamples])
            a.step(x, array.array('f', self.adcData[i*self.nSamples:(i+1)*self.nSamples]), where='post')

            if self.sp is not None:
                self.sp.filter_channelx(i, self.adcData)
                vx[i] = np.array([self.sp.scrAryp[k] for k in range(self.sp.nSamples)])
                self.yx[i].clear()
                self.yx[i].plot(x, vx[i], color='red')

        if self.dataInfoText:
            if self.dataInfo is None:
                self.dataInfo = self.dataPlotsFigure.text(0.02, 0.01, self.dataInfoText, ha='left', va='bottom', color='m', transform=self.dataPlotsFigure.transFigure)
            else: self.dataInfo.set_text(self.dataInfoText)

        self.dataPlotsCanvas.draw()
        self.dataPlotsToolbar.update()
        return

def test():
    # data

    sp1 = SignalProcessor()
    apply_config(sp1, 'Lithium/c')

    p1 = DataPanelGUILite()
    p1.sp = sp1

    fname1 = '/data/Samples/TMSPlane/fpgaLin/Dec05b/Dec05b_data_15.root'
    tree1 = TChain('tree1')
    tree1.Add(fname1)
    tree1.Show(0)

    tree1.SetBranchAddress('adc',p1.adcData)

    NMax = tree1.GetEntries()
    ievt = 0
    while ievt< NMax:
        print("Event:", ievt)
        tree1.GetEntry(ievt)
#         sp1.filter_channels()

        p1.plot_data()

        while True:
            x = input("Next:")
            if x=='q': sys.exit()
            elif len(x)>0 and x[0] == 's':
                for name in x.split()[1:]:
                    dirx = os.path.dirname(name)
                    if not os.path.exists(dirx): os.makedirs(dirx)
                    plt.savefig(name)
                    print("saved figure to", name)
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break


if __name__ == '__main__':
    test()
