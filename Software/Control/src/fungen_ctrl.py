#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

## @package fungen_ctrl
# Control the function generator
#

from __future__ import print_function
import time
import os
import sys
import shutil
import math
# use either usbtmc or NI Visa
try:
    import usbtmc
except:
    import visa

## Rigol DG1022
class DG1022(object):

    ## @var handle to instrument
    _instr = None

    ## Initialization
    def __init__(self):
        try:
            rm = visa.ResourceManager()
            rm.list_resources()                 # list available instruments
            self._instr = rm.open_resource('USB0::0x1AB1::0x0588::DG1D131402088::INSTR')
        except:
            self._instr = usbtmc.Instrument(0x1ab1, 0x0588) # RIGOL TECHNOLOGIES,DG1022 ,DG1D131402088
            self._instr.timeout = 10

    ## Generate tail-pulse and write into instrument's memory
    # @param xp number of samples before the edge
    # @param np total number of samples for the pulse
    # @param alpha exp-decay coefficient in exp(-alpha * (i - xp))
    def setup_tail_pulse(self, freq=100, xp=16, np=1024, alpha=0.01):
        self._instr.write("FUNC USER")
        time.sleep(0.5)
        self._instr.write("FREQ %g" % freq)
        time.sleep(0.5)

        amax = 16383
        vals=[0 for i in xrange(np)]
        for i in xrange(np):
            if i<xp:
                vals[i] = amax
            else:
                vals[i] = int(amax*(1-math.exp(-(i-xp)*alpha)))
        string = "DATA:DAC VOLATILE"
        for i in xrange(np):
            string += (",%d"% vals[i])
        self._instr.write(string)
        time.sleep(1.0)
        self._instr.write("FUNC:USER VOLATILE")
        time.sleep(0.5)

    def setup_tail_pulse2(self, freq=100, xp=16, np=1024, alpha=0.01):
        self._instr.write("FUNC USER")
        time.sleep(0.5)
        self._instr.write("FREQ %g" % freq)
        time.sleep(0.5)

        amax = 16383
        vals=[0 for i in xrange(np)]

        pp = int(0.0005*freq*np)%np ### the pulse will always be at around 0.5 ms of the sample
        dp = pp+int(0.00002*freq*np) ### keep high voltage for 0.01 ms
        for i in range(pp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
        for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

        string = "DATA:DAC VOLATILE"
        for i in xrange(np):
            string += (",%d"% vals[i])
        # print(string)
        self._instr.write(string)
        time.sleep(1.0)
        self._instr.write("FUNC:USER VOLATILE")
        time.sleep(0.5)


    def set_frequency(self, freq=100.0):
        self._instr.write("FREQ %g" % freq)
        time.sleep(0.5)

    def set_voltage(self, vLow=0.0, vHigh=1.0):
        self._instr.write("VOLT:UNIT VPP")
        time.sleep(0.5)
        self._instr.write("VOLTage:LOW %g" % vLow)
        time.sleep(0.5)
        self._instr.write("VOLTage:HIGH %g" % vHigh)
        time.sleep(0.5)

    def turn_on_output(self):
        self._instr.write("OUTP:LOAD 50")
        time.sleep(0.5)
        self._instr.write("OUTP ON")
        time.sleep(0.5)

    def set_phase(self,ph):
        self._instr.write("PM:DEViation {0:d}".format(ph))
        time.sleep(0.5)

    def setupCH2(self, freq, vLow, vHigh, userFun, phase=0):
        self._instr.write("FUNC:CH2 USER")
        self._instr.write("FUNC:USER:CH2 %s" % userFun)
#         self._instr.write("FUNC:CH2 %s" % userFun)
        time.sleep(0.5)

        self._instr.write("FREQ:CH2 %g" % freq)
        time.sleep(0.5)

        self._instr.write("VOLT:UNIT:CH2 VPP")
        time.sleep(0.5)
        self._instr.write("VOLTage:LOW:CH2 %g" % vLow)
        time.sleep(0.5)
        self._instr.write("VOLTage:HIGH:CH2 %g" % vHigh)
        time.sleep(0.5)
        self._instr.write("COUP ON")
        self._instr.write("COUP:BASE:CH1")
        self._instr.write("COUP:PHASEDEV %d" % phase)
        time.sleep(0.5)

        self._instr.write("OUTP:CH2 ON")

    def turn_on_trigger(self):
        self._instr.write("OUTPut:SYNC ON")
        time.sleep(0.5)
        self._instr.write("OUTPut:TRIGger ON")
        time.sleep(0.5)

    def turn_off_trigger(self):
        self._instr.write("OUTPut:SYNC OFF")
        time.sleep(0.5)
        self._instr.write("OUTPut:TRIGger OFF")
        time.sleep(0.5)

    def close(self):
        self._instr.close()

def main():
    hV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    fQ = int(sys.argv[2]) if len(sys.argv)>2 else 100

    print("Setting high V: {0:.3f} and Frequency {1:d}".format(hV, fQ))
    if hV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hV))
        sys.exit(1)


    fg = DG1022()
    fg.set_voltage(0.0, hV)
    fg.setup_tail_pulse2(fQ, 64, 1024, 0.01)
#    fg.set_phase(100)
    fg.turn_on_output()
#     fg.setupCH2(fQ,0.0,hV,'SIN')
    fg.setupCH2(fQ,0.0,hV,'StairUp')
#     fg.turn_on_trigger()
#     fg.setupCH2(fQ,0.0,hV,'PPulse')
    fg.close()


def test1():
    fg = DG1022()
    fg.turn_off_trigger()
    fg.close()


def test(freq=100, xp=16, np=1024, alpha=0.01):
    amax = 16383
    vals=[0 for i in xrange(np)]

    pp = int(0.0005*freq*np)%np
    dp = pp+int(0.00001*freq*np)
    for i in range(pp-xp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
    for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

    string = "DATA:DAC VOLATILE"
    for i in xrange(np):
        string += (",%d"% vals[i])

    from matplotlib import pyplot as plt
    plt.plot(vals)
    plt.show()

if __name__ == "__main__":
#     test1()
    main()
    #test()
