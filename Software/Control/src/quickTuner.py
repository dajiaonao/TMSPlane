#!/usr/bin/env python
import socket
from TMS1mmX19Tuner1 import CommonData, SensorConfig
from command import *
from math import sqrt
from rootUtil import waitRootCmdX, get_default_fig_dir, savehistory
from ROOT import TGraph, TLatex, gPad, gStyle, Error, Info, Warning, gROOT, TLegend, TF1, TGraphErrors
from array import array
import sys, time
import logging as lg

sDir = get_default_fig_dir()
sTag = "test_"
sDirectly = False

if gROOT.IsBatch(): sDirectly = True

isDebug = True
# lg.basicConfig(level=lg.DEBUG,
#                 format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                 datefmt='%a, %d %b %Y %H:%M:%S',
#                 filename='myapp.log',
#                 filemode='w')

def checkNSeq(d, n, i, v):
    nd = len(d)
    for j in range(n, n+i):
        if j>nd or j<0: return False

def growList(l):
    i = 0
    while True:
       yield l[i] if i<len(l) else -1
       i+=1

def loopList(l):
    i = 0
    N = len(l)
    while True:
       yield l[i%N]
       i+=1

def farList(start, end, n=-1):
    clist = [end]
    i = 0
    while True:
        i += 1
        if i==len(clist):
            dx = (clist[0]-start)*0.5
            clist = [x-dx for x in clist]+[end]
            i = 0
        yield clist[i]

def farList3(start,end):
    N = 1
    i = 0
    dx = 0.5*(end-start)
    while True:
        if i==N:
            N += 1
            dx = (end-start)/(N+1)
            pass
        yield x


def farList2(ls1):
    start = ls1[0]
    end = ls1[1]
    dx = 0.5*(start+end)
    dx0 = dx
    dx1 = dx
    while True:
        if x2>dx1 or x2<dx0:
            dx *= -0.5
            if x2>dx1: dx1 = x2
            elif x2<x0: dx0 = x2
        x2 += dx

        yield x2

def getMeanVar(l, useVar2=False):
    muS = 0
    var2S = 0
    for x in l:
        muS += x
        var2S += x*x
    iN = 1./len(l)
    muS *= iN
    var2S = var2S*iN - muS*muS
    if not useVar2: var2S = sqrt(var2S)
    return muS, var2S



plot_count = 0
class SigInfo:
    def __init__(self, data=None):
        self.resp = [] # [(t0, dT, tM, A),]
        self.lt = TLatex()
        self.sTag = sTag
        self.sDir = sDir
        self.autoSave = sDirectly
        if data:
            self.extract(data)
        else:
            self.bkgMu = None
            self.bkgVar = None
            self.quality = None
    def show(self, data, info=None, info2=None):
        x = [0.2*i for i in range(len(data))]
        g0 = TGraph(len(data), array('d',x), array('d',data))
        g0.Draw("AP")
        g0.GetHistogram().GetYaxis().SetTitle("V_{out} [V]")
        g0.GetHistogram().GetXaxis().SetTitle("t [#mus]")
#         g0.GetHistogram().GetYaxis().SetRangeUser(0.9, 1.4)

        if info: self.lt.DrawLatexNDC(0.2,0.8,info)
        if info2: self.lt.DrawLatexNDC(0.2,0.93,info2)

        global plot_count
        plot_count += 1

        waitRootCmdX(self.sDir+self.sTag+str(plot_count), self.autoSave)


    def showMore(self, data, info=None, info2=None):
        x = [0.2*i for i in range(len(data))]
        g0 = TGraph(len(data), array('d',x), array('d',data))
        g0.Draw("AP")
        g0.GetHistogram().GetYaxis().SetTitle("V_{out} [V]")
        g0.GetHistogram().GetXaxis().SetTitle("t [#mus]")
#         g0.GetHistogram().GetYaxis().SetRangeUser(0.9, 1.4)

        if info: self.lt.DrawLatexNDC(0.2,0.8,info)
        if info2: self.lt.DrawLatexNDC(0.2,0.93,info2)

        ### add info
        n1=500; n2=2000; np=20
        maxI, mx = max(enumerate(data[:-n2+np]), key=lambda p:p[1])
        minI, mn = min(enumerate(data[:-n2+np]), key=lambda p:p[1])
        dx = 0.5*(mx-mn)
        dn1 = sum(data[maxI+n1:maxI+n1+np])/np
        dn2 = sum(data[maxI+n2:maxI+n2+np])/np

        ## we want large dx, large #2 and small #3
#         return (0.5*(mx+mn), dx, 1-(mx-dn1)/dx, 1-(mx-dn2)/dx, maxI-minI)

        ### A line for the mean
        fun1 = TF1("fun1",str(0.5*(mx+mn)), 0, 99999999)
        fun1.SetLineColor(3)
        fun1.SetLineStyle(2)
        fun1.Draw("same")
        ### Draw 2 circles for max and min
        gr1 = TGraph()
        gr1.SetPoint(0, maxI*0.2, mx)
        gr1.SetMarkerColor(2)
        gr1.SetMarkerStyle(24)
        gr1.Draw("Psame")

        gr2 = TGraph()
        gr2.SetPoint(0, minI*0.2, mn)
        gr2.SetMarkerColor(4)
        gr2.SetMarkerStyle(24)
        gr2.Draw("Psame")
        ### Add two arrows for the the n50 and n2000
        gr3 = TGraph()
        gr3.SetPoint(0, (maxI+n1)*0.2, dn1)
        gr3.SetMarkerColor(2)
        gr3.SetMarkerStyle(23)
        gr3.Draw("Psame")

        gr4 = TGraph()
        gr4.SetPoint(0, (maxI+n2)*0.2, dn2)
        gr4.SetMarkerColor(4)
        gr4.SetMarkerStyle(23)
        gr4.Draw("Psame")
       
        global plot_count
        plot_count += 1

        waitRootCmdX(self.sDir+self.sTag+str(plot_count), self.autoSave)

    def getQuickInfo(self, data, n1=500, n2=2000, np=20):
        '''Get some useful infomation quickly'''
        maxI, mx = max(enumerate(data[:-n2+np]), key=lambda p:p[1])
        minI, mn = min(enumerate(data[:-n2+np]), key=lambda p:p[1])
        dx = 0.5*(mx-mn)
        dn1 = sum(data[maxI+n1:maxI+n1+np])/np
        dn2 = sum(data[maxI+n2:maxI+n2+np])/np
