#!/usr/bin/env python3
'''
input: *.isf from ossiloscopy for CSA
output: summary.txt and root files after peaks findings
'''

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
from array import array

#signIt = lambda t: t if t<127 else t-256
signIt = lambda t: t 

myOutPutDir = './'

class findrate(object):
    header = ' '.join(["filename", "date", "time", "npeaks", "duration", "rates", "heightmean", "prominencemean", "widthmean", "bkg", "prominencemean"])
    def __init__(self, filename="tek0001CH2.isf"):
        self.filename = filename
        self.timelap = 10. #second
        self.inputarray = np.array([])
        self.npeaks = 0
        self.npeaks_corr_pm2 = 0
        self.npeaks_corr_pm = 0
        self.npeaks_corr_pm3 = 0
        self.date = ""
        self.time = ""
        self.diffpeakmean = 0
        self.heightmean = 0
        self.widthmean = 0
        self.prominencemean = 0
        self.prominence2mean = 0
        self.prominence3mean = 0
        self.bkg = 0
        self.isDebug = False
        self.showPlot = False
        self.outputDir = None
        self.prominence2Cut=20
        self.prominenceCut=10
        self.prominence3Cut=20

#         self.process_fun = self.processinput
        self.process_fun = self.processinput_v1

    def getinput_from_root_v0(self, fname=None, entry=0):
        Nsample = 20000000
        data1 = array('B',[0]*Nsample)
        T0 = ROOT.TDatime()

        if fname is None: fname = self.filename
        f1 = ROOT.TFile(fname)
        tree1 = f1.Get('tr1')
        tree1.SetBranchAddress("data",data1)
        tree1.SetBranchAddress("T",ROOT.AddressOf(T0))

        tree1.GetEntry(entry)
        print(data1[:10], data1[-10:])
        print(T0)
        self.inputarray = np.asarray(data1)
        plt.plot(self.inputarray)
        plt.show()


    def getinput_from_root(self, fname=None, entry=0, idx0=None):
        Nsample = 20000000
        data1 = array('B',[0]*Nsample)
        idx = array('i',[0])
        T0 = ROOT.TDatime()

        if fname is None: fname = self.filename
        f1 = ROOT.TFile(fname)
        tree1 = f1.Get('tr1')
        tree1.SetBranchAddress("data",data1)
        tree1.SetBranchAddress("idx",idx)
        tree1.SetBranchAddress("T",ROOT.AddressOf(T0))

        if idx0 is not None:
            ### find the entry for idx0
            nSel = tree1.Draw("Entry$",f"idx=={idx0}","goff")
            if nSel == 0:
                print(f"No entry found with idx={idx0}")
                return None
            elif nSel > 1:
                print(f"{nSel} entries found with idx={idx0}.")
            v1 = tree1.GetV1()
            entry = int(v1[0])

        if self.isDebug: print(f"getting entry {entry}")
        tree1.GetEntry(entry)
        if self.isDebug:
            print(data1[:10], data1[-10:])
            print(idx[0])
            print(T0)
        self.inputarray = np.asarray(data1)
        plt.plot(self.inputarray)
        plt.show()

        return entry

    def corrected_proms(self, peaks):
        npeaks = len(peaks)
        prom2 = np.array([0]*npeaks)

        for i in range(npeaks):
            istart = 5 if i==0 else peaks[i-1]
            for y in range(peaks[i], istart, -1):
                if self.inputarray[y] > self.inputarray[peaks[i]]-4: continue
                if self.inputarray[y-1]<=self.inputarray[y]: continue;
                prom2[i] = self.inputarray[peaks[i]]-self.inputarray[y-4]
#                 print(f"{i}:{peaks[i]} -> {prom2[i]} -- {prom1[i]}")
                break
        return prom2

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
            if self.isDebug: print(len(wav1), wav1[:10], wav1[-10:])

            self.inputarray = np.asarray(wav1)

    def processinput_v1(self, N):
        '''Based on the default processinput function, but will only count the peaks pass a cut on prom3. This will remove more background and give a correct dt distribution for the rate estimation.'''
        print("using processinput_v1") # for debug

        W = 300
        basename = os.path.basename(self.filename)
        if N>0: self.inputarray = self.inputarray[:N]
        arwav2 = self.inputarray
