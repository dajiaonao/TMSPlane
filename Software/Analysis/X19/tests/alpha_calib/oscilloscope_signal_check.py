#!/usr/bin/env python3
from multiprocessing import Pool
import matplotlib.pyplot as plt
# from scipy import signal
from scipy.signal import find_peaks, peak_prominences
import numpy as np
from sys import argv
from glob import glob
import os, time, re
import ROOT
from root_numpy import root2array, array2root

#signIt = lambda t: t if t<127 else t-256
signIt = lambda t: t 

myOutPutDir = './'

class findrate(object):
    header = ' '.join(["filename", "date", "time", "npeaks", "duration", "rates", "heightmean", "prominencemean", "widthmean", "bkg"])
    def __init__(self, filename="tek0001CH2.isf"):
        self.filename = filename
        self.timelap = 10. #second
        self.inputarray = np.array([])
        self.npeaks = 0
        self.date = ""
        self.time = ""
        self.diffpeakmean = 0
        self.heightmean = 0
        self.widthmean = 0
        self.prominencemean = 0
        self.bkg = 0
        self.isDebug = False
        self.showPlot = False

    def getinput(self):
        with open(self.filename,'rb') as f1:
            b0 = f1.read(1024)
            b1i = b0.find(b':CURVE')
            b = b0[:b1i]
            c = b.split(b';')

            b2 = b0[b1i:]
            c += [b2]

            pars = {}
            for v in c:
                a = v.find(b" ")
                if self.isDebug: print(v,a)
                pars[v[:a]] = v[a+1:]

            self.timelap = float(pars[b'WFID'].split(b',')[3].split(b'/')[0][1:6])
            self.timelap *=10
            self.date = pars[b':DATE'].decode("utf-8").strip('"')
            self.time = pars[b':TIME'].decode("utf-8").strip('"')
    
            wav = pars[b':CURVE'][10:]
            wav += f1.read()[:-1]
#             wav1 = [signIt(int(x)) for x in wav[::2]] if pars[b'BIT_NR'] == b'16' else [signIt(int(x)) for x in wav]
            wav1 = [signIt(int(x)) for x in wav[::2]] if pars[b'BIT_NR'] == b'16' else [int(x) for x in wav]
            if self.isDebug: print(len(wav1), wav1[:10])

            self.inputarray = np.asarray(wav1)

    def processinput(self, N):
        W = 1200
        basename = os.path.basename(self.filename)
        arwav2 = self.inputarray[:N] if N>0 else self.inputarray
        self.inputarray = None
        peaks, properties = find_peaks(arwav2, height=None, width=(100,500), wlen=W, prominence=2, distance=50) 

        if self.isDebug: print(len(peaks),peaks)
        #wav3 = [wav2[ix] for ix in peaks]

        promsall = peak_prominences(arwav2, peaks, wlen=W)
        proms = promsall[0]
        promxmins = promsall[1]
        promxmaxs = promsall[2]
        lpromscallow = []
        for i in range(len(proms)-1):
            if arwav2[promxmins[i]] < arwav2[promxmaxs[i]]:
                lpromscallow.append(arwav2[peaks[i]] - arwav2[promxmins[i]])
            else:
                lpromscallow.append(arwav2[peaks[i]] - arwav2[promxmaxs[i]])
        promscallow = np.asarray(lpromscallow)
        if self.isDebug:
            print(proms[:10])
            print(promscallow[:10])

        if self.showPlot:
            contour_heights = arwav2[peaks] - proms
            plt.plot(arwav2)
            plt.plot(peaks, arwav2[peaks], "x")
            plt.vlines(x=peaks, ymin=contour_heights, ymax=arwav2[peaks], color = "C1")
            plt.vlines(promxmins, ymin=contour_heights, ymax=arwav2[peaks], color = "C2", linestyles = "dashed")
            plt.vlines(promxmaxs, ymin=contour_heights, ymax=arwav2[peaks], color = "C2", linestyles = "dotted")
            plt.hlines(y=arwav2[peaks], xmin=promxmins, xmax=promxmaxs, color = "C2", linestyles = "dashdot")
            plt.hlines(y=properties["width_heights"], xmin=properties["left_ips"], xmax=properties["right_ips"], color = "C1")

            #x2 = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
            fig0, ax0 = plt.subplots(num="diffpeak_"+basename)

            num_bins = 50
            # the histogram of the data
            n, bins, patches = ax0.hist(np.diff(peaks), num_bins)
            

            fig1, ax1 = plt.subplots(num="peakheight_"+basename)
            #n, bins, patches = ax.hist([arwav1[ix] for ix in peaks], num_bins)
            ax1.hist(arwav2[peaks], num_bins)

            fig2, ax2 = plt.subplots(num="peakprom_"+basename)
            #plt.plot(proms)
            ax2.hist(proms, num_bins)