#         dn1 = max(data[maxI+n1:maxI+n1+np])
#         dn2 = max(data[maxI+n2:maxI+n2+np])
#         print mx, dn1, dn2, dx,

#         avarged = [sum(data[50*t:min([50*t+50,len(data)])] for t in range(len(data)/50))]

        ## we want large dx, large #2 and small #3
        return (0.5*(mx+mn), dx, 1-(mx-dn1)/dx, 1-(mx-dn2)/dx, maxI-minI)

    def extract(self, data):
        self.resp = []
        nData = len(data)
        muS = 0
        var2S = 0
        for i in range(nData):
            muS += data[i]
            var2S += data[i]*data[i]

        ### remove the outliers one by one
        minMs = 3*3

        data2 = data[:]
        mu = muS/nData
        var2 = var2S/nData - mu*mu

        for i in range(nData):
            ## get max and idex
            mI, ms = max(enumerate([(x and pow(x-mu,2)/var2) for x in data2]), key=lambda p:p[1])
            data2[mI] = None
            idata = nData-i-1
            if isDebug: print mI, 'removed', idata, 'left. Max Zn=', ms 

            if ms<minMs: break
            mV = data[mI]

            var2S -= mV*mV
            muS -= mV

            mu = muS/idata
            var2 = var2S/idata - mu*mu

        self.bkgMu = mu
        self.bkgVar = sqrt(var2)

        ### get fragments
        iStart = None
        nLow = 0
        for i in range(nData):
            if data2[i] is not None and iStart is not None:
                if nLow == 0:
                    nLow += 1
                    if i+1<nData and data2[i+1] is None: continue ## require at least two consective None
                    if i+2<nData and data2[i+2] is None: continue ## require at least two consective None

                if i-iStart > 10:
                    mI, mx = max(enumerate(data[iStart:i]), key=lambda p:abs(p[1]-mu))
                    self.resp.append((iStart, i-iStart, mI, mx-mu))
                iStart = None
                nLow = 0
            elif iStart is None and data2[i] is None:
                iStart = i
        ### remove low quality peaks
        if len(self.resp) > 0:
            self.quality = max([abs(x[3]) for x in self.resp])
#         mx = max(self.resp, key=lambda p:abs(p[3]))
#         self.resp = [x for x in self.resp if abs(x[3])>0.3*mx[3]]
#         print mx


        if isDebug:
            print self.resp, self.quality
            print mu, var2, len([x for x in data2 if x is not None])

        x = [0.2*i for i in range(nData)]
        g0 = TGraph(nData, array('d',x), array('d',data))
        g0.Draw("AP")
        g0.GetHistogram().GetYaxis().SetTitle("V_{out} [V]")
        g0.GetHistogram().GetXaxis().SetTitle("t [#mus]")

        g1 = TGraph(nData, array('d',[x[0]*0.2 for x in enumerate(data2) if x[1] is not None]), array('d',[x[1] for x in enumerate(data2) if x[1] is not None]))
        g1.SetMarkerColor(2)
        g1.Draw('Psame')
        
        waitRootCmdX()

class TuneResults:
    def __init__(self,nPar=6):
        self.inputVs = [None]*nPar
        self.status = None
    def show(self):
        print self.inputVs
        print self.status

class QuickTuner:
    def __init__(self, mode=0):
        self.mode = mode # 0: normal, 1: testing
        self.sensorConfig = None
        self.showPlot = True
        self.gainRef = None
        self.tuneRef = [0.6, -1, 0.3, 0.1]
        self.logFile = None
        self.lt = TLatex()
        self.stepI = 0
        self.sDir = sDir
        self.sTag = sTag
        self.autoSave = sDirectly
        self.halfPeriod = 2500
        
        ### To save the results a list of [((),())]
        self.results = None

        self.setup()

    def setupLogFile(self,fname):
        self.logFile = open(fname,'a')

    def setup(self):
        ### get connected
        data_ip_port = "192.168.2.3:1024"
        control_ip_port = "192.168.2.3:1025"
        dataIpPort = data_ip_port.split(':')
        sD = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        ctrlIpPort = control_ip_port.split(':')
        sC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        cmd = Cmd()
        cd = CommonData(cmd, dataSocket=sD, ctrlSocket=sC)
        cd.aoutBuf = 1 
        cd.x2gain = 2
        cd.sdmMode = 0
        cd.bufferTest = 0

        if self.mode == 0:
            sD.connect((dataIpPort[0],int(dataIpPort[1])))
            sC.connect((ctrlIpPort[0],int(ctrlIpPort[1])))
            self.sensorConfig = SensorConfig(cd)

        cd.getCurrentBest()

        for i in range(len(cd.sensorVcodes)):
            print i, [cd.tms1mmReg.dac_code2volt(vx) for vx in cd.sensorVcodes[i]]

    def get_score(self, data):
        score = 0
        ## is there any structure?
        ### Find the jumps
        nP = 10 # use 10 previous points if exist
        nTh = 4
        pPoints = []
        nPoints = []

        nData = len(data)
        for i in range(nData):
            ### get the average of previous nP points -- these nP should be similar

            av = 0.
            av2 = 0.
            nPp = 0
            for j in range(nP):
                jx = i-1-j
                if jx < 0: break
                jv = data[jx]

                nPp += 1
                av += jv
                av2 += jv*jv
            if nPp <2: continue ### not enough points

            av /= nPp
            av2 /= nPp
            av2 -= av*av
            av2 = sqrt(av2)

            nOut = 0
            for j in range(nP):
                jx = i-1-j
                if jx>=0 and abs(data[jx]-av)/av2 > 4: nOut += 1

            if i<50:
                print i, av, av2, nOut 

            if nOut > 0 or av/av2<2: # not good average
                continue ## skip as we can't judge...

            if (data[i]-av)/av2 > 5: ### good positive point
                pPoints.append((i, data[i]-av))
            elif (data[i]-av)/av2 < -5:
                nPoints.append((i, av-data[i]))
                
         
            ### Compare with current one

        print pPoints
        print nPoints
        ## is it a signal structure?
        ## How good is the signal?

        return score;