#         peaks, properties = find_peaks(arwav2, height=None, width=(100,500), wlen=W, prominence=2, distance=160) 
        peaks, properties = find_peaks(arwav2, height=None, width=(20,300), wlen=W, prominence=2, distance=160) 
        if self.isDebug: print(len(peaks),peaks)

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

        ### get the values
        self.npeaks = len(peaks)
        pks = arwav2[peaks]
        df_pks = np.diff(peaks)
        widths = properties['widths']
        proms2 = self.corrected_proms(peaks)
        proms3 = pks - arwav2[promxmins]
        rtime = peaks - promxmins

        if self.isDebug:
            for i in range(self.npeaks):
                if abs(proms3[i]-proms2[i])>5:
                    print(peaks[i], proms3[i], proms2[i])

        ### plots if requested
        if self.showPlot:
            contour_heights = arwav2[peaks] - proms
            plt.plot(arwav2)
            plt.plot(peaks, arwav2[peaks], "x")
            plt.vlines(x=peaks, ymin=contour_heights, ymax=arwav2[peaks], color = "C1")
            plt.vlines(promxmins, ymin=contour_heights, ymax=arwav2[peaks], color = "C2", linestyles = "dashed")
            plt.vlines(promxmaxs, ymin=contour_heights, ymax=arwav2[peaks], color = "C2", linestyles = "dotted")
            plt.hlines(y=arwav2[peaks], xmin=promxmins, xmax=promxmaxs, color = "C2", linestyles = "dashdot")
            plt.hlines(y=properties["width_heights"], xmin=properties["left_ips"], xmax=properties["right_ips"], color = "C1")

            plt.plot(peaks, proms2, "+")
            plt.plot(peaks, proms3, "o")

            proms_diff = proms3 - proms2
            plt.plot(peaks, proms_diff)

            #x2 = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
            fig0, ax0 = plt.subplots(num="diffpeak_"+basename)

            num_bins = 50
            # the histogram of the data
            n, bins, patches = ax0.hist(np.diff(peaks), num_bins)

            fig1, ax1 = plt.subplots(num="peakheight_"+basename)
            #n, bins, patches = ax.hist([arwav1[ix] for ix in peaks], num_bins)
            ax1.hist(arwav2[peaks], num_bins)

            fig2, ax2 = plt.subplots(num="peakprom3_"+basename)
            #plt.plot(proms)
            ax2.hist(proms3, num_bins)
            plt.show()

        ### calculate means
#         self.heightmean = np.mean(pks)
#         self.diffpeakmean = np.mean(df_pks)
#         self.prominencemean = np.mean(proms)
#         self.prominence2mean = np.mean(proms2[proms2>self.prominence2Cut])
#         self.npeaks_corr = len(proms2[proms2>self.prominence2Cut])/self.timelap 
#         self.widthmean = np.mean(widths)
        self.heightmean = np.mean(pks)
        self.diffpeakmean = np.mean(df_pks)
        self.prominencemean = np.mean(proms)
        self.prominence2mean = np.mean(proms2[proms2>self.prominence2Cut])
        self.prominence3mean = np.mean(proms3[proms3>self.prominence3Cut])
        self.npeaks_corr_pm2 = len(proms2[proms2>self.prominence2Cut])
        self.npeaks_corr_pm = len(proms[proms>self.prominenceCut])
        self.npeaks_corr_pm3 = len(proms[proms3>self.prominence3Cut])
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
        bigx0 = np.array([(df_pks[i],pks[i],proms[i],widths[i],proms2[i],proms3[i],rtime[i]) for i in range(self.npeaks)],dtype=[('dt',np.float32),('pk',np.float32),('proms',np.float32),('width',np.float32),('proms2',np.float32), ('proms3',np.float32), ('rtime',np.float32)])
        print(bigx0.shape,bigx0.dtype)


        bigx = bigx0
        ### ---- let's do the interesting things here
#         pCut3 = 2
        pCut3 = 20
        dtC = None ### use None as initial value to deal with the first one properly
        for i in range(len(bigx0)):
            if proms3[i] > pCut3 and (proms3[i]<142 or proms3[i]>148):
#             if proms3[i] > pCut3 and (proms3[i]<180 or proms3[i]>190):
                if dtC is not None: bigx0['dt'][i] += dtC ### add the accumulated dt: dtC, no need for 1st one
                dtC = 0                                ### and reset dtC
            else:
                if dtC is not None: dtC += bigx0['dt'][i]  ### accumulating... no need for the 1st one
                bigx0['dt'][i] = -bigx0['dt'][i]              ### not necussary, but as a check

        bigx = bigx0[bigx0['proms3']>pCut3] ### a tough cut for the sake of sigal purity
        #### --- OK, interesting thing done, and cut made, ready to be saved now.


        oDir = self.outputDir if self.outputDir is not None else myOutPutDir
        rootfile = array2root(bigx, oDir+"/"+basename[:-4] + '.root',  mode="recreate")

        self.inputarray = None ### we do not need to keep it, otherwise it will take a lot of memory...


    def processinput(self, N):
        W = 500
        basename = os.path.basename(self.filename)
        if N>0: self.inputarray = self.inputarray[:N]
        arwav2 = self.inputarray
