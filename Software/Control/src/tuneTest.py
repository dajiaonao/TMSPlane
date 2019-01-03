#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from PyDE import *
import threading
from Queue import Queue
import time
from TMS1mmX19Tuner import SensorConfig, CommonData
import socket
from command import *

class tuner(threading.Thread):
    def __init__(self, idx):
        threading.Thread.__init__(self)
        self.idx = idx
        self.rx_qs = None
        self.tx_qs = None
        self.atBounds = [(-10,10),(-10,10),(-10,10),(-10,10),(-10,10),(-10,10)] 
        self.atMaxIters = 100

    def run(self):
        de = DE(self.auto_tune_fun, self.atBounds, maxiters=self.atMaxIters)
        ret = de.solve()
        self.tx_qs[self.idx] = None
        self.rx_qs[self.idx] = None
        print("Done {0:d}\n".format(self.idx))
 
        time.sleep(self.idx*1+1)
        print('-'*10, self.idx)
        print(ret)
       
    def auto_tune_fun1(self, x):
        return sum([(a-self.idx)*(a-self.idx) for a in x])

    def auto_tune_fun(self, x):
        ### put x to the queue
#         print(self.idx, 'sending', x)
        self.tx_qs[self.idx].put(x)
#         print('+++sent:['+','.join([str(a) for a in x]))

        ### wait for the returned value
        gg = self.rx_qs[self.idx].get()
#         print('+++get:{0:g}'.format(gg))
        return gg

class Train(threading.Thread):
    def __init__(self, nChan=5):
        threading.Thread.__init__(self)
        self.tx_qs = None
        self.rx_qs = None
        self.pars = [None]*nChan
        self.meas = [None]*nChan
        self.on = True
        self.mask = [0]*nChan

        ### for data taking
        self.s = None
        self.cmd = None
        self.sensor_config = None
        self.cd = None



    def run(self):
        while self.on:
            cnt = 0
            cnt1 = 0
            for i,q in enumerate(self.rx_qs):
                if q is None: continue
                cnt += 1
#                 x = q.get()
#                 self.pars[i] = x

                if not q.empty():
                    cnt1 += 1
                    x = q.get()
                    self.mask[i] = 1
#                     print('--- {0:d} get'.format(i)+' ['+','.join([str(a) for a in x])+']')
                    self.pars[i] = x

            if cnt == 0: self.on = False
            if cnt1 == 0: continue

            #### update sensor
            for i,p in enumerate(self.pars):
                if self.mask[i] == 1:
                    ### update sensor i

            ### take data
            time.sleep(2.0)
            meas = [[] for i in range(self.cd.sigproc.nParamMax)]*nChan
            for i in range(self.cd.atMeasNavg):
                # reset data fifo
                self.cd.dataSocket.sendall(self.cd.cmd.send_pulse(1<<2));
                time.sleep(0.05)
                buf = self.cd.cmd.acquire_from_datafifo(self.cd.dataSocket, self.cd.nWords, self.cd.sampleBuf)
                self.cd.sigproc.demux_fifodata(buf, self.cd.adcData, self.cd.sdmData)

                currMeasP = self.cd.sigproc.measure_pulse(self.cd.adcData)

                for j in range(nChan):
                    if currMeasP[j][2] < self.cd.atTbounds[0] or currMeasP[j][2] > self.cd.atTbounds[1] or currMeasP[j][3] < 0:
                        ### set -1
                    for k in range(len(currMeasP[j])):
                        meas[j][k].append(currMeasP[j][k])

            for j in range(nChan):
                currMeasP[j] = [sum(x)/len(x) for x in meas[j]]
                print("AutoTune: meas after {:d} avgs : {:}".format(self.cd.atMeasNavg, currMeasP[j]))
                ret = -currMeasP[j][3]/currMeasP[j][1]
                print("AutoTune: ret : ", ret, currMeasP[j][1], currMeasP[j][3])
                if ret < self.cd.atBestRet:
                    self.cd.atBestRet = ret
                    for i in range(len(self.cd.atBestVolts)):
                        self.cd.atBestVolts[i] = self.cd.inputVs[i]

            ### return
            for i,t in enumerate(self.tx_qs):
                if self.mask[i] == 1:
                    t.put(self.meas[i])
                    self.mask[i] = 0
#                     print("--- {0:d} {1:g}".format(i, self.meas[i]))
        print('Stopping the train.....')


class TestClass:
    def __init__(self, nAdcCh=20):
        self.x = None
        self.tx_qs = [None]*nAdcCh
        self.rx_qs = [None]*nAdcCh
        self.nAdcCh = nAdcCh

    def test_tune(self):
        dataIpPort = '192.168.2.3:1024'
        sD = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sD.connect((dataIpPort[0],int(dataIpPort[1])))

        ctrlIpPort = '192.168.2.3:1025'
        sC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sC.connect((ctrlIpPort[0],int(ctrlIpPort[1])))

        cmd = Cmd()
        cd = CommonData(cmd, dataSocket=sD, ctrlSocket=sC)
        cd.aoutBuf = 1 # AOUT buffer select, 0:AOUT1, 1:AOUT2, >1:disable both
        cd.x2gain = 2 # BufferX2 gain 
        cd.sdmMode = 0 # SDM working mode, 0:disabled, 1:normal operation, 2:test with signal injection 
        cd.bufferTest = 0 #

        sc1 = SensorConfig(cd, configFName='config.json')

        tr1 = Train(self.nAdcCh)
        tr1.tx_qs = self.rx_qs
        tr1.rx_qs = self.tx_qs
        tr1.sensor_config = sc1
        tr1.cd = cd
        tr1.on = True

        for i in range(self.nAdcCh):
            self.tx_qs[i] = Queue()
            self.rx_qs[i] = Queue()
            th1 = tuner(i)
            th1.tx_qs = self.tx_qs
            th1.rx_qs = self.rx_qs            
            th1.start()
        tr1.start()


def test1():
    tc1 = TestClass(8)
    tc1.test_tune()

if __name__ == '__main__':
    test1()