#     def assess(self,  isensor=None, inputVs=[1.379, 1.546, 1.626, 1.169, 1.357, 2.458], adjustDecayTime=10):
    def assess(self, isensor=None, inputVs=None, adjustDecayTime=10, adjustRef=True):
        tname = self.__class__.__name__ + ':' + sys._getframe().f_code.co_name

        cd = self.sensorConfig.cd
        cd.updatePars(isensor, inputVs)

        isensor = cd.currentSensor
        self.sensorConfig.update_sensor(isensor) 
        print("Checking:", isensor, cd.inputVs)

        ### get new data
        time.sleep(5)
        data = cd.adcData[isensor]
        a1 = SigInfo()
        a1.sTag = self.sTag

        r = (0,0,0,0,0)
        nTest = 10
        if self.mode==0:
            var = 99
            nTried = 0
            while nTried<4:
                rAva = []
                rL = [0,0,0,0,0]
                for k in range(nTest):
                    cd.fetch()
                    r = a1.getQuickInfo(data)
                    rAva.append(r[1])
                    for i in range(len(r)): rL[i] += r[i]/nTest
                mu,var = getMeanVar(rAva)
#                 print mu, var
                r = tuple(rL)
                if var<0.002:
                    print "Convereged."
                    break

                print "Not stable"
                time.sleep(10)
                nTried += 1 

        if self.logFile:
            infox = "{1:d}> P{0:d}:".format(isensor, self.stepI)
            infox += ', '.join(['{0:.3f}'.format(x) for x in cd.inputVs])
            infox += '->'+' '.join('{0:.4f}'.format(x) for x in r)
            self.logFile.write(infox+'\n')
        self.stepI += 1

        print "temp results: r=", r
        if self.showPlot:
            ref = self.gainRef if self.gainRef else -1
            a1.show(data, "P{1:d}: A={0:.4f} ({2:.4f})".format(r[1],isensor, ref),', '.join(['{0:.3f}'.format(x) for x in cd.inputVs]))

        if self.gainRef and self.gainRef - r[1]>0.002:
            Warning(tname, "Will not fine tune")
            return None

        if adjustRef:
            inputVs_t = cd.inputVs[:]
            if r[0]+r[1]>1.25:
                print '-----r[0]=', r[0], cd.voltsNames[5], ':',cd.inputVs[5],'->',
                cd.inputVs[5] -= 0.01
                print cd.inputVs[5]
                r_t = self.assess(isensor, cd.inputVs, adjustDecayTime, True)

                ### check the results: the gain should not degrade much, the avarage should get smaller
                if r_t[1]-r[1]>-0.002 and r_t[0]<r[0]:
                    r = r_t
                else:
                    cd.inputVs = inputVs_t
                    Error(tname, "Failed to reduce r[0], reverting...")

            elif r[0]<self.tuneRef[0] and cd.inputVs[5]<2.99:
                print '-----r[0]=', r[0], cd.voltsNames[5], ':',cd.inputVs[5],'->',
                cd.inputVs[5] += 0.01
                print cd.inputVs[5]
                r_t = self.assess(isensor, cd.inputVs, adjustDecayTime, True)

                ### check the results
                if r_t[1]-r[1]<-0.002 and r_t[0]>r[0]:
                    r = r_t
                else:
                    cd.inputVs = inputVs_t
                    Error(tname, "Failed to increase r[0], reverting...")

        if adjustDecayTime and r[1]>0.004:
            inputVs_t = cd.inputVs[:]
            adjustDecayTime -= 1
            print r[4], float(abs(r[4])%self.halfPeriod)/self.halfPeriod
            if r[3]>self.tuneRef[3] or r[3]<-0.1 or float(abs(r[4])%self.halfPeriod)/self.halfPeriod>0.1:
                print '-----r[3]=', r[3], cd.voltsNames[4], ':',cd.inputVs[4],'->',
                cd.inputVs[4] += 0.01
                print cd.inputVs[4]
                r_t = self.assess(isensor, cd.inputVs, adjustDecayTime, adjustRef)

                ### check the results
                if r_t and r_t[1]-r[1]<-0.002 and r_t[3]<r[3]:
                    r = r_t
                else:
                    cd.inputVs = inputVs_t
                    Error(tname, "Failed to reduce r[3], reverting...")
            elif r[2]<self.tuneRef[2]:
                print '-----r[2]=', r[2], cd.voltsNames[4], ':',cd.inputVs[4],'->',
                cd.inputVs[4] -= 0.01
                print cd.inputVs[4]
                r_t = self.assess(isensor, cd.inputVs, adjustDecayTime, adjustRef)

                ### check the results
                if r_t and r_t[1]-r[1]<-0.002 and r_t[2]>r[2]:
                    r = r_t
                else:
                    cd.inputVs = inputVs_t
                    Error(tname, "Failed to increase r[2], reverting...")


        return r

    def scanForStructure(self, chan=18, xtag=''):
        self.sTag = "sfs_"+xtag+str(chan)+'_'

        for vdis in range(9):
            for vref in range(10):
                cd = self.sensorConfig.cd
                cd.currentSensor = chan
                cd.readBackPars(chan)
                cd.inputVs[4] = 1.+0.1*vdis
                cd.inputVs[5] = 2.+0.1*vref

                x0 = self.assess(adjustDecayTime=0, adjustRef=False)
    def scanForStructure2(self, chan=18, xtag=''):
        self.sTag = "sfs_"+xtag+str(chan)+'_'

        for vref in range(10):
            for vdis in range(9):
                cd = self.sensorConfig.cd
                cd.currentSensor = chan
                cd.readBackPars(chan)
                cd.inputVs[4] = 1.+0.1*vdis
                cd.inputVs[5] = 2.+0.1*vref

                x0 = self.assess(adjustDecayTime=0, adjustRef=False)



    def scan(self):
        '''Scan the given range with given steps'''

        pass

    def smartScan(self):
        '''Increase the number of points denpending on the situation'''
        pass

    def tryExisting(self):
        '''Try the existing parameters'''
        isendor = cd.currentSensor
