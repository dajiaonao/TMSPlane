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
import numpy as nm
import matplotlib.pyplot as plt
import array
from ROOT import *
gROOT.LoadMacro("sp.C+")
from ROOT import SignalProcessor

class tuner(threading.Thread):
    def __init__(self, idx):
        threading.Thread.__init__(self)
        self.idx = idx
        self.rx_qs = None
        self.tx_qs = None
        self.atBounds = [(-10,10),(-10,10),(-10,10),(-10,10),(-10,10),(-10,10)] 
        self.atMaxIters = 1000

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
    def __init__(self, cd):
        threading.Thread.__init__(self)
        self.cd = cd
        self.tx_qs = None
        self.rx_qs = None
        self.on = True
        self.mask = [0]*cd.nCh
        self.nSig = 3

        ### this copy of sensorVcodes is used to save the best value find so far
        self.sensorVcodes = [[v for v in cd.sensorVcodes[i]] for i in range(cd.nCh)]
        self.bestConfigFile = 'current_best_config.json'
        self.retBest = [0.]*cd.nAdcCh

        ### for data taking
        self.sc = None

        ### plotting
        self.axs = None
        self.plot_x = None
        self.pltCnt = 0
        self.pltN = 20

        self.sp = SignalProcessor()
        self.sp.fltParam.clear()
        for x in [30, 50, 200, -1]: self.sp.fltParam.push_back(x)
#         self.sp.IO_adcData = self.cd.adcData
        self.sp.CF_chan_en.clear()
        self.sp.IO_mAvg.clear()
        for i in range(20):
            self.sp.CF_chan_en.push_back(1)
            self.sp.IO_mAvg.push_back(0.)

        s1 = self.cd.sigproc
        self.data1 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * (s1.nSamples * s1.nAdcCh))()
        self.ret1 = array.array('f',[0]*s1.nAdcCh)
        self.par1 = array.array('f',[0]*(self.cd.nCh*len(self.cd.inputVs)))

        self.saveT0 = -1
        outRootName = 'tt_test.root'
        self.fout1 = TFile(outRootName,'recreate')
        self.tree1 = TTree('tree1',"tune data for {0:d} channels, {1:d} samples".format(s1.nAdcCh, s1.nSamples))
        self.T = array.array('i',[0])
        self.tree1.Branch('T',self.T,'T/i')
        self.tree1.Branch('adc',self.data1, "adc[{0:d}][{1:d}]/F".format(s1.nAdcCh, s1.nSamples))
        self.tree1.Branch('ret',self.ret1, "ret[{0:d}]/F".format(s1.nAdcCh))
        self.tree1.Branch('par',self.par1, "par[{0:d}][{1:d}]/F".format(self.cd.nCh, len(self.cd.inputVs)))

    def plot_data(self):
#         item = self.q.get()
        if self.axs is None:
            print("creating the plot......")
            import matplotlib
            matplotlib.rcParams['toolbar'] = 'None'
            plt.ion()
            fig, self.axs = plt.subplots(self.cd.nAdcCh, 1, sharex=True)
            # Remove horizontal space between axes
            plt.tight_layout(pad=0)
            fig.subplots_adjust(hspace=0)
            self.plot_x = [self.cd.adcDt * i for i in range(self.cd.nSamples)]

        for i in range(self.cd.nAdcCh):
            self.axs[i].cla()
#             self.axs[i].plot(self.cd.adcData[i])
#             self.axs[i].step(array.array('f', self.cd.adcData[i]), where='post')
#             self.axs[i].plot(self.plot_x, array.array('f', self.cd.adcData[i]))
            self.axs[i].plot(self.plot_x, self.data1[i*self.cd.nSamples : (i+1)*self.cd.nSamples])
        plt.draw()
