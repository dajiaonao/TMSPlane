#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## @package TMS1mmX19Tuner
# Human interface for tuning the Topmetal-S 1mm version chip x19 array
#

from __future__ import print_function
import math,sys,time,os,shutil
import copy
import socket
import argparse
from command import *
from sigproc import *
import TMS1mmX19Config

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import threading

from TMS1mmX19Tuner1 import CommonData, SensorConfig
import matplotlib
# matplotlib.use('TkAgg')
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler # for the default matplotlib key bindings
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from matplotlib import artist
import array

online = True

class DataPanelGUI(object):

    ##
    # @param [in] dataFigSize (w, h) in inches for the data plots figure assuming dpi=72
    def __init__(self, master, cd, dataFigSize=(13, 12.5)):
        self.mode = 0
        self.master = master
        self.cd = cd
        self.nAdcCh = self.cd.nAdcCh
        self.nSdmCh = self.cd.nCh
        self.adcSdmCycRatio = self.cd.adcSdmCycRatio
        self.sensor_config = None

        self.master.wm_title("Topmetal-S 1mm version x19 array data")
        # appropriate quitting
        self.master.wm_protocol("WM_DELETE_WINDOW", self.quit)
        self.autoSaveData = False
        self.sampleID = 0

        ######## Control frame #########
        self.nVolts = self.cd.nVolts
        self.nCh = self.cd.nCh

        self.controlFrame = tk.Frame(self.master)
        self.controlFrame.pack(side=tk.LEFT)
        button1 = tk.Button(master=self.controlFrame, text='Save data', command=self.save_data0)
        button1.pack(side=tk.TOP, fill=tk.X)

        button = tk.Button(master=self.controlFrame, text='Re-sample', command=self.re_sample)
        button.pack(side=tk.BOTTOM, fill=tk.X)
        button2 = tk.Button(master=self.controlFrame, text='Auto-update', command=self.auto_update)
        button2.pack(side=tk.TOP, fill=tk.X)

        # frame for selecting a sensor to operate on
        self.sensorsFrame = tk.Frame(self.controlFrame)
        self.sensorsFrame.pack(side=tk.TOP)

        ### save config
        button3 = tk.Button(master=self.controlFrame, text='Save config', command=self.save_config)
        button3.pack(side=tk.TOP, fill=tk.X, expand=True)

        # sensor location approximated on a grid (row, col)
        self.sensorLocOnGrid = {0 : [4,2], 1 : [2,2], 2 : [3,1], 3 : [5,1],  4 : [6,2],  5 : [5,3],
                                6 : [3,3], 7 : [0,2], 8 : [1,1], 9 : [2,0], 10 : [4,0], 11 : [6,0],
                                12 : [7,1], 13 : [8,2], 14: [7,3], 15 : [6,4], 16 : [4,4],
                                17 : [2,4], 18 : [1,3]}
        self.sensorSelVar = tk.IntVar()
        self.sensorSelRadioButtons = [tk.Radiobutton(self.sensorsFrame, text="{:d}".format(i),
                                                     variable=self.sensorSelVar, value=i,
                                                     command=self.select_current_sensor)
                                      for i in range(self.nCh)]
        for i in range(len(self.sensorSelRadioButtons)):
            b = self.sensorSelRadioButtons[i]
            b.grid(row=self.sensorLocOnGrid[i][0], column=self.sensorLocOnGrid[i][1])

        # frame for controls
        self.voltagesFrame = tk.Frame(self.controlFrame)
        self.voltagesFrame.pack(side=tk.BOTTOM)

        # GUI widgets
        self.voltsNameLabels =  [tk.Label(self.voltagesFrame, text=self.cd.voltsNames[i])
                             for i in range(self.nVolts)]
        self.voltsILabels = [tk.Label(self.voltagesFrame, font="Courier 10", text="0.0")
                             for i in range(self.nVolts)]

        self.voltsOutputLabels = [tk.Label(self.voltagesFrame, font="Courier 10", text="0.0")
                                  for i in range(self.nVolts)]

        self.voltsSetVars = [tk.DoubleVar() for i in range(self.nVolts)]
        for i in range(self.nVolts):
            self.voltsSetVars[i].set(self.cd.inputVs[i])
        self.voltsSetEntries = [tk.Spinbox(self.voltagesFrame, width=8, justify=tk.RIGHT,
                                           textvariable=self.voltsSetVars[i],
                                           from_=0.0, to=3.3, increment=0.001,
                                           format_="%6.4f",
                                           command=self.set_voltage_update)
                                for i in range(self.nVolts)]
        for v in self.voltsSetEntries:
            v.bind('<Return>', self.set_voltage_update)

        self.voltsSetCodeVars = [tk.IntVar() for i in range(self.nVolts)]
        for i in range(self.nVolts):
            self.voltsSetCodeVars[i].set(self.cd.inputVcodes[i])
        self.voltsSetCodeEntries = [tk.Spinbox(self.voltagesFrame, width=8, justify=tk.RIGHT,
                                               textvariable=self.voltsSetCodeVars[i],
                                               from_=0, to=65535, increment=1,
                                               command=self.set_voltage_dac_code_update)
                                    for i in range(self.nVolts)]
        for v in self.voltsSetCodeEntries:
            v.bind('<Return>', self.set_voltage_dac_code_update)

        # caption
        tk.Label(self.voltagesFrame, text="Name", width=8,
                 fg="white", bg="black").grid(row=0, column=0, sticky=tk.W+tk.E)
        tk.Label(self.voltagesFrame, text="Voltage [V]", width=10,
                 fg="white", bg="black").grid(row=0, column=1, sticky=tk.W+tk.E)
        tk.Label(self.voltagesFrame, text="DAC code", width=10,
                 fg="white", bg="black").grid(row=0, column=2, sticky=tk.W+tk.E)
        tk.Label(self.voltagesFrame, text="Measured [V]",
                 fg="white", bg="black").grid(row=0, column=3, sticky=tk.W+tk.E)

        # placing widgets
        for i in range(self.nVolts):
            self.voltsNameLabels[i].grid(row=i+1,column=0)
            self.voltsSetEntries[i].grid(row=i+1, column=1)
            self.voltsSetCodeEntries[i].grid(row=i+1, column=2)
            self.voltsOutputLabels[i].grid(row=i+1, column=3)

        self.update_values_display()
        ######## End of contral Frame ########

        # frame for plotting
        self.dataPlotsFrame = tk.Frame(self.master)
        self.dataPlotsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.dataPlotsFrame.bind("<Configure>", self.on_resize)
        self.dataPlotsFigure = Figure(figsize=dataFigSize, dpi=72)
        self.dataPlotsFigure.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.05, hspace=0, wspace=0)
        # x-axis is shared