#         peaks, properties = find_peaks(arwav2, height=None, width=(100,500), wlen=W, prominence=2, distance=50) 
#         peaks, properties = find_peaks(arwav2, height=None, width=(100,500), wlen=W, prominence=2, distance=30) 
#        peaks, properties = find_peaks(arwav2, height=None, width=(100,500), wlen=2000, prominence=2, distance=160) 
        peaks, properties = find_peaks(arwav2, height=None, width=(100,500) , wlen=W, prominence=2, distance=160) 
#         peaks, properties = find_peaks(arwav2, height=None, wlen=W, prominence=2, width=(150,500), distance=30) 
#          peaks, properties = find_peaks(arwav2, height=None, width=100, prominence=2, distance=100, wlen=2000)
        if self.isDebug: print(len(peaks),peaks)
        #wav3 = [wav2[ix] for ix in peaks]

        promsall = peak_prominences(arwav2, peaks, wlen=W)
#         promsall = peak_prominences(arwav2, peaks, wlen=200)
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

        ### get the values
        self.npeaks = len(peaks)
        pks = arwav2[peaks]
        df_pks = np.diff(peaks)
        widths = properties['widths']
        proms2 = self.corrected_proms(peaks)
        proms3 = pks - arwav2[promxmins]
        rtime = peaks - promxmins

        if self.isDebug:
            for i in range(self.npeaks):
                if abs(proms3[i]-proms2[i])>5:
                    print(peaks[i], proms3[i], proms2[i])

        ### plots if requested
        if self.showPlot:
            contour_heights = arwav2[peaks] - proms
            plt.plot(arwav2)
            plt.plot(peaks, arwav2[peaks], "x")
            plt.vlines(x=peaks, ymin=contour_heights, ymax=arwav2[peaks], color = "C1")
            plt.vlines(promxmins, ymin=contour_heights, ymax=arwav2[peaks], color = "C2", linestyles = "dashed")
            plt.vlines(promxmaxs, ymin=contour_heights, ymax=arwav2[peaks], color = "C2", linestyles = "dotted")
            plt.hlines(y=arwav2[peaks], xmin=promxmins, xmax=promxmaxs, color = "C2", linestyles = "dashdot")
            plt.hlines(y=properties["width_heights"], xmin=properties["left_ips"], xmax=properties["right_ips"], color = "C1")

            plt.plot(peaks, proms2, "+")
            plt.plot(peaks, proms3, "o")

            proms_diff = proms3 - proms2
            plt.plot(peaks, proms_diff)

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
            plt.show()

        ### calculate means
        self.heightmean = np.mean(pks)
        self.diffpeakmean = np.mean(df_pks)
        self.prominencemean = np.mean(proms)
        self.prominence2mean = np.mean(proms2[proms2>self.prominence2Cut])
        self.prominence3mean = np.mean(proms3[proms3>self.prominence3Cut])
        self.npeaks_corr_pm2 = len(proms2[proms2>self.prominence2Cut])
        self.npeaks_corr_pm = len(proms[proms>self.prominenceCut])
        self.npeaks_corr_pm3 = len(proms[proms3>self.prominence3Cut])
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
        bigx = np.array([(df_pks[i],pks[i],proms[i],widths[i],proms2[i],proms3[i],rtime[i]) for i in range(self.npeaks)],dtype=[('dt',np.float32),('pk',np.float32),('proms',np.float32),('width',np.float32),('proms2',np.float32), ('proms3',np.float32), ('rtime',np.float32)])

        oDir = self.outputDir if self.outputDir is not None else myOutPutDir
        rootfile = array2root(bigx, oDir+"/"+basename[:-4] + '.root',  mode="recreate")

        self.inputarray = None ### we do not need to keep it, otherwise it will take a lot of memory...

    def get_summary(self):
        return f"{os.path.basename(self.filename)} {self.date}_{self.time} {self.npeaks} {self.timelap} {self.npeaks/self.timelap} {self.heightmean:.3f} {self.prominencemean:.3f} {self.widthmean:.3f} {self.bkg:.3f} {self.prominence2mean:.3f} {self.npeaks_corr_pm2/self.timelap} {self.npeaks_corr_pm/self.timelap} {self.prominence3mean:.3f} {self.npeaks_corr_pm3/self.timelap}"

