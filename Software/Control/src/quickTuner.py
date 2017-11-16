#!/usr/bin/env python
import socket
from TMS1mmX19Tuner import CommonData, SensorConfig
from command import *
from math import sqrt
from rootUtil import waitRootCmdX
from ROOT import *
from array import array
import sys

isDebug = True


def checkNSeq(d, n, i, v):
    nd = len(d)
    for j in range(n, n+i):
        if j>nd or j<0: return False

class sigInfo:
    def __init__(self, data=None):
        self.resp = [] # [(t0, dT, tM, A),]
        if data:
            self.extract(data)
        else:
            self.bkgMu = None
            self.bkgVar = None
            self.quality = None
    def extract(self, data):
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
        self.quality = max([abs(x[3]) for x in self.resp])
#         mx = max(self.resp, key=lambda p:abs(p[3]))
#         self.resp = [x for x in self.resp if abs(x[3])>0.3*mx[3]]
#         print mx


        if isDebug:
            print self.resp, self.quality
            print mu, var2, len([x for x in data2 if x is not None])

        x = [0.2*i for i in range(nData)]
        g0 = TGraph(nData, array('d',x), array('d',data))
        g0.Draw()

        g1 = TGraph(nData, array('d',[x[0]*0.2 for x in enumerate(data2) if x[1] is not None]), array('d',[x[1] for x in enumerate(data2) if x[1] is not None]))
        g1.SetMarkerColor(2)
        g1.Draw('Psame')
        
        waitRootCmdX()

class QuickTuner:
    def __init__(self, mode=0):
        self.mode = mode # 0: normal, 1: testing

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

#         sensorConfig = SensorConfig(cd)
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

    def assess(self, pars):
        ### send the parameters
        if mode==0: self.cd.dataSocket.sendall(self.cd.cmd.send_pulse(1<<2));
        time.sleep(0.1)

        ### save old data
        for i in range(len(self.cd.adcData)):
            for j in range(len(self.cd.adcData[i])):
                self.cd.adcData0[i][j] = self.cd.adcData[i][j]
       
        ### get new data
        if online:
            buf = self.cd.cmd.acquire_from_datafifo(self.cd.dataSocket, self.cd.nWords, self.cd.sampleBuf)
            self.demux_fifodata(buf, self.cd.adcData)


        ### evaluate the score
        get_score(self.cd.adcData)

        pass

    def demux_fifodata(self, fData, adcData=None, sdmData=None, adcVoffset=1.024, adcLSB=62.5e-6):
        wWidth = 512
        bytesPerSample = wWidth / 8
        if type(fData[0]) == str:
            fD = bytearray(fData)
        else:
            fD = fData
        if len(fD) % bytesPerSample != 0:
            print ("empty fD")
            return []
        nSamples = len(fD) / bytesPerSample
        if adcData == None:
            adcData = [[0 for i in xrange(nSamples)] for j in xrange(self.nAdcCh)]
        if sdmData == None:
            sdmData = [[0 for i in xrange(nSamples*self.adcSdmCycRatio)]
                          for j in xrange(self.nSdmCh*2)]
        for i in xrange(nSamples):
            for j in xrange(self.nAdcCh):
                idx0 = bytesPerSample - 1 - j*2
                v = ( fD[i * bytesPerSample + idx0 - 1] << 8
                    | fD[i * bytesPerSample + idx0])
                # convert to signed int
                v = (v ^ 0x8000) - 0x8000
                # convert to actual volts

                adcData[j][i] = v * adcLSB + adcVoffset
            b0 = self.nAdcCh*2
            for j in xrange(self.adcSdmCycRatio*self.nSdmCh*2):
                bi = bytesPerSample - 1 - b0 - int(j / 8)
                bs = j % 8
                ss = int(j / (self.nSdmCh*2))
                ch = j % (self.nSdmCh*2)
                sdmData[ch][i*self.adcSdmCycRatio + ss] = (fD[i * bytesPerSample + bi] >> bs) & 0x1
        #
        return adcData

    def save_data(self, fNames):
        with open(fNames[0], 'w') as fp:
            fp.write("# 5Msps ADC\n")
            nSamples = len(self.cd.adcData[0])
            for i in xrange(nSamples):
                for j in xrange(len(self.cd.adcData)):
                    fp.write(" {:9.6f}".format(self.cd.adcData[j][i]))
                fp.write("\n")
        with open(fNames[1], 'w') as fp:
            fp.write("# 25Msps SDM\n")
            nSamples = len(self.cd.sdmData[0])
            for i in xrange(nSamples):
                for j in xrange(len(self.cd.sdmData)):
                    fp.write(" {:1d}".format(self.cd.sdmData[j][i]))
                fp.write("\n")

    def tune(self, chan):
        ## give a set of parameters and get a quantity of goodness
        ### pass the parameters and get data
        ### assess the data -- what's good? What's better?
        ## Move the next set of parameters


        ### do the tunes here



        sensorConfig.cd.sD.close()
        sensorConfig.cd.sC.close()

        pass
    def test(self):
        print "testing"
        dat1 = None
        ichan = 5 if len(sys.argv)<2 else int(sys.argv[1])
        with open('adc_test.dat') as f1:
            dat1 = [float(l.split()[ichan]) for l in f1.readlines() if l.find('#')==-1]
        a1 = sigInfo(dat1)
#         self.get_score(dat1)
#         self.check(dat1)

def test():
    qt1 = QuickTuner(mode=1)
    qt1.test()

if __name__ == '__main__':
    test()