#         dataPlotsSubplotN = self.dataPlotsFigure.add_subplot(self.nCh, 1, self.nCh, xlabel='t [us]', ylabel='[V]')
        dataPlotsSubplotN = self.dataPlotsFigure.add_subplot(1, 1, 1, xlabel='t [us]', ylabel='[V]')
        self.dataPlotsSubplots = []
#         self.dataPlotsSubplots = [self.dataPlotsFigure.add_subplot(self.nCh, 1, i+1, sharex=dataPlotsSubplotN)
#                                   for i in range(self.nCh-1)]
#         for a in self.dataPlotsSubplots:
#             artist.setp(a.get_xticklabels(), visible=False)
        self.dataPlotsSubplots.append(dataPlotsSubplotN)
        self.dataPlotsCanvas = FigureCanvasTkAgg(self.dataPlotsFigure, master=self.dataPlotsFrame)
        self.dataPlotsCanvas.draw()
        self.dataPlotsCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#         self.dataPlotsToolbar = NavigationToolbar2TkAgg(self.dataPlotsCanvas, self.dataPlotsFrame)
        self.dataPlotsToolbar = NavigationToolbar2Tk(self.dataPlotsCanvas, self.dataPlotsFrame)
        self.dataPlotsToolbar.update()
        self.dataPlotsCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.dataPlotsCanvas.mpl_connect('key_press_event', self.on_key_event)
        #
        self.plot_data()

    def on_key_event(self, event):
        print('You pressed {:s}'.format(event.key))
        key_press_handler(event, self.dataPlotsCanvas, self.dataPlotsToolbar)

    def on_resize(self, event):
        # print(event.width, event.height)
        return

    def quit(self):
        with self.cd.cv:
            self.cd.quit = True
            self.cd.cv.notify()
        self.master.quit()     # stops mainloop
        self.master.destroy()  # this is necessary on Windows to prevent
                               # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def get_and_plot_data(self):
        # reset data fifo
        print("in get_and_plot_data")
        if online: self.cd.dataSocket.sendall(self.cd.cmd.send_pulse(1<<2));
        time.sleep(0.1)

        for i in range(len(self.cd.adcData)):
            for j in range(len(self.cd.adcData[i])):
                self.cd.adcData0[i][j] = self.cd.adcData[i][j]
        
        if online:
            buf = self.cd.cmd.acquire_from_datafifo(self.cd.dataSocket, self.cd.nWords, self.cd.sampleBuf)
            self.cd.sigproc.demux_fifodata(buf, self.cd.adcData, self.cd.sdmData)
        self.plot_data()

        if self.autoSaveData:
            self.cd.sigproc.save_data(self.cd.dataFName, self.cd.adcData, self.cd.sdmData)

    def plot_data(self):
        print("going to plot sensor", self.cd.currentSensor)
        for a in self.dataPlotsSubplots:
            a.cla()
            self.dataPlotsFigure.texts = []