#             plt.show()

        ### get the values
        self.npeaks = len(peaks)
        pks = arwav2[peaks]
        df_pks = np.diff(peaks)
        widths = properties['widths']

        ### calculate means
        self.heightmean = np.mean(pks)
        self.diffpeakmean = np.mean(df_pks)
        self.prominencemean = np.mean(proms)
        self.widthmean = np.mean(widths)

#         mdx = np.array([])
#         for i in range(self.npeaks-1):
#             if peaks[i+1]-peaks[i]<1000: continue
# #             print(peaks[i],peaks[i+1])
#             a,b = int(peaks[i])+500, int(peaks[i+1])-500
#             mdx = np.append(mdx,arwav2[a:b])
#         self.bkg = np.std(mdx)


        midds = [int(0.5*(peaks[i]+peaks[i+1])) for i in range(self.npeaks-1) if peaks[i+1]-peaks[i]>1000]
        self.bkg = np.std(arwav2[midds])

        ### save to root
        df_pks = np.append(np.array([-1]),df_pks)
        bigx = np.array([(df_pks[i],pks[i],proms[i],widths[i]) for i in range(self.npeaks)],dtype=[('dt',np.float32),('pk',np.float32),('proms',np.float32),('width',np.float32)])
        rootfile = array2root( bigx, myOutPutDir+"/"+basename[:-4] + '.root',  mode="recreate")

    def get_summary(self):
        return f"{os.path.basename(self.filename)} {self.date}_{self.time} {self.npeaks} {self.timelap} {self.npeaks/self.timelap} {self.heightmean:.3f} {self.prominencemean:.3f} {self.widthmean:.3f} {self.bkg:.3f}"

def processor(inputName):
    print(f"Processing {inputName}")
    myrate = findrate(inputName)
    myrate.getinput()
    myrate.processinput(-1)
    return myrate

def multi_run():
    script, pattern, Nfiles, mydir = argv

    if not os.path.exists(mydir): os.makedirs(mydir)
    global myOutPutDir
    myOutPutDir = mydir

    filesall = sorted([f for f in glob(pattern) if not os.path.exists(mydir+'/'+os.path.basename(f)[:-4]+'.root')], key=lambda f:os.path.getmtime(f))
    files = filesall[:int(Nfiles)] if int(Nfiles)>0 else filesall[:]
    print(files)
    myrates = []
    print(len(files))

    p = Pool(6)
    myrates = p.map(processor, files)
   
    newfile = open(mydir+"/summary.txt","a")
    print(findrate.header)
    for i in range(len(myrates)):
        s = myrates[i].get_summary()
        print(s)
        newfile.write(s+'\n')   


def test():
    script, pattern, Nfiles = argv
    filesall = sorted([f for f in glob(pattern)], key=lambda f:os.path.getmtime(f))
    files = filesall[:int(Nfiles)] if int(Nfiles)>0 else filesall[:]
    print(files)
    myrates = []
    print(len(files))
    for i in range(len(files)):
        print(f"processing the {i} of {len(files)} file: {files[i]}")
        myrate = findrate(files[i])
        myrate.showPlot = True
        myrate.getinput()
        myrate.processinput(-1)
        myrates.append(myrate)
    print(myrate.header)
    for i in range(len(myrates)):
        print(myrates[i].get_summary())

    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close("all")

def main():
    if len(argv)>3: multi_run()
    else: test()

if __name__ == '__main__':
    main()
#     test()
    #multi_run()
