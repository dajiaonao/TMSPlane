#!/usr/bin/env python
import socket
# import argparse
# import pprint
from command import *
from sigproc import SigProc 
import time
import array
import glob
from ROOT import *
from subprocess import call
from math import isnan

def waitRootCmdY():
    a = raw_input("waiting...")

try:
    from rootUtil import waitRootCmdX
except ImportError:
    waitRooCmdX = waitRootCmdY


class SignalChecker:
    def __init__(self):
        self.control_ip_port = "192.168.2.3:1024"
        self.cmd = Cmd()
        self.s = None
        self.connected = False
#         self.connect()

    def connect(self):
        ctrlipport = self.control_ip_port.split(':')
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect((ctrlipport[0],int(ctrlipport[1])))
        self.connected = True

    def take_samples(self, n=10, name="sample_{0:d}"):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)

        for i in range(n):
            self.s.sendall(self.cmd.send_pulse(1<<2));
            time.sleep(0.5)

            name1 = name.format(i)
            ret = self.cmd.acquire_from_datafifo(self.s, nWords, buf)
            s1.demux_fifodata(ret,data1,data2)
            s1.save_data([name1+'.adc', name1+'.sdm'], data1, data2)

    def take_samples2(self, n=10, outRootName='test_sample.root'):
        if not self.connected: self.connect()

        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        T = array.array('i',[0])
        fout1 = TFile(outRootName,'recreate')
        tree1 = TTree('tree1',"data: {0:d} channel, {1:d} samples".format(s1.nAdcCh, s1.nSamples))
        tree1.Branch('T',T,'T/i')
        tree1.Branch('adc',data1, "adc[{0:d}][{1:d}]/F".format(s1.nAdcCh, s1.nSamples))

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)

        for i in range(n):
            if i%100==0: print(str(i)+' samples taken.')
            self.s.sendall(self.cmd.send_pulse(1<<2));
#             time.sleep(0.5)

            T[0] = int(time.time())
            ret = self.cmd.acquire_from_datafifo(self.s, nWords, buf)
            s1.demux_fifodata(ret,data1,data2)
            tree1.Fill()
        fout1.Write()

    def show_signal(self):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)


        self.s.sendall(self.cmd.send_pulse(1<<2));
        time.sleep(0.5)

        ret = self.cmd.acquire_from_datafifo(self.s, nWords, buf)
        s1.demux_fifodata(ret,data1,data2)

        mx = s1.measure_pulse(data1, fltParam=[500, 150, 200, -1.])
        for x in mx:
            for i in range(len(x)):
                print x[i]
        d = [x[1] for x in mx]
        self.plot_data(d)

    def plot_data(self,d):
        if len(d)<19:
            print('Need 19 entries')
            return
        from ROOT import TH2Poly, gStyle
        gStyle.SetOptStat(0)

        hc = TH2Poly();
        hc.SetTitle("TMS19Plane");
        hc.Honeycomb(-4.3,-4,1,5,5);
        listA = [(0,0),(2,0),(1,1.5),(-1,1.5),(-2,0),(-1,-1.5),(1,-1.5),(4,0),(3,2),(1,3),(0,3),(-1,3),(-3,2),(-4,0),(-3,-2),(-1,-3),(0,-3),(1,-3),(3,-2)]

        for i in range(len(listA)):
            hc.Fill(listA[i][0],listA[i][1],d[i])

        hc.Draw("text colz0");
        waitRootCmdX()

    def check_file(self, fname):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        s1.read_data([fname,''], data1, data2)

        mx = s1.measure_pulse(data1, fltParam=[500, 150, 200, -1.])
        d = [x[2] for x in mx]
        self.plot_data(d)

    def show_sample(self, fnameP='/data/Samples/TMSPlane/Dec26/sample_{0:d}.adc', Ns=10, ich=8):
        from ROOT import TGraph, gPad, TLatex
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        data3 = ((s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nSamples)*Ns)()
        dataList = []
        for i in range(Ns):
            fname = fnameP.format(i)
            s1.read_data([fname,''], data1, data2)
            x = array.array('f', range(s1.nSamples))