#             for txt in self.dataPlotsFigure.texts:
#                 txt.set_visible(False)
        a = self.dataPlotsSubplots[-1]
#         a.set_xlabel(u't [us]')
        a.set_xlabel(u't [ms]')
        self.cd.adcDt = 0.2*0.001
        a.set_ylabel('[V]')
        nSamples = len(self.cd.adcData[0])
        x = [self.cd.adcDt * i for i in range(nSamples)]

        a.locator_params(axis='y', tight=True, nbins=4)
        a.yaxis.set_major_formatter(FormatStrFormatter('%7.4f'))
        a.set_xlim([0.0, self.cd.adcDt * nSamples])
       
        a.grid()

        a.step(x, array.array('f', self.cd.adcData0[self.cd.currentSensor]), where='post', color='lightcoral')
        a.step(x, array.array('f', self.cd.adcData[self.cd.currentSensor]), where='post')
        dd1 = max(self.cd.adcData[self.cd.currentSensor])-min(self.cd.adcData[self.cd.currentSensor])
        l1 = self.dataPlotsFigure.text(0.2, 0.92,'New:{0:.3f}'.format(0.5*dd1), ha='center', va='center', transform=a.transAxes)
        l1.set_color('blue')

        dd0 = max(self.cd.adcData0[self.cd.currentSensor])-min(self.cd.adcData0[self.cd.currentSensor])
        l0 = self.dataPlotsFigure.text(0.2, 0.90,'Old:{0:.3f}'.format(0.5*dd0), ha='center', va='center', transform=a.transAxes)
        l0.set_color('lightcoral')
        l2 = self.dataPlotsFigure.text(0.2, 0.88,'Old:{0:.3f}'.format(0.5*(dd1-dd0)), ha='center', va='center', transform=a.transAxes)
        if dd1-dd0>0:
            l2.set_color('green')
        else: l2.set_color('black')
