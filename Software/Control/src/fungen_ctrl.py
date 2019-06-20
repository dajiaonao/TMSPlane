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

#             print(usbtmc.list_devices())
#             print('------------')
#             print(self._instr.ask("*IDN?"))

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
#         alpha = 0.001
        vals=[0 for i in xrange(np)]
#         for i in range(1000,np): vals[i] = int(amax*(1-math.exp(-(i-100)*alpha)))
# #         for i in range(8):
# #             for j in range(np/8):
# #                 vals[i*np/8+j] = amax/8.*i
# #         for i in range(0,100): vals[i] = amax
# #         for i in range(100): vals[np-100-i] = amax
# #         for i in range(100,np): vals[i] = int(amax*(1-math.exp(-(i-100)*alpha)))
        k = np/1024.
# 
        alpha /= k
        pp = int(0.0005*freq*np)%np ### the pulse will always be at around 0.5 ms of the sample
        dp = pp+int(0.00002*freq*np) ### keep high voltage for 0.01 ms
        for i in range(pp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
        for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

        string = "DATA:DAC VOLATILE"
        for i in xrange(np):
            string += (",%d"% vals[i])
        print(string)
        self._instr.write(string)
        time.sleep(1.0)
        self._instr.write("FUNC:USER VOLATILE")
        time.sleep(0.5)
#         print(self._instr.ask("DATA:ATTRibute:POINts? VOLATILE"))

    def setup_tail_pulse3(self, freq=100, xp=16, np=1024, alpha=0.01):
        self._instr.write("FUNC USER")
        time.sleep(0.5)
        self._instr.write("FREQ %g" % freq)
        time.sleep(0.5)

        amax = 16383
        vals=[0 for i in xrange(np)]
        k = np/1024.

        alpha /= k
        pp = 0 ### the pulse will always be at around 0.5 ms of the sample
        dp = pp+int(0.00002*freq*np) ### keep high voltage for 0.01 ms
        for i in range(pp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
        for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

        string = "DATA:DAC VOLATILE"
        for i in xrange(np):
            string += (",%d"% vals[i])
#         print(string)
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

    def set_dc(self,v=0.1):
        self._instr.write("APPL:DC DEF,DEF,{0:.2f}".format(v))
        self._instr.write("OUTP ON")

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


    def data_pusle_mode(self, v, f):
        '''Square wave, usualy low frequency'''

    def opt_pulse_mode(self):
        pass
    def use_mode(self, args):
        cmd = getattr(self, args[0]+'_mode')
        if cmd:
           pass 

    def close(self):
        self._instr.close()

def main0():
    hV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    fQ = int(sys.argv[2]) if len(sys.argv)>2 else 100
    np = int(sys.argv[3]) if len(sys.argv)>3 else 1024

    print("Setting high V: {0:.3f} and Frequency {1:d}".format(hV, fQ))
    if hV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hV))
        sys.exit(1)

#     test(fQ, 64, np, 0.01)
#     return

    fg = DG1022()
    fg.set_voltage(0.2, 0.2+hV)
    fg.setup_tail_pulse2(fQ, 64, np, 0.01)
#    fg.set_phase(100)
    fg.turn_on_output()
#     fg.setupCH2(fQ,0.0,hV,'SIN')
    fg.setupCH2(fQ,0.0,hV,'StairUp')
#     fg.setupCH2(fQ,0.0,hV,'VOLATILE')
#

def main_test():
    hV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    fQ = int(sys.argv[2]) if len(sys.argv)>2 else 100
    np = int(sys.argv[3]) if len(sys.argv)>3 else 1024

    print("Setting high V: {0:.3f} and Frequency {1:d}".format(hV, fQ))
    if hV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hV))
        sys.exit(1)

    fg = DG1022()
    fg._instr.write("APPLy:SQUare {0:d},{1:.3f},{2:.3f}".format(fQ, hV, 0.2+0.5*hV))
    time.sleep(1)

    n = 27500.
    print(math.modf(n/(5000000./fQ)), )
    a = math.modf(n*fQ/5000000.)
    phase = a[0]*360 - 180
    print(phase)
    ## CH2 --> Test pulse for trigger
    fg._instr.write("APPLy:SQUare:CH2 {0:d},0.04,0.02".format(fQ))
    time.sleep(1)
    fg._instr.write("PHASe:CH2 {0:d}".format(int(phase)))