def process_file(inputName):
    print(f"Processing {inputName}")
    myrate = findrate(inputName)
    myrate.getinput()
    myrate.process_fun(-1)
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
    myrates = p.map(process_file, files)
   
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
        myrate.process_fun(-1)
        myrates.append(myrate)
    print(myrate.header)
    for i in range(len(myrates)):
        print(myrates[i].get_summary())

    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close("all")

def test0():
    dir1 = '/data/Samples/TMSPlane/data/merged/Jan15a/'
    fr1 = findrate('/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air2_0.isf')
    fr1.isDebug = True
#     fr1.getinput()
#     fr1.getinput_from_root('/data/Samples/TMSPlane/merged/Jan15a/TPCHV2kV_PHV0V_air2.root')
    ret = fr1.getinput_from_root(dir1+'TPCHV2kV_PHV0V_air4_t0.root',idx0=352)
#     ret = fr1.getinput_from_root(dir1+'TPCHVoff_gasOff_Pulse_25mV_t0_29.root')
    if ret is None: return None

    fr1.showPlot = True
    fr1.process_fun(-1)
    print(fr1.get_summary())

def monitor(indir, outdir):
    '''In this mode, it will check the files in `indir` and process any files that is not included in the summary file, and the output histograms are put in `outdir`'''
    nUpdate = 10

    flist = []
    if outdir[-1] != '/': outdir = outdir.rstrip()+'/'
    if not os.path.exists(outdir): os.makedirs(outdir)
    summary_file = outdir+'summary.txt'

    flist = []
    modex = 'w'
    print(summary_file)
    if os.path.exists(summary_file):
        with open(summary_file,'r') as fin1:

            ### load the db first
            lines = fin1.readlines()
            flist = [line.split()[0] for line in lines if len(line.split())>1]
            print(flist)
            modex = 'a'

    with open(summary_file,modex) as fin1:
        while True:
            ### for exception capture
            try:
                ### get the list of the files in indir
                new_files = [f for f in glob(indir+'*.isf') if os.path.basename(f) not in flist]
                print(new_files)

                print(len(new_files), 'to be processed')
                nProcessed = 0
                for fx in new_files:
                    print(f"------processing {fx}")
                    myrate = findrate(fx)
#                     myrate.process_fun = myrate.processinput
                    myrate.outputDir = outdir
                    myrate.showPlot = False
                    myrate.getinput()
                    myrate.process_fun(-1)

                    fin1.write(myrate.get_summary()+'\n')   
                    flist.append(os.path.basename(fx))

                    nProcessed += 1
                    if nProcessed > nUpdate:
                        fin1.flush()
                        nProcessed = 0

                if nProcessed > 0: fin1.flush()

                ### wait for the next loop
                time.sleep(10) ### just means maximum 10s delay if the processing speed is higher than the data recording speed
            except KeyboardInterrupt:
                break

def main1():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filePath", help="the file or pattern to monitor")
    parser.add_option("-p", "--pattern",    dest="filePattern",    help="the file or pattern to view")
    parser.add_option("-m", "--monitor",    dest="monitorDir",    help="the file or pattern to view")
    parser.add_option("-d", "--dir",    dest="indir",    help="the file or pattern to view")
    parser.add_option("-o", "--outdir",    dest="outdir",    help="the file or pattern to view")

    (options, args) = parser.parse_args()

    if options.monitorPattern:
        monitor(options.monitorPattern)
    elif options.viewPattern:
        view(options.viewPattern)
    else:
        print("Unknown pattern")

def main():
    if len(argv)>3: multi_run()
    else: test()

if __name__ == '__main__':
#    monitor('/home/TMSTest/PlacTests/TMSPlane/data/fpgaLin/raw/May31a/','/data/TMS_data/Processed/May31a_cut20')
#    monitor('/data/TMS_data/raw/Jun25a_tek/','/data/TMS_data/Processed/Jun25a_p1')
#    monitor('/data/TMS_data/raw/Jun30a_tek/','/data/TMS_data/Processed/Jun30a_p1')
#    monitor('/data/TMS_data/raw/Jul12a_tek/','/data/TMS_data/Processed/Jul12a_p1')
#    monitor('/data/TMS_data/raw/Jul16b_tek/','/data/TMS_data/Processed/Jul16b_p1')
#    monitor('/data/TMS_data/raw/Jul16c_tek/','/data/TMS_data/Processed/Jul16c_p1')
#    monitor('/data/TMS_data/raw/Jul16d_tek/','/data/TMS_data/Processed/Jul16d_p2')
   monitor('/data/TMS_data/raw/Jul17a_tek/','/data/TMS_data/Processed/Jul17a_p1')
#     test0()
#     process_file('/data/Samples/TMSPlane/Jan15a/TPCHV2kV_PHV0V_air3_204.isf')
#     main()
#     test()
#       multi_run()
