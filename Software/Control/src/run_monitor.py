#!/usr/bin/env python
import sys, os
import time
import threading
from TMS1mmX19Tuner import DataPanelGUI, CommonData
from array import array
from glob import glob
from ROOT import TFile, TChain, gDirectory

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

class DataViewer():
    def __init__(self,cd,dp):
        self.cd = cd
        self.dataPanel = dp
        self.dataT = array('i',[0])
        self.tree = None
        self.treename = 'tree1'
        self.fName = 'data/fpgaLin/Feb27a_data_*.root'
        self.fIndx = 0
        self.fList = None

    def get_file_list(self, show=True):
        self.fList = glob(self.fName)
        if len(self.fList)>1:
            self.fName = self.fList[0]
            self.fIndx = 0
        if show:
            for i,f in enumerate(self.fList):
                print(i, f)

    def get_file(self, fname):
        self.tree = TChain(self.treename)
        self.tree.Add(fname)
        self.tree.SetBranchAddress('adc',self.cd.adcData)
        self.tree.SetBranchAddress('T',self.dataT)

    def run(self):
        if self.tree is None:
            if self.fName is not None:
                self.get_file(self.fName)
        elist = None
        ievt = 0
        while True:
            ievt1 = ievt
            if elist is not None:
                ievt1 = self.tree.GetEntryNumber(ievt)
                print 'Entry:', ievt,

            print 'Event:', ievt1
            if ievt1 >= 0:
                self.tree.GetEntry(ievt1)
                self.dataPanel.plot_data()
            else:
                print "Invalid event number!!!!"

            x = raw_input("Next:")
#             if x=='q': sys.exit()
            if x=='q': return
            elif len(x)>0 and x[0] == 's':
                for name in x.split()[1:]:
                    dirx = os.path.dirname(name)
                    if not os.path.exists(dirx): os.makedirs(dirx)
                    plt.savefig(name)
                    print "saved figure to", name
            elif len(x)>2 and x[:2] == 'f ':
                try:
                    fname = x[2:]
                    print "Switching to file:", fname
                    self.get_file(fname)
                    ievt = 0
                except ValueError:
                    print "Error in parsing the file name:",fname
            elif len(x)>2 and x[:2] == 'c ':
                try:
                    self.tree.SetEntryList(0)
                    self.tree.Draw('>>elist',x[2:],'entrylist')
                    elist = gDirectory.Get('elist')
                    self.tree.SetEntryList(elist)
                    print "selection",x[2:], 'applied (', elist.GetN(), 'entries)'
                    ievt = 0
                except ValueError:
                    print "failed to set the entrylist"
                    self.tree.SetEntryList(0)
                    elist = None
            else:
                try:
                    ievt = int(x)
                except ValueError:
                    ievt += 1

class DataUpdater(threading.Thread):
    def __init__(self, cd, dp):
        threading.Thread.__init__(self)
        self.cd = cd
        self.dT = 10
        self.dataPanel = dp
        self.fPattern = 'data/fpgaLin/Feb27a_data_*.root'
        self.currentFile = None
        self.dataT = array('i',[0])
        self.tFile = None

    def get_file(self):
        files = sorted(glob(self.fPattern), key=lambda f:os.path.getmtime(f))
        if len(files)>0:
            f = files[-1]
            if f != self.currentFile: self.update_tree(f)
    def update_tree(self, f):
        tFile = TFile(f,'read')
        tree = tFile.Get('tree1')
        if not tree: return

        if self.tFile: self.tFile.Close()
        self.currentFile = f
        self.tFile = tFile
        self.tree = tree
        print "Using file", self.currentFile
        self.tree.SetBranchAddress('adc',self.cd.adcData)
        self.tree.SetBranchAddress('T',self.dataT)

    def run(self):
        n_old = None
        with self.cd.cv:
            while not self.cd.quit:
                self.get_file()
                self.tree.Refresh()
                n = self.tree.GetEntries()
                if n==0:
                    print "0 Entry, waiting...."
                    continue
                self.tree.GetEntry(n-1)
                print 'Event', n-1

                if n != n_old:
                    self.dataPanel.plot_data()

                ### to get notified from the data pannel
                self.cd.cv.acquire()
                self.cd.cv.wait(self.dT)
                self.cd.cv.release()
 
def monitor(pattern='data/fpgaLin/Feb27a_data_*.root'):
    cd = CommonData()
    root = tk.Tk()
    dataPanel = DataPanelGUI(root, cd, visibleChannels=None, guiI=False)

    du1 = DataUpdater(cd, dataPanel)
    du1.fPattern = pattern
    du1.start()

    root.mainloop()
    du1.join()

def view(fname='data/fpgaLin/tt_test.root'):
#     if len(sys.argv)>1: fname = sys.argv[1]

    cd = CommonData()
    root = tk.Tk()
    dataPanel = DataPanelGUI(root, cd, visibleChannels=None, guiI=False)

    dv1 = DataViewer(cd, dataPanel)
    dv1.fName = fname
    dv1.run()

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-m", "--monitor", dest="monitorPattern", help="the file or pattern to monitor")
    parser.add_option("-v", "--view",    dest="viewPattern",    help="the file or pattern to view")

    (options, args) = parser.parse_args()

    if options.monitorPattern:
        monitor(options.monitorPattern)
    elif options.viewPattern:
        view(options.viewPattern)
    else:
        print("Unknown pattern")

if __name__ == '__main__':
#     monitor('data/fpgaLin/Feb27b_data_*.root')
#     monitor('data/fpgaLin/Feb28a_data_*.root')
#     monitor('data/fpgaLin/Mar07C*.root')
#     monitor('data/fpgaLin/Mar08D*.root')
#     view()
    main()
