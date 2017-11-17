#!/usr/bin/env python
import socket
from TMS1mmX19Tuner import CommonData, SensorConfig
from command import *
from math import sqrt
from rootUtil import waitRootCmdX
from ROOT import TGraph
from array import array
import sys, time

isDebug = False


def checkNSeq(d, n, i, v):
    nd = len(d)
    for j in range(n, n+i):
        if j>nd or j<0: return False

class SigInfo:
    def __init__(self, data=None):
        self.resp = [] # [(t0, dT, tM, A),]
        if data:
            self.extract(data)
        else:
            self.bkgMu = None
            self.bkgVar = None
            self.quality = None
    def show(self, data):
        x = [0.2*i for i in range(len(data))]
        g0 = TGraph(len(data), array('d',x), array('d',data))
        g0.Draw("AP")
        g0.GetHistogram().GetYaxis().SetTitle("V_{out} [V]")
        g0.GetHistogram().GetXaxis().SetTitle("t [#mus]")

        waitRootCmdX()

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

        self.setup()

    def setup(self):
        ### get connected
        data_ip_port = "192.168.2.3:1024"
        control_ip_port = "192.168.2.3:1025"
        dataIpPort = data_ip_port.split(':')
        sD = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        ctrlIpPort = control_ip_port.split(':')
        sC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        if self.mode == 0:
            sD.connect((dataIpPort[0],int(dataIpPort[1])))
            sC.connect((ctrlIpPort[0],int(ctrlIpPort[1])))

        cmd = Cmd()
        cd = CommonData(cmd, dataSocket=sD, ctrlSocket=sC)
        cd.aoutBuf = 1 
        cd.x2gain = 2
        cd.sdmMode = 0
        cd.bufferTest = 0

        self.sensorConfig = SensorConfig(cd)
        pass

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

    def assess(self,  isensor=None, inputVs=[1.379, 1.546, 1.626, 1.169, 1.357, 2.458]):
        cd = self.sensorConfig.cd
        cd.updatePars(isensor, inputVs)

        isensor = cd.currentSensor
        self.sensorConfig.update_sensor(isensor) 

        ### Tips:
        ## 1. Wait for a while to see the stable results, unless you want to catch the transation period
        ## 2. grab the data for several times to see if it's stable already
        ## 3. While checking the results, we can already aquire new data -- so put the tune code to a seperate thread?

        ### get new data
        time.sleep(3)
        a1 = SigInfo()
        if self.mode==0:
            x = "x"

            ### loop until it becomes stable
            while x != 'n':
                cd.fetch()
                a1.show(cd.adcData[isensor])
                x = raw_input("n: for next point")
            a1.extract(cd.adcData[isensor])

#             for i in range(20):
#                 cd.fetch()
#                 cd.saveData('test{0:d}_'.format(i))
# #                 a1.extract(cd.adcData[isensor])
#                 a1.show(cd.adcData[isensor])

        ### evaluate the score
#         get_score(self.cd.adcData)

        return a1.quality

    def tune(self, chan):
        ## give a set of parameters and get a quantity of goodness
        ### pass the parameters and get data
        ### assess the data -- what's good? What's better?
        ## Move the next set of parameters
        cd = self.sensorConfig.cd
        cd.currentSensor = chan
        cd.inputVs = [1.029,1.106,1.676,1.169,0.8,2.99]

        ax = []
        for i in range(20):
            cd.inputVs[0] = 1.029 - 0.1 + 0.01*i
#             print cd.inputVs
            ax.append((cd.inputVs[:], self.assess()))
            print ax[-1]

        for j in ax:
            print j[0],':',j[1]

        ### do the tunes here
        ## change the value and compare the quality


    def test(self):
        print "testing"
        dat1 = None
        ichan = 5 if len(sys.argv)<2 else int(sys.argv[1])
        with open('adc_test.dat') as f1:
            dat1 = [float(l.split()[ichan]) for l in f1.readlines() if l.find('#')==-1]
        a1 = SigInfo(dat1)
#         self.get_score(dat1)
#         self.check(dat1)

def test():
    qt1 = QuickTuner(mode=0)
    cd1 = qt1.sensorConfig.cd
    cd1.inputVs = [1.029,1.106,1.676,1.169,0.8,2.99]
    print qt1.sensorConfig.cd.inputVs
#     qt1.assess()
    qt1.tune(5)
#     qt1.test()

if __name__ == '__main__':
    test()