#         self.q.task_done()


    def test_update_sensor(self):
        print('/'*40)
        inputVs = [[1.379, 1.546, 1.626, 1.169, 1.357, 2.458],[1.379, 1.546, 1.626, 1.169, 1., 2.]]
        #### update sensor configurations
        ss = set()
        for i,p in enumerate(inputVs):
            self.cd.set_sensor(i,p)
            ss.add(self.sc.tms1mmX19chainSensors[self.sc.tms1mmX19sensorInChain[i]][0])

        ### apply the configurations
        print(ss)
        for isr in ss:
            self.sc.update_sensor(isr)
        print('\\'*40)

    def take_data(self):
        '''return an array of FOM'''
        s1 = self.cd.sigproc
        self.cd.dataSocket.sendall(self.cd.cmd.send_pulse(1<<2));
        buf = self.cd.cmd.acquire_from_datafifo(self.cd.dataSocket, self.cd.nWords, self.cd.sampleBuf)
        s1.demux_fifodata(buf, self.data1, self.cd.sdmData)

        self.sp.measure_multiple(self.data1, 2000)
        for i in range(s1.nAdcCh): self.ret1[i] = -self.sp.IO_mAvg[i]

        self.T[0] = int(time.time())
        print(self.ret1[3],self.ret1[0])
        self.tree1.Fill()

        if self.T[0]-self.saveT0>200:
            self.tree1.AutoSave('SaveSelf')
            self.saveT0 = self.T[0]

    def run(self):
        nPar = len(self.cd.inputVs)

        ### save the initial values
        for i in range(self.cd.nCh):
            for kk in range(nPar): 
                self.par1[i*nPar+kk] = self.cd.tms1mmReg.dac_code2volt(self.sensorVcodes[i][kk])

        while self.on:
            cnt = 0
#             cnt1 = 0
            ss = set()
            for i,q in enumerate(self.rx_qs):
                if q is None: continue
                cnt += 1
#                 x = q.get()
#                 self.pars[i] = x

                if not q.empty():
#                     cnt1 += 1
                    x = q.get()
                    self.mask[i] = 1
#                     print('--- {0:d} get'.format(i)+' ['+','.join([str(a) for a in x])+']')
#                     self.pars[i] = x
#                     print(i,x)
                    self.cd.set_sensor(i,x)
                    for kk in range(nPar): self.par1[i*nPar+kk] = x[kk] 
                    ss.add(self.sc.tms1mmX19chainSensors[self.sc.tms1mmX19sensorInChain[i]][0])


            if cnt == 0: self.on = False
            if len(ss) == 0: continue
#             if cnt1 == 0: continue

            #### update sensor configurations
#             ss = set()
#             for i,p in enumerate(self.pars):
#                 if self.mask[i] == 1:
#                     self.cd.set_sensor(i,p)
#                     ss.append(self.sc.tms1mmX19chainSensors[self.sc.tms1mmX19sensorInChain[i]][0])

            ### apply the configurations
            for isr in ss:
                self.sc.update_sensor(isr,quiet=1)

            ### take data
            self.pltCnt += 1
            t = None
            if self.pltCnt%self.pltN == 0:
                self.plot_data()
#                 t = threading.Thread(target=self.plot_data)
#                 t.daemon = True
#                 t.start()
#                 self.q.put('run')

            time.sleep(15.0)
            if t is not None: t.join()

            self.take_data()
            ret = self.ret1

            ### return
            needUpdate = False
            for i,t in enumerate(self.tx_qs):
                if self.mask[i] == 1:
                    t.put(ret[i])
                    self.mask[i] = 0

                    ### save the values if it's the best so far
                    if ret[i]<self.retBest[i]:
                        print("find better parameters for channel", i)
                        print('old:',self.sensorVcodes[i], self.retBest[i])
                        self.retBest[i] = ret[i]
                        self.sensorVcodes[i] = [a for a in self.cd.sensorVcodes[i]]
                        print('new:',self.sensorVcodes[i], self.retBest[i])
                        needUpdate = True
#                     print("--- {0:d} {1:g}".format(i, self.meas[i]))
            if needUpdate:
                self.sc.write_config_fileX(self.bestConfigFile, self.sensorVcodes)
        print('Stopping the train.....')
        plt.close('all')
        self.tree1.Write()
        self.fout1.Close()

class TestClass:
    def __init__(self, nCh=19):
        self.x = None
        self.tx_qs = [None]*nCh
        self.rx_qs = [None]*nCh
        self.nCh = nCh
        self.muteList = []
        self.atBounds = None

    def test_tune(self):
        host='192.168.2.3'
        if socket.gethostname() == 'FPGALin': host = 'localhost'

        dataIpPort = (host+':1024').split(':')
        sD = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sD.connect((dataIpPort[0],int(dataIpPort[1])))

        ctrlIpPort = (host+':1025').split(':')
        sC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sC.connect((ctrlIpPort[0],int(ctrlIpPort[1])))

        cmd = Cmd()
        cd = CommonData(cmd, dataSocket=sD, ctrlSocket=sC)
        cd.aoutBuf = 1 # AOUT buffer select, 0:AOUT1, 1:AOUT2, >1:disable both
        cd.x2gain = 2 # BufferX2 gain 
        cd.sdmMode = 0 # SDM working mode, 0:disabled, 1:normal operation, 2:test with signal injection 
        cd.bufferTest = 0 #
