#!/usr/bin/env python3
import sys, os
import time
import threading
from TMS1mmX19Tuner import DataPanelGUI, CommonData
from array import array
from glob import glob
from ROOT import TFile, TChain, gDirectory
from datetime import datetime

if sys.version_info[0] < 3:
    import tkinter as tk
else:
    import tkinter as tk

def savehistory(dir1=os.environ["HOME"]):
    import rlcompleter, readline
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set show-all-if-ambiguous On')

    import atexit
    f = os.path.join(dir1, ".python_history")
    try:
        readline.read_history_file(f)
    except IOError:
        pass
    atexit.register(readline.write_history_file, f)


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
                print((i, f))

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
        itree0 = -1
        irun = -1

        while True:
            ievt1 = ievt
            if elist is not None:
                ievt1 = self.tree.GetEntryNumber(ievt)
                print('Entry:')

            if ievt1 >= 0:
                ret = self.tree.GetEntry(ievt1)
                if ret == 0:
                    print("Invalid event number:", ievt1, '. Not read from file!!!!!')

                itree = self.tree.GetTreeNumber()
                if itree != itree0:
                    itree0 = itree
                    fname = self.tree.GetListOfFiles()[itree0].GetTitle()
                    try:
                        irun = int(fname.rstrip('.root').split('_')[-1])
                    except ValueError:
                        irun = -1
                    print(fname, irun)

                self.dataPanel.dataInfoText = ', '.join(['Run '+str(irun), 'Event '+str(ievt1), str(datetime.fromtimestamp(self.dataT[0]))])
                self.dataPanel.plot_data()
            else:
                print("Invalid event number:", ievt1, '!!!!!')

            print('Event:', ievt1, itree, irun)

            x = input("Next:")
#             if x=='q': sys.exit()
            if x=='q': return
            elif len(x)>0 and x[0] == 's':
                names = x.split()[1:]
#                 print '+',names,'+',len(names)
                if len(names)==0: names = ['run{0:d}_event{1:d}'.format(irun, ievt1)]
#                 print 'will save as'names
                for name in names:
                    dirx = os.path.dirname(name)
#                     print dirx, 'ppp'
                    if dirx and (not os.path.exists(dirx)): os.makedirs(dirx)
                    self.dataPanel.dataPlotsFigure.savefig(name)
                    print("saved figure to", name)
            elif len(x)>2 and x[:2] == 'f ':
                try:
                    fname = x[2:]
                    print("Switching to file:", fname)
                    self.get_file(fname)
                    ievt = 0
                except ValueError:
                    print("Error in parsing the file name:",fname)
            elif len(x)>2 and x[:2] == 'c ':
                try:
                    self.tree.SetEntryList(0)
                    self.tree.Draw('>>elist',x[2:],'entrylist')
                    elist = gDirectory.Get('elist')
                    self.tree.SetEntryList(elist)
                    print("selection",x[2:], 'applied (', elist.GetN(), 'entries)')
                    ievt = 0
                except ValueError:
                    print("failed to set the entrylist")
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
        self.irun = -1
        self.mfileI = -1

    def get_file(self):
        files = sorted(glob(self.fPattern), key=lambda f:os.path.getmtime(f))
        if len(files)>-self.mfileI-1:
            f = files[self.mfileI]
            if f != self.currentFile: self.update_tree(f)

    def update_tree(self, f):
        tFile = TFile(f,'read')
        tree = tFile.Get('tree1')
        if not tree: return

        if self.tFile: self.tFile.Close()
        self.currentFile = f
        self.tFile = tFile
        self.tree = tree
        print("Using file", self.currentFile)
        try:
            self.irun = int(self.currentFile.rstrip('.1').rstrip('.root').split('_')[-1])
#             self.irun = int(self.currentFile.rstrip('.root').split('_')[-1])
        except (TypeError, ValueError):
            self.irun = -1
        self.tree.SetBranchAddress('adc',self.cd.adcData)
        self.tree.SetBranchAddress('T',self.dataT)

    def run(self):
        n_old = None
        with self.cd.cv:
            while not self.cd.quit:
                self.get_file()
                if self.tFile is None:
                    print("No file")
                    time.sleep(10)
                    continue

                self.tree.Refresh()
                n = self.tree.GetEntries()
                if n==0:
                    print("0 Entry, waiting....")
                    continue

                print('Event', n-1)
                if n != n_old:
                    self.tree.GetEntry(n-1)
                    self.dataPanel.dataInfoText = ', '.join(['Run '+str(self.irun), 'Event '+str(n-1), str(datetime.fromtimestamp(self.dataT[0]))])
                    self.dataPanel.plot_data()
                    n_old = n
             
                ### to get notified from the data pannel
                self.cd.cv.acquire()
                self.cd.cv.wait(self.dT)
                self.cd.cv.release()
 
def monitor(pattern='data/fpgaLin/Feb27a_data_*.root'):
    cd = CommonData()
    root = tk.Tk()
    dataPanel = DataPanelGUI(root, cd, visibleChannels=None)

    du1 = DataUpdater(cd, dataPanel)
    du1.mfileI = -1
    du1.fPattern = pattern
    du1.run()
    #du1.start()

    #root.mainloop()
    #du1.join()

def view(fname='data/fpgaLin/tt_test.root'):
#     if len(sys.argv)>1: fname = sys.argv[1]

    cd = CommonData()
    root = tk.Tk()
    dataPanel = DataPanelGUI(root, cd, visibleChannels=None)

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
    savehistory()
#     monitor('data/fpgaLin/Feb27b_data_*.root')
#     monitor('data/fpgaLin/Feb28a_data_*.root')
#     monitor('data/fpgaLin/Mar07C*.root')
#     monitor('data/fpgaLin/Mar08D*.root')
#     view()
    main()