#         currentValues = 
#         for i in range(len(cd.sensorVcodes)):
#             print i, [cd.tms1mmReg.dac_code2volt(vx) for vx in cd.sensorVcodes[i]]

        pass

    def tune2(self, chan):
        self.sTag = "plot_{0:d}_".format(chan)

        cd = self.sensorConfig.cd
        cd.currentSensor = chan
        cd.readBackPars(chan) 

        print "starting with pars:", cd.inputVs
        ### check it
#         x0 = self.assess(adjustDecayTime=0, adjustRef=False)
        x0 = self.assess()
        self.gainRef = x0[1]

        inputVs0 = cd.inputVs[:]
        for i in range(cd.nCh):
            if cd.isGood[i]:
                cd.sensorVcodes[chan] = cd.sensorVcodes[i][:]
#                 xi = self.assess(adjustDecayTime=0, adjustRef=False)
                xi = self.assess()
                if xi[1]>self.gainRef:
                    cd.readBackPars(chan)
                    self.gainRef = xi[1]
                    print "find better starting point:", cd.inputVs, 'with gain:',self.gainRef
                    if self.logFile: self.logFile.write('# new base\n')
                else:
                    cd.sensorVcodes[chan] = inputVs0
                    print "worse gain:", xi[1], "going back to the old one"

        ### first step: get high gain with loose shape requirement
        ### scan all parameters execpt VDIS
        self.tuneRef = [0.6, -1, 0.2, 0.1] ## loose requirement for high gain
#         changeList = [0.001, 0.001, 0.003, 0.005, 0.02, 0.03, 0.05, 0.2, 0.3, 0.5]
        changeList = [0.001, 0.001, 0.002, 0.003, 0.005, 0.02, 0.03, 0.05, 0.1, 0.1, 0.1,0.1, 0.1, 0.1, 0.2]
        tunePars = [5,1,2,0,3]

        updated = True
        tuned = []
        tuneVref = (5 not in tunePars)
        for ipar in growList(tunePars):
            if ipar == -1: break ### reach the end of the list
            print "===> Start tune", cd.voltsNames[ipar]
          
            ### find the best point
            updated = False
            while True:
                direction = 0
                inputVs0 = cd.inputVs[:]
                while direction == 0:
                    print '------', cd.voltsNames[ipar], '[U]:',cd.inputVs[ipar],'->',
                    for d in changeList:
                        cd.inputVs[ipar] += d
                        if(cd.inputVs[ipar]>3): break
                        print cd.inputVs[ipar],
                        x1 = self.assess(adjustRef=tuneVref)
                        if x1 is None: continue
                        print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
                        print x0, x1, self.gainRef
                        if abs(x1[1]-self.gainRef)>0.001: break
                    if (x1 is None) or x1[1]<self.gainRef+0.0008:
                        cd.inputVs = inputVs0
                        print 'reverting...'
                        break
                    x0 = x1
                    self.gainRef = x0[1]
                    print 'Good. Moving on...'
                    if self.logFile: self.logFile.write('# new base\n')
                    direction = 1
                inputVs0 = cd.inputVs[:]
                while direction == 0:
                    print '------', cd.voltsNames[ipar], '[D]:',cd.inputVs[ipar],'->',
                    for d in changeList:
                        cd.inputVs[ipar] -= d
                        if(cd.inputVs[ipar]<0): break
                        print cd.inputVs[ipar],
                        x1 = self.assess(adjustRef=tuneVref)
#                         x1 = self.assess()
                        if x1 is None: continue
                        print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
                        print x0, x1, self.gainRef
                        if abs(x1[1]-self.gainRef)>0.001: break
                    if (x1 is None) or x1[1]<self.gainRef+0.0008:
                        cd.inputVs = inputVs0
                        print 'reverting...'
                        break
                    x0 = x1
                    self.gainRef = x0[1]
                    print 'Good. Moving on...'
                    if self.logFile: self.logFile.write('# new base\n')
                    direction = -1
                if direction != 0:
                    updated = True
                else: break

            ### redo other parameters if 
            if updated:
                tunePars += tuned ### if the parameter changed, the tuned ones need to be revisited
                tuned = []
            else:
                tuned.append(ipar)

        print "gain tune done:", cd.inputVs
