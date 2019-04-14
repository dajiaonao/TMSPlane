#!/usr/bin/env python36
import time
from subprocess import call

def setPulse(v,f):
    cmd = 'ssh maydaq.dhcp.lbl.gov ./fungen_ctrl.py {0:.3f} {1:d}'.format(v,f)
    call(cmd, shell=True)

class pulse_configuror:
    def __init__(self):
        pass
    def setupPulse(self,v,f=10):
        print("setting up", v, f)
        print(time.localtime())
        cmd = 'ssh maydaq.dhcp.lbl.gov ./fungen_ctrl.py {0:.3f} {1:d}'.format(v,f)
        call(cmd, shell=True)

    def rotating(self, vList, dT=20*60):
        iv = 0
        nV = len(vList)
        while True:
            try:
                self.setupPulse(vList[iv])
                iv += 1
                if iv == nV: iv = 0

                time.sleep(dT)
            except KeyboardInterrupt:
                break

def test():
    pc1 = pulse_configuror()
    pc1.rotating([0.02,0.04,0.08,0.12,0.20,0.32,0.40,0.50], 80)

if __name__ == '__main__':
    test()