#         cd.atTbounds = (2650,2750)
        cd.atTbounds = (4050,4150)

        sc1 = SensorConfig(cd, configFName='config.json')

        tr1 = Train(cd)
        tr1.tx_qs = self.rx_qs
        tr1.rx_qs = self.tx_qs
        tr1.sc = sc1
        tr1.on = True

#         tr1.test_update_sensor()
#         tr1.take_data()
        ### for the chip #3? the default one in LBL
        better_bounds = [None]*self.nCh
        better_bounds[0] = [(0.9, 1.5), (0.5, 1.2), (1.1, 1.8), (0.5, 1.4), (1.4, 1.8), (2.5, 2.8)]
        better_bounds[1] = [(0.8, 1.5), (0.5, 1.4), (1.0, 1.8), (0.5, 1.6), (1.4, 2.0), (2.5, 2.8)]
        better_bounds[2] = [(0.5, 1.5), (0.5, 1.8), (0.5, 1.5), (0.5, 2.0), (0.8, 2.4), (1.8, 2.8)]
        better_bounds[3] = [(0.8, 1.5), (0.5, 1.3), (1.0, 1.8), (0.5, 2.0), (0.8, 2.0), (1.8, 2.8)]
        better_bounds[4] = [(0.9, 1.2), (0.5, 1.3), (0.5, 1.8), (0.5, 1.4), (0.8, 1.8), (2.5, 2.8)]
        better_bounds[5] = [(0.8, 1.5), (0.5, 1.5), (0.9, 1.8), (0.5, 2.0), (0.8, 2.0), (1.8, 2.8)]
        better_bounds[6] = [(0.8, 1.2), (0.5, 1.5), (1.0, 1.5), (0.5, 2.0), (0.8, 1.8), (1.8, 2.8)]
        better_bounds[7] = [(0.5, 1.5), (0.5, 1.1), (1.4, 1.8), (0.5, 1.6), (0.8, 1.5), (2.5, 2.8)]
        better_bounds[8] = [(0.5, 1.5), (0.5, 1.8), (0.5, 1.8), (0.5, 2.0), (0.8, 1.6), (2.4, 2.8)]
        better_bounds[9] = [(0.7, 1.5), (0.5, 1.4), (1.0, 1.8), (0.5, 1.8), (0.8, 2.0), (2.5, 2.8)]
        better_bounds[10] = [(0.8, 1.3), (0.5, 1.4), (0.9, 1.6), (0.5, 2.0), (0.8, 2.0), (1.9, 2.8)]
        better_bounds[11] = [(0.5, 1.5), (0.5, 1.0), (1.3, 1.8), (0.5, 1.4), (0.8, 1.2), (2.5, 2.8)]
        better_bounds[12] = [(0.7, 1.3), (0.5, 1.3), (1.1, 1.8), (0.5, 1.8), (0.8, 2.0), (2.5, 2.8)]
        better_bounds[13] = [(0.8, 1.3), (0.5, 1.4), (1.1, 1.8), (0.5, 1.7), (0.8, 2.2), (2.4, 2.8)]
        better_bounds[14] = [(0.7, 1.5), (0.5, 1.2), (1.3, 1.8), (0.5, 1.5), (0.8, 1.8), (2.5, 2.8)]
        better_bounds[15] = [(0.9, 1.3), (0.5, 1.2), (1.1, 1.8), (0.5, 1.6), (0.8, 1.8), (2.5, 2.8)]
        better_bounds[16] = [(0.9, 1.5), (0.5, 1.2), (1.2, 1.8), (0.5, 1.5), (0.8, 1.8), (2.5, 2.8)]
        better_bounds[17] = [(0.5, 1.5), (0.5, 1.0), (1.0, 1.5), (0.5, 1.1), (0.8, 1.2), (2.5, 2.8)]
        better_bounds[18] = [(0.9, 1.4), (0.5, 1.3), (1.0, 1.8), (0.5, 1.6), (0.8, 1.8), (2.5, 2.8)]


        for i in range(self.nCh):
            if i in self.muteList: continue
            self.tx_qs[i] = Queue()
            self.rx_qs[i] = Queue()
            th1 = tuner(i)
            th1.tx_qs = self.tx_qs
            th1.rx_qs = self.rx_qs            
#             th1.atBounds = cd.atBounds
            th1.atBounds = better_bounds[i]
#             th1.atBounds = better_bounds[i] if better_bounds[i] is not None else cd.atBounds
            th1.atMaxIters = cd.atMaxIters
            th1.start()
        tr1.start()

def test1():
    tc1 = TestClass()
#     tc1.muteList = [3,5,6,8,12,18]
    tc1.muteList = []
    tc1.test_tune()

if __name__ == '__main__':
    test1()