#         x1 = self.assess()
#         print x1
#         print ['{0:.3f}'.format(x) for x in cd.inputVs]
        print "------------------------"
 
#         ### second step: tune the [VDIS, VREF, VCASN, VBIASN] with loose gain requirement
#         self.tuneRef = [0.6, -1, 0.4, 0.05] ## loose requirement for high gain
# #         changeList = [0.001, 0.001, 0.003, 0.005, 0.02, 0.03, 0.05, 0.2, 0.3, 0.5]
#         changeList = [0.001, 0.001, 0.002, 0.003, 0.005, 0.02, 0.03, 0.05, 0.1, 0.1, 0.1,0.1, 0.1, 0.1, 0.2]
#         tunePars = [4,0,2,5]
# 
#         updated = True
#         tuned = []
#         tuneVref = (5 in tunePars)
#         tuneDT = 0 if 4 in tunePars else 10
#         for ipar in growList(tunePars):
#             if ipar == -1: break ### reach the end of the list
#             print "===> Start tune", cd.voltsNames[ipar]
#           
#             ### find the best point
#             updated = False
#             while True:
#                 direction = 0
#                 inputVs0 = cd.inputVs[:]
#                 while direction == 0:
#                     print '------', cd.voltsNames[ipar], '[U]:',cd.inputVs[ipar],'->',
#                     for d in changeList:
#                         cd.inputVs[ipar] += d
#                         if(cd.inputVs[ipar]>3): break
#                         print cd.inputVs[ipar],
#                         x1 = self.assess(adjustDecayTime=tuneDT, adjustRef=tuneVref)
#                         if x1 is None: continue
#                         print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
#                         print x0, x1, self.gainRef
#                         if abs(x1[1]-self.gainRef)>0.001: break
#                     if (x1 is None) or x1[1]<x0[1]+0.0008:
#                         cd.inputVs = inputVs0
#                         print 'reverting...'
#                         break
#                     x0 = x1
#                     self.gainRef = x0[1]
#                     print 'Good. Moving on...'
#                     if self.logFile: self.logFile.write('# new base\n')
#                     direction = 1
#                 inputVs0 = cd.inputVs[:]
#                 while direction == 0:
#                     print '------', cd.voltsNames[ipar], '[D]:',cd.inputVs[ipar],'->',
#                     for d in changeList:
#                         cd.inputVs[ipar] -= d
#                         if(cd.inputVs[ipar]<0): break
#                         print cd.inputVs[ipar],
#                         x1 = self.assess(adjustDecayTime=tuneDT, adjustRef=tuneVref)
# #                         x1 = self.assess()
#                         if x1 is None: continue
#                         print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
#                         print x0, x1, self.gainRef
#                         if abs(x1[1]-self.gainRef)>0.001: break
#                     if (x1 is None) or x1[1]<x0[1]+0.0008:
#                         cd.inputVs = inputVs0
#                         print 'reverting...'
#                         break
#                     x0 = x1
#                     self.gainRef = x0[1]
#                     print 'Good. Moving on...'
#                     if self.logFile: self.logFile.write('# new base\n')
#                     direction = -1
#                 if direction != 0:
#                     updated = True
#                 else: break
# 
#             ### redo other parameters if 
#             if updated:
#                 tunePars += tuned ### if the parameter changed, the tuned ones need to be revisited
#                 tuned = []
#             else:
#                 tuned.append(ipar)

        print "final:", cd.inputVs
        x1 = self.assess(adjustDecayTime=0, adjustRef=False)
        print x1
        print ['{0:.3f}'.format(x) for x in cd.inputVs]

    def tune(self, chan):
        ## give a set of parameters and get a quantity of goodness
        ### pass the parameters and get data
        ### assess the data -- what's good? What's better?
        ## Move the next set of parameters
        cd = self.sensorConfig.cd
        cd.currentSensor = chan
        cd.readBackPars(chan) 