#     fg._instr.write("PHASe:CH2 -70")
    time.sleep(1)

    fg._instr.write("OUTP ON")
    time.sleep(1)
    fg._instr.write("OUTP:CH2 ON")
    time.sleep(1)

    fg._instr.write("PHASe:ALIGN")
    time.sleep(1)

    fg.close()


def main():
    hV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    fQ = int(sys.argv[2]) if len(sys.argv)>2 else 100
    np = int(sys.argv[3]) if len(sys.argv)>3 else 1024

    print("Setting high V: {0:.3f} and Frequency {1:d}".format(hV, fQ))
    if hV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hV))
        sys.exit(1)

#     test(fQ, 64, np, 0.01)
#     return

    fg = DG1022()
    fg.set_voltage(0.2, 0.2+hV)
    fg.setup_tail_pulse(fQ, 64, np, 0.004)
#    fg.set_phase(100)
#     fg.turn_on_output()
#     fg.setupCH2(fQ,0.0,hV,'SIN')
#     fg.setupCH2(fQ,0.0,hV,'StairUp')
#     fg.setupCH2(fQ,0.0,hV,'VOLATILE')
#     fg.turn_on_trigger()
#     fg.setupCH2(fQ,0.0,hV,'PPulse')

    ## CH2 --> Test pulse for trigger
    fg._instr.write("APPLy:SQUare:CH2 {0:d},0.04,0.02".format(fQ))
    time.sleep(1)
    fg._instr.write("PHASe:CH2 -70")
    time.sleep(1)

    fg._instr.write("OUTP ON")
    time.sleep(1)
    fg._instr.write("OUTP:CH2 ON")
    time.sleep(1)

    fg._instr.write("PHASe:ALIGN")
    time.sleep(1)

    fg.close()

def calib_test():
    '''Only change the input pulse voltage'''
    dV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    fQ = int(sys.argv[2]) if len(sys.argv)>2 else 100
    hVDC = float(sys.argv[3]) if len(sys.argv)>3 else 0.2
    np = 1024

    if hVDC < 0.5*dV: hVDC = 0.5*dV
    if hVDC+0.5*dV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hVDC+0.5*dV))
        sys.exit(1)
    print("Setting low V: {0:.3f}, high V: {1:.3f}".format(hVDC-0.5*dV, hVDC+0.5*dV))

    fg = DG1022()
    fg.set_voltage(hVDC-0.5*dV, hVDC+0.5*dV)
    fg.setup_tail_pulse3(fQ, 64, np, 0.01)
    fg._instr.write("PHASe 0")
    time.sleep(0.5)
#     fg._instr.write("APPLy:SQUare:CH2 {0:d},0.04,0.02".format(fQ))
    fg._instr.write("APPLy:SQUare:CH2 10,0.04,0.02")
    time.sleep(0.5)
    fg._instr.write("PHASe:CH2 -70")
    time.sleep(0.5)
    fg._instr.write("PHASe:ALIGN")
    time.sleep(0.5)

    fg.close()


def test2():
    '''Only change the input pulse voltage'''
    dV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    hVDC = float(sys.argv[2]) if len(sys.argv)>2 else 0.2


    if hVDC < 0.5*dV: hVDC = 0.5*dV
    if hVDC+0.5*dV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hVDC+0.5*dV))
        sys.exit(1)
    print("Setting low V: {0:.3f}, high V: {1:.3f}".format(hVDC-0.5*dV, hVDC+0.5*dV))

    fg = DG1022()
    fg.set_voltage(hVDC-0.5*dV, hVDC+0.5*dV)
#     fg._instr.write("PHASe 179")
    fg._instr.write("PHASe:ALIGN")

    fg.close()