#             s1.filters_trapezoidal(data1[ich], data3[i], [100,100,200,-1])
            s1.filters_trapezoidal(data1[ich], data3[i], [100,100,100,0.000722])
            g1 = TGraph(s1.nSamples, x, data3[i])
#             g1 = TGraph(s1.nSamples, x, data1[ich])

            opt = 'AP' if i==0 else "PSame"
            g1.Draw(opt+' PLC PMC')
            dataList.append(g1)

        lt = TLatex()
        lt.DrawLatexNDC(0.2,0.8,"Chan={0:d}".format(ich))
        gPad.Update()
        waitRootCmdX()

    def check_enc(self, filePattern):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        files = glob.glob(filePattern)
        with open('test1bbb.dat','w') as fout:
            fout.write(':'.join(['sID/I', 'ch/I', 'B/F','dB/F','idx/I','A/F']))
            for fname in files:
                s1.read_data([fname,''], data1, data2)
                mxx = s1.measure_pulse(data1, fltParam=[500, 150, 200, -1.])
                for ch in range(s1.nAdcCh):
                    mx = mxx[ch]
                    fout.write('\n'+' '.join([fname[fname.find('_')+1:-4],str(ch), str(mx[0]), str(mx[1]), '{0:d}'.format(int(mx[2])), str(mx[3])]))

    def check_enc2(self, inRoot, outText):
        s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
        data1 = s1.generate_adcDataBuf()
        data2 = s1.generate_sdmDataBuf()

        fout1 = TFile(inRoot,'read')
        tree1 = fout1.Get('tree1')
#         tree1.SetBranchAddress('ch0',data1)
        tree1.SetBranchAddress('adc',data1)
        with open(outText,'w') as fout:
            fout.write(':'.join(['sID/I', 'ch/I', 'B/F','dB/F','idx/I','A/F']))

            for i in range(tree1.GetEntries()):
                if i%100==0: print(str(i)+' entries processed')
                tree1.GetEntry(i)
                mxx = s1.measure_pulse(data1, fltParam=[500, 150, 200, -1.])
                for ch in range(s1.nAdcCh):
                    mx = mxx[ch]
                    if isnan(mx[1]): print("xxxx")
                    fout.write('\n'+' '.join([str(i),str(ch), str(mx[0]), str(mx[1]), '{0:d}'.format(int(mx[2])), str(mx[3])]))

def text2root(spattern, irange, outname):
    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = s1.generate_adcDataBuf()
    data2 = s1.generate_sdmDataBuf()

    fout1 = TFile(outname,'recreate')
    tree1 = TTree('tree1',"data: {0:d} channel, {1:d} samples".format(s1.nAdcCh, s1.nSamples))
    tree1.Branch('ch0',data1, "ch0[{0:d}][{1:d}]/F".format(s1.nAdcCh, s1.nSamples))

    for i in irange:
        s1.read_data([spattern.format(i),'xxx'], data1, data2)
        tree1.Fill()
    fout1.Write()

def setPulse(v,f):
    cmd = 'ssh maydaq.dhcp.lbl.gov ./fungen_ctrl.py {0:.3f} {1:d}'.format(v,f)
    call(cmd, shell=True)

def test1():
    sc1 = SignalChecker()
    sc1.control_ip_port = "localhost:1024"
#     sc1.take_samples2(100, "data/test1.root")
#     sc1.take_samples2(5000, "data/sample1.root")
#     sc1.take_samples2(5000, "data/Jan18a_C2_50mV.root")
#     dir1 = 'data/fpgaLin/'
#     tag1 = dir1+'Jan22a_C2_100mV_'
#     for f in [100,200,500,1000]:
#         setPulse(0.1,f)
#         time.sleep(20)
#         sc1.take_samples2(5000, tag1+"f{0:d}.root".format(f))
#         sc1.check_enc2(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f))
    dir1 = 'data/fpgaLin/'