#         cd.inputVs = [1.029,1.106,1.676,1.169,0.8,2.99]

        print "starting with pars:", cd.inputVs
        ### check it
        x0 = self.assess()
        self.gainRef = x0[1]

        ## tune the first four VDIS for higher gain
        tuned = []
        px = [None]*6 ## to save the results of the 6 parameters
        mx = 0
        updated = True
        changeList = [0.001, 0.001, 0.003, 0.005, 0.02, 0.03, 0.05, 0.2, 0.3, 0.5]
        tunePars = [5,1,2,0,3]

        for ipar in growList(tunePars):
            if ipar == -1: break ### reach the end of the list
            print "===> Start tune", cd.voltsNames[ipar]
          
            ### find the best point
            updated = False
            while True:
                direction = 0
                inputVs0 = cd.inputVs[:]
                while direction == 0:
                    print '------', cd.voltsNames[ipar], '[U]:',cd.inputVs[ipar],'->',
                    for d in changeList:
                        cd.inputVs[ipar] += d
                        if(cd.inputVs[ipar]>3): break
                        print cd.inputVs[ipar],
                        x1 = self.assess()
                        if x1 is None: continue
                        print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
                        print x0, x1, self.gainRef
                        if abs(x1[1]-self.gainRef)>0.001: break
                    if (x1 is None) or x1[1]<x0[1]+0.0008:
                        cd.inputVs = inputVs0
                        print 'reverting...'
                        break
                    x0 = x1
                    self.gainRef = x0[1]
                    print 'Good. Moving on...'
                    direction = 1
                inputVs0 = cd.inputVs[:]
                while direction == 0:
                    print '------', cd.voltsNames[ipar], '[D]:',cd.inputVs[ipar],'->',
                    for d in changeList:
                        cd.inputVs[ipar] -= d
                        if(cd.inputVs[ipar]<0): break
                        print cd.inputVs[ipar],
                        x1 = self.assess()
                        if x1 is None: continue
                        print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
                        print x0, x1, self.gainRef
                        if abs(x1[1]-self.gainRef)>0.001: break
                    if (x1 is None) or x1[1]<x0[1]+0.0008:
                        cd.inputVs = inputVs0
                        print 'reverting...'
                        break
                    x0 = x1
                    self.gainRef = x0[1]
                    print 'Good. Moving on...'
                    direction = -1
                if direction != 0:
                    updated = True
                else: break

            ### redo other parameters if 
            if updated:
                tunePars += tuned ### if the parameter changed, the tuned ones need to be revisited
            else:
                tuned.append(ipar)

        print "final:", cd.inputVs
        x1 = self.assess()
        print x1
        print ['{0:.3f}'.format(x) for x in cd.inputVs]

    def handTune(self, chan):
        self.sensorConfig.cd.currentSensor = chan
        inputVs = None
        while True:
            ### check it
            x0 = self.assess(None, inputVs)
            print x0
            args = raw_input("inputVs:")
            if args in ['e','q','exit','quit','.q']:
                break
            inputVs = [float(x) for x in args.split(',')]

    def test(self):
        print "testing"
        dat1 = None
        ichan = 5 if len(sys.argv)<2 else int(sys.argv[1])
        with open('adc_test.dat') as f1:
            dat1 = [float(l.split()[ichan]) for l in f1.readlines() if l.find('#')==-1]
#         a1 = SigInfo(dat1)
        a1 = SigInfo()
        print a1.getQuickInfo(dat1, 20)
#         self.get_score(dat1)
#         self.check(dat1)

    def fullTune(self):
        '''Do everything automatically'''
        ### First find the initial values for fine tune
        ### Dead channels will be marked
        self.getInitialValues()

        ### Continue with the fine tune
        ## Could be done in prallel in future
        nChan = 19 # number of channels
        for i in range(nChan):
            # don't waste time on the dead ones
            if self.isDead[i]: continue
            self.tune2(i)

        ### Finish. The output is a list of parameters and the characteristics
        ### Where to save the output? Inside the class, or return from this method? -- save to the method.

    def compareInputs(self, chan, inputs, dt=10, info=None, saveName='testing'):
        '''Compare a list of inputs
        Each input is a tuple: (tag, tex, [pars]), tex will be shown in the legend and tag should plain text used to distinguish the entry.
        For each entry, a TGraph will be made.
        '''
        cd1 = self.sensorConfig.cd

        grs = []
        dataX = []
        ic = 1
        max0 = -1
        min0 = 999
        lg = TLegend(0.7,0.8,0.9,0.9)
        lg.SetFillStyle(0)

        for ip in inputs:
            cd1.updatePars(chan, ip[2])
            print ip[2]
            self.sensorConfig.update_sensor(chan)
            print("Checking:", cd1.currentSensor, cd1.inputVs)
            time.sleep(dt)
            cd1.fetch()
#             dataX.append(cd1.adcData[chan][:])
            dataX = cd1.adcData[chan][:]
            for i in range(10): print dataX[i]

#             ndata = len(dataX[-1])
#             gr1 = TGraph(ndata, array('d',[i*0.2*0.001 for i in range(ndata)]), array('d', dataX[-1]))
            ndata = len(dataX)
            gr1 = TGraph(ndata, array('d',[i*0.2*0.001 for i in range(ndata)]), array('d', dataX))
            gr1.SetLineColor(ic)
            gr1.SetMarkerColor(ic)
            gr1.SetMarkerStyle(20+ic)
            ic += 1

            lg.AddEntry(gr1, ip[1],'lp')

            grs.append(gr1)

#             max0 = max([max0, max(dataX[-1])])
#             min0 = min([min0, min(dataX[-1])])
            max0 = max([max0, max(dataX)])
            min0 = min([min0, min(dataX)])

#             gr1.Draw("AP")
#             waitRootCmdX()

        gr0 = grs[0]
        gr0.Draw("AP")
        dm = max0 - min0
        h1 = gr0.GetHistogram()
        h1.GetYaxis().SetRangeUser(min([min0*0.8,min0-0.1*dm]), max([max0*1.2,max0+0.1*dm]))
        h1.GetXaxis().SetTitle("t [ms]")
        h1.GetYaxis().SetTitle("V_{out} [V]")
        for gr in grs[1:]: gr.Draw("Psame")
        h1.Draw('axissame')

        lg.Draw()

        if info:
            self.lt.DrawLatexNDC(0.2,0.8, info)

        waitRootCmdX(self.sDir+self.sTag+saveName, self.autoSave)

