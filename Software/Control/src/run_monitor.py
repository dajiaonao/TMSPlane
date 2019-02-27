#!/usr/bin/env python
import sys, os
import time
import threading
from TMS1mmX19Tuner import DataPanelGUI, CommonData
from array import array
from glob import glob
from ROOT import TFile

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

class DataUpdater(threading.Thread):
    def __init__(self, cd, dp):
        threading.Thread.__init__(self)
        self.cd = cd
        self.dT = 10
        self.dataPanel = dp
        self.fPattern = 'data/fpgaLin/Feb27a_data_*.root'
        self.currentFile = None
        self.dataT = array('i',[0])
        self.on = True

    def get_file(self):
        files = sorted(glob(self.fPattern), key=lambda f:os.path.getmtime(f))
        if len(files)>0:
            f = files[-1]
            if f != self.currentFile: self.update_tree(f)
    def update_tree(self, f):
        tFile = TFile(f,'read')
        tree = tFile.Get('tree1')
        if not tree: return

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
                print 'Event', n
                if n==0:
                    print "0 Entry, waiting...."
                    continue
                self.tree.GetEntry(n-1)

                if n != n_old:
                    self.dataPanel.plot_data()
                time.sleep(self.dT)
 
def test1():
    cd = CommonData()
    root = tk.Tk()
    dataPanelMaster = tk.Toplevel(root)
    dataPanel = DataPanelGUI(dataPanelMaster, cd, visibleChannels=None)

    du1 = DataUpdater(cd, dataPanel)
    du1.start()

    root.mainloop()

    du1.on = False
    du1.join()

if __name__ == '__main__':
    test1()
