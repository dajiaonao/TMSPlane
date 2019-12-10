#!/usr/bin/env python3
'''This module use the configuration from the reco_config.py and show the results'''
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
from ctypes import *
ANALYSIS_WAVEFORM_BASE_TYPE = c_float

class DataPanelGUILite(object):
    # @param [in] dataFigSize (w, h) in inches for the data plots figure assuming dpi=72
    def __init__(self, dataFigSize=(13, 12.5), visibleChannels=None, guiI=True):
        self.master = None
        self.nAdcCh = 20
        self.nSdmCh = 19
        self.adcDt =  0.2
        self.nSamples = 16384
        self.adcData = array.array('f',[0]*(self.nSamples*self.nAdcCh))
        self.sp = None

#         self.master.wm_title("Topmetal-S 1mm version x19 array data")
#         self.master.wm_protocol("WM_DELETE_WINDOW", self.quit)

        # frame for plotting
        self.dataInfo = None
        self.dataInfoText = None
#         self.dataPlotsFrame = tk.Frame(self.master)
        self.dataPlotsFrame = tk.Frame()
        self.dataPlotsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.dataPlotsFigure = Figure(figsize=dataFigSize, dpi=72)
        self.dataPlotsFigure.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.05, hspace=0, wspace=0)
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
        self.dataPlotsSubplots[self.nAdcCh-1] = dataPlotsSubplotN
        self.dataPlotsCanvas = FigureCanvasTkAgg(self.dataPlotsFigure, master=self.dataPlotsFrame)
        self.dataPlotsCanvas.draw()
        self.dataPlotsCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.dataPlotsToolbar = NavigationToolbar2Tk(self.dataPlotsCanvas, self.dataPlotsFrame)
        self.dataPlotsToolbar.update()
        self.dataPlotsCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.plot_data()

    def on_key_event(self, event):
        print(('You pressed {:s}'.format(event.key)))
        print((event.key, event.key=='r'))
        key_press_handler(event, self.dataPlotsCanvas, self.dataPlotsToolbar)

    def quit(self):
        self.master.quit()     # stops mainloop
        self.master.destroy()  # this is necessary on Windows to prevent
                               # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def plot_data(self):
        # self.dataPlotsFigure.clf(keep_observers=True)
        for i,a in list(self.dataPlotsSubplots.items()):
            a.cla()
        for i,a in list(self.dataPlotsSubplots.items()):
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
                self.sp.filter_channel(i, self.adcData)
                vx = np.array([self.sp.scrAry[k] for k in range(self.sp.nSamples)])
                a.plot(vx)

        if self.dataInfoText:
            if self.dataInfo is None:
                self.dataInfo = self.dataPlotsFigure.text(0.02, 0.01, self.dataInfoText, ha='left', va='bottom', color='m', transform=self.dataPlotsFigure.transFigure)
            else: self.dataInfo.set_text(self.dataInfoText)

        self.dataPlotsCanvas.draw()
        self.dataPlotsToolbar.update()
        return

def check():
    data1 = array('f',[0]*(16384*20))
    pTag = 'Feb25a'
    tagA = 'data/fpgaLin/'+pTag+'_data_'
    inRoot = 'data/fpgaLin/'+pTag+'_data_1138.root'
    if len(sys.argv)>1:
        if os.path.exists(sys.argv[1]):
            inRoot = sys.argv[1]
        elif os.path.exists(tagA+sys.argv[1]+'.root'):
            inRoot = tagA+sys.argv[1]+'.root'
        else:
            files = sorted([f for f in glob(tagA+'*.root')], key=lambda f:os.path.getmtime(f))

            a =  -1
            try:
                a = int(sys.argv[1])
            except TypeError:
                pass
            if time.time() - os.path.getmtime(files[-1]) < 10:
                print("dropping the latest file, which probably is still being written:", files[-1])
                if a!=0: files.pop()
                else: a = -1

            if abs(a)<len(files):
                inRoot = files[a]
            else:
                print("Index {0:d} out of range:{1:d}".format(a, len(files)))
                return

    print("Using file:", inRoot)
    fout1 = TFile(inRoot,'read')
    tree1 = fout1.Get('tree1')
    tree1.SetBranchAddress('adc',data1)

    print("Entries in the tree:", tree1.GetEntries())

    run = -1
    runPattern = '.*_data_(\d+).root'
    if runPattern is not None:
        m = re.match(runPattern, inRoot)
        if m:
            try:
                run = int(m.group(1))
            except ValueError:
                print("Run number not exatracted for file", iRoot)

    i = 56
    ich = 1
    sp1 = SignalProcessor()
    sp1.fltParam.clear()

    for x in [30, 50, 200, P]: sp1.fltParam.push_back(x)
    thre = [0.002]*sp1.nAdcCh
    thre[19] = 0.05
    sp1.ch_thre.clear()
    for x in thre: sp1.ch_thre.push_back(x)

    plt.ion()
    fig,axs = plt.subplots(nrows=20, ncols=1, sharex=True, sharey=False, squeeze=True, figsize=(13, 12.5), dpi=72)
    plt.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.05, hspace=0, wspace=0)
    plt.show()

    NMax = tree1.GetEntries()
    ievt = 0
    while ievt< NMax:

        print("Event:", ievt)
        tree1.GetEntry(ievt)

        for ich in range(sp1.nAdcCh):
            va = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]
            sp1.measure_pulse2(data1, ich)

            vx = np.array([sp1.scrAry[i] for i in range(sp1.nSamples)])
            vo = data1[ich*sp1.nSamples:(ich+1)*sp1.nSamples]

            axs[ich].clear()
            axs[ich].plot(vo)

            tx = axs[ich].twinx()
            tx.clear()
            tx.plot(vx,color='r')
        plt.draw()
        plt.grid(True)
        plt.pause(0.001)

        while True:
            x = input("Next:")
            if x=='q': sys.exit()
            elif len(x)>0 and x[0] == 's':
                for name in x.split()[1:]:
                    dirx = os.path.dirname(name)
                    if not os.path.exists(dirx): os.makedirs(dirx)
                    plt.savefig(name)
                    print("saved figure to", name)
            elif len(x)>2 and x[:2] == 'ch':
                try:
                    ich = int(x[2:])
                    print("Switching to channel:", ich)
                    break
                except ValueError:
                    continue
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1
                break

def test():
#     root = tk.Tk()
#     root.wm_title("Topmetal-S 1mm version x19 array Tuner")

    # data
#     dataPanelMaster = tk.Toplevel(root)
    p1 = DataPanelGUILite()

    sp1 = SignalProcessor()
    apply_config(sp1, 'Lithium/c')

    p1.sp = sp1

    fname1 = '/data/Samples/TMSPlane/fpgaLin/Dec05b/Dec05b_data_15.root'
    tree1 = TChain('tree1')
    tree1.Add(fname1)
    tree1.Show(0)

    waveLen = 16384
#     data1 = array('f',[0]*(waveLen*20))
#     data2 = array('f',[0]*waveLen)
    tree1.SetBranchAddress('adc',p1.adcData)


    for i in range(10):
        tree1.GetEntry(i)
        p1.plot_data()

        a = input("jjj")


if __name__ == '__main__':
#     check()
    test()