def test1():
    fg = DG1022()
    fg.turn_off_trigger()
    fg.close()


def set_ch1_dc():
    fg = DG1022()
    fg.set_dc()
    fg.close()

def test(freq=100, xp=16, np=1024, alpha=0.01):
    amax = 16383
    vals=[0 for i in xrange(np)]

    alpha *= np/1024.
    pp = int(0.0005*freq*np)%np ### the pulse will always be at around 0.5 ms of the sample
    dp = pp+int(0.00002*freq*np) ### keep high voltage for 0.01 ms
    for i in range(pp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
    for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

#     amax = 16383
#     vals=[0 for i in xrange(np)]
# 
#     pp = int(0.0005*freq*np)%np
#     dp = pp+int(0.00001*freq*np)
#     for i in range(pp-xp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
#     for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

    string = "DATA:DAC VOLATILE"
    for i in xrange(np):
        string += (",%d"% vals[i])

    from matplotlib import pyplot as plt
    plt.plot(vals)
    plt.show()

def optimization_config():
    fQ = 2500
    fg = DG1022()
    ## CH1 --> guard ring
#     fg.set_voltage(0.2,0.26)
#     fg.set_voltage(0.2,0.25)
    fg.set_voltage(0.2,0.5)
#     fg.setup_tail_pulse2(fQ, 64, 1024, 0.01)
    fg.setup_tail_pulse(fQ, 64, 1024, 0.006)
#     fg.setup_tail_pulse(fQ, 64, 1024, 0.01)
#     fg._instr.write("PHASe 0")
    time.sleep(1)

    nShift = 0
    phase = -50#((5000000/fQ) % 360)-180

    ## CH2 --> Test pulse for trigger
    fg._instr.write("APPLy:SQUare:CH2 {0:d},0.01,0.005".format(fQ))
    time.sleep(1)
    fg._instr.write("PHASe:CH2 {0:d}".format(phase))
    time.sleep(1)

    fg._instr.write("OUTP ON")
    time.sleep(1)
    fg._instr.write("OUTP:CH2 ON")
    time.sleep(1)

    fg._instr.write("PHASe:ALIGN")
    time.sleep(1)


    fg.close()

def physics_mode():
    ## 0.04, 0.2, 0.12, 0.32, 0.4, 0.02
    hV = float(sys.argv[1]) if len(sys.argv)>1 else 0.05
    hVlow = 0.2
    if hV > 1:
        print('The demanded high V is too high: {0:.3f}. Abort...'.format(hV))
        sys.exit(1)
    print("Setting low V: {0:.3f}, high V: {1:.3f}".format(hVlow, hVlow+hV))

#     return

    fQ = 10
    fQ1 = fQ
#     fQ1 = 100
    fg = DG1022()
    ## CH1 --> guard ring
#     fg.set_dc(0.2)
#     hV = 0.2
    fg._instr.write("APPLy:SQUare {0:d},{1:.3f},{2:.3f}".format(fQ1, hV, hVlow+0.5*hV))
    time.sleep(1)

    ## CH2 --> Test pulse for trigger
    fg._instr.write("APPLy:SQUare:CH2 {0:d},0.01,0.005".format(fQ))
    time.sleep(1)


    n = 2750.
    print(math.modf(n/(5000000./fQ)), )
    a = math.modf(n*fQ/5000000.)
    phase = a[0]*360
    if phase>180: phase = phase - 360
    print(phase)
    fg._instr.write("PHASe:CH2 {0:d}".format(int(phase)))
    time.sleep(1)

    fg._instr.write("OUTP ON")
    time.sleep(1)
    fg._instr.write("OUTP:CH2 ON")
    time.sleep(1)

    fg._instr.write("PHASe:ALIGN")
    time.sleep(1)

    fg.close()





if __name__ == "__main__":
#     calib_test()
#     optimization_config()
#     test2()
#     test1()
#     main()
#     main_test()
    physics_mode()
#     set_ch1_dc()
    #test()
