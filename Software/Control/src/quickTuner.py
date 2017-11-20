#!/usr/bin/env python
import socket
from TMS1mmX19Tuner import CommonData, SensorConfig
from command import *
from math import sqrt
from rootUtil import waitRootCmdX
from ROOT import TGraph, TLatex, gPad, gStyle
from array import array
import sys, time
import logging as lg


isDebug = False
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
        g0.GetHistogram().GetYaxis().SetRangeUser(0.9, 1.4)

        if info: self.lt.DrawLatexNDC(0.2,0.8,info)
        if info2: self.lt.DrawLatexNDC(0.2,0.93,info2)

        global plot_count
        print plot_count
        plot_count += 1
        print plot_count

        gPad.Update()
        waitRootCmdX("plot_"+str(plot_count), True)

    def getQuickInfo(self, data, n1=500, n2=2000, np=20):
        '''Get some useful infomation quickly'''
        maxI, mx = max(enumerate(data[:-n2+np]), key=lambda p:p[1])
        minI, mn = min(enumerate(data[:-n2+np]), key=lambda p:p[1])
        dx = 0.5*(mx-mn)
        dn1 = sum(data[maxI+n1:maxI+n1+np])/np
        dn2 = sum(data[maxI+n2:maxI+n2+np])/np
#         dn1 = max(data[maxI+n1:maxI+n1+np])
#         dn2 = max(data[maxI+n2:maxI+n2+np])
        print mx, dn1, dn2, dx,


        ## we want large dx, large #2 and small #3
        return (0.5*(mx+mn), dx, 1-(mx-dn1)/dx, 1-(mx-dn2)/dx)

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

class QuickTuner:
    def __init__(self, mode=0):
        self.mode = mode # 0: normal, 1: testing
        self.sensorConfig = None
        self.showPlot = True

        self.setup()

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

        cd.updatePars(5, [1.149, 0.746, 1.226, 1.409, 1.82, 2.85])
        cd.updatePars(6, [1.379, 1.146, 1.426, 1.169, 1.52, 2.758])

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
    def assess(self,  isensor=None, inputVs=None, adjustDecayTime=10, adjustRef=True):
        cd = self.sensorConfig.cd
        cd.updatePars(isensor, inputVs)

        isensor = cd.currentSensor
        self.sensorConfig.update_sensor(isensor) 
        print("Checking:", isensor, cd.inputVs)

        ### get new data
        time.sleep(3)
        data = cd.adcData[isensor]
        a1 = SigInfo()

        r = (0,0,0,0)
        nTest = 5
        if self.mode==0:
            var = 99
            nTried = 0
            while nTried<4:
                rAva = []
                rL = [0,0,0,0]
                for k in range(nTest):
                    cd.fetch()
                    r = a1.getQuickInfo(data)
                    rAva.append(r[1])
                    for i in range(len(r)): rL[i] += r[i]/nTest
                mu,var = getMeanVar(rAva)
                print mu, var
                r = tuple(rL)
                if var<0.002:
                    print "Convereged."
                    break

                print "Not stable"
                nTried += 1 

        print "temp results: r=", r
        if self.showPlot:
            a1.show(data, "A={0:.4f}".format(r[1]),', '.join(['{0:.3f}'.format(x) for x in cd.inputVs]))

        if adjustDecayTime and r[1]>0.005:
            adjustDecayTime -= 1
            if r[2]<0.25:
                print '-----r[2]=', r[2], cd.voltsNames[4], ':',cd.inputVs[4],'->',
                cd.inputVs[4] -= 0.01
                print cd.inputVs[4]
                r = self.assess(isensor, cd.inputVs, adjustDecayTime, adjustRef)
            elif r[3]>0.1:
                print '-----r[3]=', r[3], cd.voltsNames[4], ':',cd.inputVs[4],'->',
                cd.inputVs[4] += 0.01
                print cd.inputVs[4]
                r = self.assess(isensor, cd.inputVs, adjustDecayTime, adjustRef)

        if adjustRef:
            if r[0]+r[1]>1.25:
                print '-----r[0]=', r[0], cd.voltsNames[5], ':',cd.inputVs[5],'->',
                cd.inputVs[5] -= 0.01
                print cd.inputVs[5]
                r = self.assess(isensor, cd.inputVs, adjustDecayTime, True)
            elif r[0]<0.7 and cd.inputVs[5]<2.99:
                print '-----r[0]=', r[0], cd.voltsNames[5], ':',cd.inputVs[5],'->',
                cd.inputVs[5] += 0.01
                print cd.inputVs[5]
                r = self.assess(isensor, cd.inputVs, adjustDecayTime, True)

        return r

    def tune(self, chan):
        ## give a set of parameters and get a quantity of goodness
        ### pass the parameters and get data
        ### assess the data -- what's good? What's better?
        ## Move the next set of parameters
        cd = self.sensorConfig.cd
        cd.currentSensor = chan
#         cd.inputVs = [1.029,1.106,1.676,1.169,0.8,2.99]

        print "starting with pars:", cd.inputVs
        ### check it
        x0 = self.assess()

        ## tune the first four VDIS for higher gain
        tuned = []
        px = [None]*6 ## to save the results of the 6 parameters
        mx = 0
        updated = True
        changeList = [0.002, 0.003, 0.005, 0.02, 0.03, 0.05, 0.2, 0.3, 0.5]
        tunePars = [1,2,0,3]

        for ipar in growList(tunePars):
            if ipar == -1: break ### reach the end of the list
            
            direction = 0
            inputVs0 = cd.inputVs[:]
            print "===> Start tune", cd.voltsNames[ipar]
            while True:
                print '------', cd.voltsNames[ipar], '[U]:',cd.inputVs[ipar],'->',
                for d in changeList:
                    cd.inputVs[ipar] += d
                    print cd.inputVs[ipar],
                    x1 = self.assess()
                    print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
                    if abs(x1[1]-x0[1])>0.001: break
                if x1[1]<x0[1]:
                    cd.inputVs = inputVs0
                    print 'reverting...'
                    break
                x0 = x1
                print 'Good. Moving on...'
                direction = 1
            while direction == 0:
                print '------', cd.voltsNames[ipar], '[D]:',cd.inputVs[ipar],'->',
                for d in changeList:
                    cd.inputVs[ipar] -= d
                    print cd.inputVs[ipar],
                    x1 = self.assess()
                    print "dx=", cd.inputVs[ipar]-inputVs0[ipar],", dA=", x1[1]-x0[1],
                    if abs(x1[1]-x0[1])>0.001: break
                if x1[1]<x0[1]:
                    cd.inputVs = inputVs0
                    print 'reverting...'
                    break
                x0 = x1
                print 'Good. Moving on...'
                direction = -1

            if direction:
                tunePars += tuned ### if the parameter changed, the tuned ones need to be revisited
            else:
                tuned.append(ipar)
                
        print "final:", cd.inputVs
        x1 = self.assess()
        print x1

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
    qt1.tune(8)
#     qt1.handTune(5)

if __name__ == '__main__':
    gStyle.SetOptTitle(0)
    test()
