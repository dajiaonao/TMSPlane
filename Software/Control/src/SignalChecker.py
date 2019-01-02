#!/usr/bin/env python
import socket
# import argparse
# import pprint
from command import *
from sigproc import SigProc 
import time
import array
import glob
from rootUtil import waitRootCmdX


class SignalChecker:
    def __init__(self):
        self.control_ip_port = "192.168.2.3:1024"
        self.cmd = Cmd()
        self.s = None
#         self.connect()

    def connect(self):
        ctrlipport = self.control_ip_port.split(':')
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect((ctrlipport[0],int(ctrlipport[1])))

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

    def check_enc(self, filePattern, ch):
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

def test1():
    sc1 = SignalChecker()
#     sc1.check_file('/data/Samples/TMSPlane/Dec26/sample_0.adc')
#     sc1.check_file('/data/Samples/TMSPlane/Dec27/Dec27a_1281.adc')
#     sc1.check_enc('/data/Samples/TMSPlane/Dec27/Dec27a_*.adc', ch=12)
#     sc1.take_samples()
#     sc1.show_signal()
#     sc1.show_sample()
#     sc1.show_sample('/data/Samples/TMSPlane/Dec27/Dec27a_10{0:d}.adc',Ns=80,ich=12)
    sc1.show_sample('/data/Samples/TMSPlane/Dec27/Dec27a_1000.adc',Ns=1,ich=12)

if __name__ == '__main__':
    test1()