def testCompare():
    qt1 = QuickTuner(mode=0)
    qt1.sTag = 'aliveTest_'
    qt1.autoSave = False

    inputs = [('l2','VBIASN=0.1, VREF=2.9',[0.1, 1.546, 1.626, 1.169, 1.357, 2.9])
             ,('l2','VBIASN=1.379, VREF=2.9',[1.379, 1.546, 1.626, 1.169, 1.357, 2.9])
             ,('l1','VBIASN=1.379, VREF=2.458',[1.379, 1.546, 1.626, 1.169, 1.357, 2.458])
             ]

    qt1.compareInputs(1, inputs, 10, "P1: 1.546, 1.626, 1.169, 1.357","P1")
    qt1.compareInputs(7, inputs, 10, "P7: 1.546, 1.626, 1.169, 1.357","P7")
    qt1.compareInputs(0, inputs, 10, "P0: 1.546, 1.626, 1.169, 1.357","P0")
    qt1.compareInputs(15, inputs, 10, "P15: 1.546, 1.626, 1.169, 1.357","P15")
    qt1.compareInputs(16, inputs, 10, "P16: 1.546, 1.626, 1.169, 1.357","P16")
    qt1.compareInputs(17, inputs, 10, "P17: 1.546, 1.626, 1.169, 1.357","P17")
    qt1.compareInputs(10, inputs, 10, "P10: 1.546, 1.626, 1.169, 1.357","P10")
    qt1.compareInputs(9, inputs, 10, "P9: 1.546, 1.626, 1.169, 1.357","P9")
    qt1.compareInputs(2, inputs, 10, "P2: 1.546, 1.626, 1.169, 1.357","P2")


def takeSamples():
    qt1 = QuickTuner(mode=0)
    cd1 = qt1.sensorConfig.cd

    dataX = []
    for i in range(10*15): # 15 min
        time.sleep(6)
        cd1.fetch()
        cd1.saveData("TS/TSa_"+str(i))
        cd1.fetch()
        cd1.saveData("TS/TSb_"+str(i))

def checkStablibity(isensor=8):
    qt1 = QuickTuner(mode=0)
    cd1 = qt1.sensorConfig.cd
    cd1.readBackPars(isensor)

    dataX = []
    for i in range(10):
        time.sleep(1)
        cd1.fetch()
        dataX.append(cd1.adcData[isensor][:])

    max1 = -1
    min1 = 999
    ndata = len(dataX[0])
    gr0 = None
    option = 'AL'
    icolor = 1
    grs = []
    for x in dataX:
        max2 = max(x)
        if max2>max1: max1 = max2
        min2 = min(x)
        if min2<min1: min1 = min2

        gr1 = TGraph(ndata, array('d',[i*0.2*0.001 for i in range(ndata)]), array('d', x))
        gr1.Draw(option)
        if gr0 == None:
            gr0 = gr1
            option = 'L'
        gr1.SetLineColor(icolor)
        icolor += 1
        grs.append(gr1)
#         waitRootCmdX()

    h1 = gr0.GetHistogram()
    print min1, max1
    h1.GetYaxis().SetRangeUser(min1,max1)
    h1.GetYaxis().SetTitle("V")
    h1.GetXaxis().SetTitle("t [ms]")
    h1.Draw("axissame")

    lt = TLatex()
    lt.DrawLatexNDC(0.2,0.92, "C{0:d}: ".format(isensor)+' '.join(['{0:.3f}'.format(x) for x in cd1.inputVs]))

    waitRootCmdX()
    print len(dataX), len(grs)

def checkPlot():
    ### get data
    ### show
    ichan = 12
    dat1 = None
    with open('sample_0_adc.dat') as f1:
        dat1 = [float(l.split()[ichan]) for l in f1.readlines() if l.find('#')==-1]
    a1 = SigInfo()

    print sDirectly, a1.autoSave
    a1.showMore(dat1)


def test():
    qt1 = QuickTuner(mode=0)
    lg.info("testing!")
#     qt1.test()
#     return

    cd1 = qt1.sensorConfig.cd
#     cd1.inputVs = [1.029,1.106,1.676,1.169,0.8,2.99]
#     cd1.inputVs = [1.151, 0.746, 1.226, 1.409, 1.46, 2.55]
    print qt1.sensorConfig.cd.inputVs
#     print qt1.assess()
#     qt1.setupLogFile("T_P15_Nov29.log")
#     qt1.tune2(15)
    qt1.setupLogFile("T_P0_Nov30.log")
    qt1.tune2(0)
#     qt1.setupLogFile("sfs_P0_Nov30.log")
#     qt1.scanForStructure2(0, "22pm50a_")
#     qt1.setupLogFile("sfs_P18_Nov30.log")
#     qt1.scanForStructure2(18, "22pm50a_")
#     qt1.setupLogFile("T_P18_Nov28.log")
#     qt1.setupLogFile("T_P2_Nov30.log")
#     qt1.tune2(2)
#     qt1.handTune(5)

def scanY(chans=[i for i in range(19)]):
    '''Used to test the scan of one or more parameters'''
    nChips = 19 # the magic number
    nChan = len(chans)

    iP = 1
    cd = CommonData()
    cd.setupConnection()
    sc1 = SensorConfig(cd)

    ### get list of chains to be updated
    chains = set([sc1.tms1mmX19chainSensors[sc1.tms1mmX19sensorInChain[c]][0] for c in chans])

    xj = open('scan_out_v2.ttl','w')

    nP = 10
    ranges = [range(11), range(10,-1,-1)]
    for iN in range(11):
        for iP in ranges[iN%2]:
            print iN,iP
            for chan in chans:
                cd.readBackPars(chan)
                cd.inputVs[0] = iN*0.33
                cd.inputVs[1] = iP*0.33
#                 print cd.inputVs
                cd.updatePars(chan, None, False)

            for c in chains: sc1.update_sensor(c)
            time.sleep(2)
            cd.fetch()

            for ic in range(len(chans)):
                chan = chans[ic]
                cd.readBackPars(chan)
#                 print cd.inputVs

                m,v = getMeanVar(cd.adcData[chan])
                print ' '.join([str(x) for x in [chan, m, v]+cd.inputVs])
                xj.write(' '.join([str(x) for x in [chan, iN, iP, m, v]+cd.inputVs])+'\n')