#         a.set_ylim([0.97,1.03])

        self.dataPlotsCanvas.draw()
        self.dataPlotsToolbar.update()

    def re_sample(self):
        self.mode = 0
        self.get_and_plot_data()

    def auto_update(self):
        self.mode = 1
        while self.mode == 1:
            try:
                time.sleep(1)
                self.get_and_plot_data()
            except:
                break

    def plot_data2(self):
        # self.dataPlotsFigure.clf(keep_observers=True)
        for a in self.dataPlotsSubplots:
            a.cla()
        for i in range(len(self.dataPlotsSubplots)-1):
            a = self.dataPlotsSubplots[i]
            artist.setp(a.get_xticklabels(), visible=False)
            a.set_ylabel("#{:d}".format(i), rotation=0)
        a = self.dataPlotsSubplots[-1]
        a.set_xlabel(u't [us]')
        a.set_ylabel('[V]')
        nSamples = len(self.cd.adcData[0])
        x = [self.cd.adcDt * i for i in range(nSamples)]
#         print(x if len(x)<10 else x[:10])
        for i in range(len(self.dataPlotsSubplots)):
            a = self.dataPlotsSubplots[i]
            a.locator_params(axis='y', tight=True, nbins=4)
            a.yaxis.set_major_formatter(FormatStrFormatter('%7.4f'))
            a.set_xlim([0.0, self.cd.adcDt * nSamples])
            a.step(x, self.cd.adcData[i], where='post')
        self.dataPlotsCanvas.show()
        self.dataPlotsToolbar.update()
        return
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
            adcData = [[0 for i in range(nSamples)] for j in range(self.nAdcCh)]
        if sdmData == None:
            sdmData = [[0 for i in range(nSamples*self.adcSdmCycRatio)]
                          for j in range(self.nSdmCh*2)]
        for i in range(nSamples):
            for j in range(self.nAdcCh):
                idx0 = bytesPerSample - 1 - j*2
                v = ( fD[i * bytesPerSample + idx0 - 1] << 8
                    | fD[i * bytesPerSample + idx0])
                # convert to signed int
                v = (v ^ 0x8000) - 0x8000
                # convert to actual volts

                adcData[j][i] = v * adcLSB + adcVoffset
            b0 = self.nAdcCh*2
            for j in range(self.adcSdmCycRatio*self.nSdmCh*2):
                bi = bytesPerSample - 1 - b0 - int(j / 8)
                bs = j % 8
                ss = int(j / (self.nSdmCh*2))
                ch = j % (self.nSdmCh*2)
                sdmData[ch][i*self.adcSdmCycRatio + ss] = (fD[i * bytesPerSample + bi] >> bs) & 0x1
        #
        return adcData

    def save_data0(self):
            self.cd.sigproc.save_data(["sample_"+str(self.sampleID)+'_'+x+'.dat' for x in ['adc','sdm']], self.cd.adcData, self.cd.sdmData)
            self.sampleID += 1

    def save_data(self, fNames):
        with open(fNames[0], 'w') as fp:
            fp.write("# 5Msps ADC\n")
            nSamples = len(self.cd.adcData[0])
            for i in range(nSamples):
                for j in range(len(self.cd.adcData)):
                    fp.write(" {:9.6f}".format(self.cd.adcData[j][i]))
                fp.write("\n")
        with open(fNames[1], 'w') as fp:
            fp.write("# 25Msps SDM\n")
            nSamples = len(self.cd.sdmData[0])
            for i in range(nSamples):
                for j in range(len(self.cd.sdmData)):
                    fp.write(" {:1d}".format(self.cd.sdmData[j][i]))
                fp.write("\n")

#     def quit(self):
#         with self.cd.cv:
#             self.cd.quit = True
#             self.cd.cv.notify()
#         self.master.destroy()

    def update_values_display(self):
        for i in range(self.nVolts):
            self.voltsILabels[i].configure(text="{:7.3f}".format(self.cd.inputIs[i]))
            self.voltsOutputLabels[i].configure(text="{:7.3f}".format(self.cd.voltsOutput[i]))
        self.master.after(int(1000*self.cd.tI), self.update_values_display)

    def select_current_sensor(self, *args):
        with self.cd.cv:
            self.cd.currentSensor = self.sensorSelVar.get()
            print("sensor", self.cd.currentSensor)
