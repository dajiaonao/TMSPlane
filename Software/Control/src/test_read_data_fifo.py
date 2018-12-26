#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package ReadDataFIFO
# test reading datafifo
#

from __future__ import print_function
from __future__ import division
import math,sys,time,os,shutil
import socket
import argparse
import pprint
from command import *
from sigproc import SigProc 
import matplotlib.pyplot as plt
import array

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--control-ip-port", type=str, default="192.168.2.3:1024", help="main control system ipaddr and port")
    args = parser.parse_args()

    s1 = SigProc(nSamples=16384, nAdcCh=20, nSdmCh=19, adcSdmCycRatio=5)
    data1 = s1.generate_adcDataBuf()
    data2 = s1.generate_sdmDataBuf()

    data_source = 1

    if data_source == 0:
        ctrlipport = args.control_ip_port.split(':')
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((ctrlipport[0],int(ctrlipport[1])))
        cmd = Cmd()

        # reset data fifo
        s.sendall(cmd.send_pulse(1<<2));
        time.sleep(0.5)

        # FPGA internal fifo : 512 bit width x 16384 depth
        nWords = (512 // 32) * 16384
        nBytes = nWords * 4
        buf = bytearray(nBytes)
        print("nBytes = {:d}".format(nBytes))
        ret = cmd.acquire_from_datafifo(s, nWords, buf)
        print("Returned {:d} bytes.".format(len(ret)))
        #print(":".join("{:02x}".format(ord(c)) for c in ret))
        s1.demux_fifodata(ret,data1,data2)

        s.close()

    else:
        s1.read_data(['/data/Samples/TMSPlane/Dec26/sample_0.adc','/data/Samples/TMSPlane/Dec26/sample_0.sdm'], data1, data2)


    ich = 8
    data3 = (s1.ANALYSIS_WAVEFORM_BASE_TYPE * s1.nSamples)()
    s1.filters_trapezoidal(data1[ich], data3, [100,100,200,-1])
   
#     for i in range(s1.nSamples):
#         print(i,data1[8][i],data3[i])
#         if i%20 == 0:
#             x = raw_input()
#             if x=='q': break

    x = range(s1.nSamples)
#     x = range(1000)
    print(len(data1[ich]))
    d0 =  array.array('f', data1[ich])
    d3 =  array.array('f', data3)
#     plt.plot(x,d0,'--',x,d3,'bs')
#     plt.plot(x,d0)
#     plt.plot(x,d3)
#     plt.ylabel('ADC')
#     plt.show()

    plt.figure(1, figsize=(16, 8))
    plt.subplot(121)
    plt.plot(x,d0)
    plt.subplot(122)
    plt.plot(x,d3)
    plt.show()