def scanX(chans=[i for i in range(19)]):
    '''Used to test the scan of one or more parameters'''
    nChips = 19 # the magic number
    nChan = len(chans)

    iP = 1
    fixedPars = [1.5, 1.5]
    cd = CommonData()
    cd.setupConnection()
    inputs = cd.inputVs
    sc1 = SensorConfig(cd)

    ### setup the style list
    mkColors = [2,3,4,6,7,8]
    mkMarkers = [20,25,23,26,21,22,24,27,32]
    styleList = [(None,None)]*nChips
    for i,j in sc1.tms1mmX19chainSensors.iteritems():
        for k,l in enumerate(j):
            styleList[l] = (mkColors[i],mkMarkers[k])

    ### get list of chains to be updated
    chains = set([sc1.tms1mmX19chainSensors[sc1.tms1mmX19sensorInChain[c]][0] for c in chans])
    print chains

    ### setup the elements for plotting 
    lg = TLegend(0.84,0.11,0.998,0.89)
    lg.SetFillStyle(0)

    grs = [TGraphErrors() for chan in chans]
    for ic in range(len(chans)):
        chan = chans[ic]
        grs[ic].SetMarkerColor(styleList[chan][0])
        grs[ic].SetLineColor(styleList[chan][0])
        grs[ic].SetMarkerStyle(styleList[chan][1])
        lg.AddEntry(grs[ic],str(chan),'lp')

    ### variables to store the results
    pValues = [None]*nChan
    changeP = [(None,None)]*nChan ## save (where, how_large) for each channel

    ### perform the scan
    max1 = -1
    min1 = 999
    for ir in range(11): ## run ir
        vr = 0.33*ir
        ### update channels
        for chan in chans:
            cd.readBackPars(chan)
            for f in range(len(fixedPars)):
                if fixedPars[f] is not None: inputs[f] = fixedPars[f]

            inputs[iP] = vr
            cd.updatePars(chan, inputs, False)

        for c in chains: sc1.update_sensor(c)
        time.sleep(2)
        cd.fetch()

#         x = ''
#         while x!='m':
#             cd.fetch()
#             a1 = SigInfo()
#             a1.showMore(dat1)
#             x = raw_input("'m' to move to next|")

        for ic in range(len(chans)):
            chan = chans[ic]
            m,v = getMeanVar(cd.adcData[chan])
            if m+v>max1: max1 = m+v
            if m-v<min1: min1 = m-v
            print chan, m,v
            grs[ic].SetPoint(ir, vr, m)
            grs[ic].SetPointError(ir, 0, v)

            ### get the values
            if pValues[ic] is not None:
                if (changeP[ic][1] is None) or (m - pValues[ic] < changeP[ic][1]):
                    changeP[ic] = (ir, m - pValues[ic])
            pValues[ic] = m

    gr1 = grs[0]
    print gr1.GetN()
    gr1.Draw("APL")
    h1 = gr1.GetHistogram()
    h1.GetXaxis().SetTitle(cd.voltsNames[iP]+' [V]')
    h1.GetYaxis().SetTitle('V_{out} [V]')
    dm = 0.05*(max1-min1)    
    h1.GetYaxis().SetRangeUser(min1-dm,max1+dm)

    for gr in grs[1:]: gr.Draw("PLsame")
    lg.Draw("same")


    ### add info of other parameters
    inputT = ''
    for i,x in enumerate(fixedPars):
        if i == iP: continue
        if x is not None: inputT += cd.voltsNames[i]+'='+str(x)
    lt = TLatex()
    lt.DrawLatexNDC(0.2,0.92,' '.join(inputT))

#     inputT = ['{0:.3f}'.format(x) for x in inputs]
#     inputT[iP] = '--'
#     lt.DrawLatexNDC(0.2,0.92,' '.join(inputT))

    for x in changeP: print x

    waitRootCmdX()

def zrange(a,b):
    d = 1 if a<b else -1
    p = a
    while p!=b:
        yield p
        p += d

def getPars():
    fname = '/home/dzhang/links/cernbox/temp/scan_out_v2.ttl' 
    lines = None
    with open(fname) as f1:
        lines = [l.rstrip().split() for l in f1.readlines() if len(l.rstrip().split())>3]

    ### 11x11 for iN x iP
    ### now let's find the vlaues
    iC = 5
    i = 0

    ### for each row, we get the max difference and whrere the max change happens
    pars = None
    lxJ = []
    while True:
        l1 = [x for x in lines if int(x[0])==iC and int(x[1])==i]
        i += 1
        if len(l1)==0: break

        kx = [float(j[3]) for j in l1]
        print kx
        imax, fmax = max(enumerate(kx), key=lambda p:p[1])
        imin, fmin = min(enumerate(kx), key=lambda p:p[1])
        print imax, imin, fmax, fmin

        d = 1 if imin<imax else -1
        imx = imin
        dmx = 0
        for j in range(imin, imax, d):
            if kx[j+d]-kx[j]>dmx:
                dmx = kx[j+d]-kx[j]
                imx = j
        print '-'*20
        print imx, dmx
        lxJ.append((imx, dmx, fmax-fmin))
    for t in lxJ: print t

def scanV():
    ### test

if __name__ == '__main__':
    savehistory('./')
    gStyle.SetOptTitle(0)
    gStyle.SetNdivisions(506,'XYZ')
#     gStyle.SetPadTickX(1);
#     gStyle.SetPadTickY(1);
    gStyle.SetLegendBorderSize(0);
#     scanY()
    getPars()
# 
#     checkPlot()
#     takeSamples()
#     checkStablibity(5)
#     test()
#     testCompare()