#             self.cd.currentSensor = self.cd.currentSensor
            # load Vcodes for the specific sensor
            for i in range(self.nVolts):
                self.voltsSetCodeVars[i].set(self.cd.sensorVcodes[self.cd.currentSensor][i])
        self.set_voltage_dac_code_update()

    def set_voltage_update(self, *args):
        with self.cd.cv:
            for i in range(self.nVolts):
                self.cd.inputVs[i] = self.voltsSetVars[i].get()
                self.cd.inputVcodes[i] = self.cd.tms1mmReg.dac_volt2code(self.cd.inputVs[i])
                self.voltsSetCodeVars[i].set(self.cd.inputVcodes[i])
                # update info for the array
                self.cd.sensorVcodes[self.cd.currentSensor][i] = self.cd.inputVcodes[i]
            self.cd.vUpdated = True
            print(self.cd.inputVs)
            print(self.cd.inputVcodes)
        return True

    def save_config(self):
        if self.sensor_config is not None:
            self.sensor_config.write_config_file()

    def set_voltage_dac_code_update(self, *args):
        with self.cd.cv:
            for i in range(self.nVolts):
                self.cd.inputVcodes[i] = self.voltsSetCodeVars[i].get()
                self.cd.inputVs[i] = self.cd.tms1mmReg.dac_code2volt(self.cd.inputVcodes[i])
                self.voltsSetVars[i].set(round(self.cd.inputVs[i],4))
                # update info for the array
                self.cd.sensorVcodes[self.cd.currentSensor][i] = self.cd.inputVcodes[i]
            self.cd.vUpdated = True
            print(self.cd.inputVcodes)
        return True

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--data-ip-port", type=str, default="192.168.2.3:1024", help="data source ipaddr and port")
    parser.add_argument("-c", "--control-ip-port", type=str, default="192.168.2.3:1025", help="control system ipaddr and port")
    parser.add_argument("-a", "--aout-buf", type=int, default="1", help="AOUT buffer select, 0:AOUT1, 1:AOUT2, >1:disable both")
    parser.add_argument("-g", "--bufferx2-gain", type=int, default="2", help="BufferX2 gain")
    parser.add_argument("-s", "--sdm-mode", type=int, default="0", help="SDM working mode, 0:disabled, 1:normal operation, 2:test with signal injection")
    parser.add_argument("-t", "--buffer-test", type=int, default="0", help="Buffer test")
    parser.add_argument("-f", "--config-file", type=str, default="config/default.json", help="configuration file, will be overwritten")
    #
    args = parser.parse_args()

    dataIpPort = args.data_ip_port.split(':')
    sD = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if online: sD.connect((dataIpPort[0],int(dataIpPort[1])))

    ctrlIpPort = args.control_ip_port.split(':')
    sC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if online: sC.connect((ctrlIpPort[0],int(ctrlIpPort[1])))

    cmd = Cmd()
    cd = CommonData(cmd, dataSocket=sD, ctrlSocket=sC)
    cd.aoutBuf = args.aout_buf
    cd.x2gain = args.bufferx2_gain
    cd.sdmMode = args.sdm_mode
    cd.bufferTest = args.buffer_test
    cd.currentSensor = 4
    sensorConfig = SensorConfig(cd, online, configFName=args.config_file)

    root = tk.Tk()
    root.wm_title("Topmetal-S 1mm version x19 array Tuner")
    dataPanel = DataPanelGUI(root, cd)
    dataPanel.sensor_config = sensorConfig

    sensorConfig.start()
    root.mainloop()
    # If you put root.destroy() here, it will cause an error if
    # the window is closed with the window manager.

    sensorConfig.join()

    sC.close()
    sD.close()