#     tag1 = dir1+'Jan22b_C2_'
#     for iv in range(16):
#         v = 0.025+iv*0.05
#         setPulse(v,1000)
#         time.sleep(20)
#         sc1.take_samples2(5000, tag1+"{0:d}mV_f1000.root".format(int(v*1000)))
#         sc1.check_enc2(tag1+"f{0:d}.root".format(f), tag1+"f{0:d}.dat".format(f))
    tag1 = dir1+'Jan28b_C2_'
    for iv in range(31):
        v = 0.025+iv*0.025

#         if v<0.37: continue
        setPulse(v,500)
        time.sleep(50)
        sc1.take_samples2(100, tag1+"{0:d}mV_f500.root".format(int(v*1000)))
#
#     sc1.take_samples(10, name="Jan03a_{0:d}")
#     sc1.take_samples(5000, name="data/Jan04a/Jana04a_{0:d}")
#     sc1.take_samples2(5000, "data/Jan05a_150mV.root")
#     sc1.take_samples2(5000, "data/Jan05a_400mV.root")
#    sc1.take_samples2(5000, "data/Jan09a_300mV.root")
#     sc1.take_samples2(5000, "data/Jan05a_50mV.root")
#     sc1.take_samples2(5000, "data/Jan08a_100mV_R19p5312us.root")
#     sc1.take_samples2(5000, "data/Jan08a_100mV_R30p0us.root")
#     sc1.take_samples2(5000, "data/Jan08a_100mV_R40p0us.root")
#     sc1.take_samples2(5000, "data/Jan08a_100mV_r50p0us.root")
#     sc1.take_samples2(5000, "data/Jan08a_100mV_r30p0us.root")
#     sc1.take_samples2(5000, "data/Jan08a_100mV_r40p0us.root")
#     sc1.take_samples2(100, "data/test.root")
#     sc1.show_signal()
#     sc1.check_file('/data/Samples/TMSPlane/Dec26/sample_0.adc')
#     sc1.check_file('/data/Samples/TMSPlane/Dec27/Dec27a_1281.adc')
#     sc1.check_enc('/data/Samples/TMSPlane/Dec27/Dec27a_*.adc', ch=12)
#     sc1.check_enc2('data/root_files/Jan05a_50mV.root', 'Jan05a_50mV.dat')
#     sc1.check_enc2('data/root_files/Jan05a_100mV.root', 'Jan05a_100mV.dat')
#     sc1.check_enc2('data/root_files/Jan05a_150mV.root', 'Jan05a_150mV.dat')
#     sc1.check_enc2('data/root_files/Jan05a_400mV.root', 'Jan05a_400mV.dat')
#     sc1.check_enc2('data/root_files/Jan08a_100mV_r30p0us.root', 'Jan08a_100mV_r30p0us.dat')
#     sc1.check_enc2('data/root_files/Jan08a_100mV_r40p0us.root', 'Jan08a_100mV_r40p0us.dat')
#     sc1.check_enc2('data/root_files/Jan08a_100mV_r50p0us.root', 'Jan08a_100mV_r50p0us.dat')
#     sc1.check_enc2('/data/Samples/TMSPlane/root_files/Jan05a_50mV.root', 'Jan05a_50mV.dat')
#     sc1.check_enc2('/data/Samples/TMSPlane/root_files/Jan05a_150mV.root', 'Jan05a_150mV.dat')
#     sc1.check_enc2('data/sample1.root', 'Jan17_sample1.dat')
#     sc1.check_enc2('data/Jan18a_C2_50mV.root', 'data/Jan18a_C2_50mV.dat')
#     sc1.take_samples()
#     sc1.show_signal()
#     sc1.show_sample()
#     sc1.show_sample('/data/Samples/TMSPlane/Dec27/Dec27a_10{0:d}.adc',Ns=80,ich=12)
#     sc1.show_sample('/data/Samples/TMSPlane/Dec27/Dec27a_1000.adc',Ns=1,ich=12)

if __name__ == '__main__':
    test1()
#     text2root(spattern='/data/Samples/TMSPlane/Dec27/Dec27a_{0:d}.adc',irange=range(10,20),outname='testxy.root')
#     text2root(spattern='data/Jan04a/Jana04a_{0:d}.adc',irange=range(5000),outname='ADC_Jan04a.root')
