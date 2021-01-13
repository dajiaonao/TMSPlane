#!/usr/bin/env python3
'''For Rigol DG4162. The device should be configured to use ip 192.168.2.3 and subnet mask 255.255.255.0
Documentation: https://www.rigolna.com/products/waveform-generators/dg4000/
'''
import socket
import time
import sys
import math

class Handle:
    def __init__(self, s):
        self.s = s

    def write(self, cmd, dt=0.5):
        print('sending',cmd)
#         self.s.send(bytes(cmd+'\n','UTF-8'))
        self.s.sendall(bytes(cmd+'\n','UTF-8'))
        if dt is not None: time.sleep(dt)

    def read(self,cmd,ndata=-1):
        print('reading',cmd)
        self.s.send(bytes(cmd+'\n','UTF-8'))

        a = self.s.recv(1024)
        while len(a)<ndata:
            a += self.s.recv(1024)

        return a


class Rigol:
    def __init__(self):
        self.addr = '192.168.2.5:5555'
        self.s3 = None
        self.handle = None

        self.pulseV = -1

    def connect(self):
        a = self.addr.split(':')
        Rig_hostname = a[0]                    #rigol dds ip address
        Rig_port = int(a[1])                                 #rigol dds instrument port
        self.s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #init local socket handle
        self.s3.connect((Rig_hostname, Rig_port))

        self._instr = Handle(self.s3)


    def raiseT_test(self, nDt, hV=0.05, lV=0):
        '''
        The freqency be fixed to 100 Hz. dt = 1/100/16000 ~= 0.625 us. Half for decay and the other half to gradually reset signal.
        Range for nDt is [0, 2000], corresponding to [0, 1]ms
        '''
        self._instr.write(":OUTPut2 OFF")
        freq = 100
        self._instr.write(":SOURce2:FUNCtion USER")
        ### source2 for trigger: 3.3V Square output
        self._instr.write(":SOURce2:FREQ %g" % freq)
        ### [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:HIGH <voltage>|MINimum|MAXimum
        self._instr.write(":SOURce2:VOLTage:HIGH %g" % hV)
        self._instr.write(":SOURce2:VOLTage:LOW %g" % lV)

        N0 = 200 ### start with n1 HV points
        N1 = 1000 - N0 - nDt ### N1 points for decay
        N2 = 600 ### N2 points for reset. N1+N2 = 20000, the limit from the device is N1+N2<=32768.
        NT = N2/10

        dataI = []
        dataI += [16383]*N0
        dataI += [int(16383*(1-n/nDt)) for n in range(nDt)]
        dataI += [0]*N1
        dataI += [int(16383*(1.-math.exp(-n/NT))) for n in range(N2)]
#         print(len(dataI))

#         dataI = dataI[1000:2000]

        ndata = len(dataI)*2
        nndata = len(str(ndata))
        datab = bytes(':DATA:DAC VOLATILE,#{0:d}{1:d}'.format(nndata, ndata),'UTF-8')
        for x in dataI: datab += x.to_bytes(2, byteorder = 'big')
        print(len(datab),datab[:30])
#         print(len(data))
#         print(''.join(data))
#         return
#         ndata = bytes(len(data))

#         dataS = '#{0:d}'.format(len(ndata))+str(ndata)
#         print(dataS)
#         data = [':DATA:DAC VOLATILE']
#         data += ',#516000'
#         data += ''.join([])
#         self._instr.write(', '.join(data))
#         self._instr.write(":DATA:DAC VOLATILE,#516000"+''.join(data))
        self._instr.s.sendall(datab)
#         self._instr.write(":OUTPut2 ON")

    def calibration(self, freq=100):
        hV = 0.3
        lV = 0.2
        '''for calibration'''
        ### [:SOURce<n>]:PHASe[:ADJust] <phase>|MINimum|MAXimum
        ### [:SOURce<n>]:APPLy:SQUare [<freq>[,<amp>[,<offset>[,<phase>]]]] //:APPLy:SQUare 100,2.5,0.5,90

        ### source1 for trigger: 3.3V Square output
        self._instr.write(":SOURce1:APPLy:SQUare {0:d},3.3,1.65,0".format(freq))

        ### source2 for trigger: 3.3V Square output
        self._instr.write(":SOURce2:FUNCtion USER")
        self._instr.write(":SOURce2:FREQ %g" % freq)
        ### [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:HIGH <voltage>|MINimum|MAXimum
        self._instr.write(":SOURce2:VOLTage:HIGH %g" % hV)
        self._instr.write(":SOURce2:VOLTage:LOW %g" % lV)

#         self._instr.write(":PA:OFFSet ON".format(offset))                       #set output offset, default value 1V 
#         self._instr.write(":PA:OFFSet:VALUe {0:.2f}".format(offset))                       #set output offset, default value 1V 

#         a = self._instr.read(':PA:OFFSet:VALUe?')
#         print a

        string = ':DATA:DAC VOLATILE,'
#         string += ','.join(['0' for i in range(100)]+['{0:d}'.format(int(x*16384/120)) for x in range(120)]+['16384']*20)
        string += ','.join(['0' for i in range(100)]+['{0:d}'.format(int(x*16384/140)) for x in range(140)]+['16384']*40)
        print(string)
        self._instr.write(string)

        ### coupling
        ## :COUPling:CHannel:BASE CH1|CH2
        ## :COUPling:CHannel:BASE?
        ## :COUPling:FREQuency[:STATe] ON|OFF
        ## :COUPling:FREQuency[:STATe]?
        ## :COUPling:FREQuency:DEViation <deviation>
        ## :COUPling:FREQuency:DEViation?
        ## :COUPling:PHASe[:STATe] ON|OFF
        ## :COUPling:PHASe[:STATe]? 
        ## :COUPling:PHASe:DEViation <deviation>
        ## :COUPling:PHASe:DEViation?
        ## :COUPling[:STATe] ON|OFF
        ## :COUPling[:STATe]?
        ## :COUPling:AMPL[:STATe] ON|OFF
        ## :COUPling:AMPL[:STATe]?  
        ## :COUPling:AMPL:DEViation <deviation>
        ## :COUPling:AMPL:DEViation?

        self._instr.write(":COUPling:CHannel:BASE CH1")
        self._instr.write(":COUPling:PHASe ON")
        self._instr.write(":COUPling:PHASe:DEViation 340")

        ### output
        ## :OUTPut[<n>][:STATe] ON|OFF
        ## :OUTPut[<n>][:STATe]?
        self._instr.write(":OUTPut1 ON")
        self._instr.write(":OUTPut2 ON")

    def setPhaseDev(self, ph=340):
        self._instr.write(":COUPling:PHASe:DEViation {0:d}".format(ph))

    def setPulseV(self, dV=0.1, lV=0.2):
        if len(sys.argv)>1: dV = float(sys.argv[1])
        self._instr.write(":SOURce2:VOLTage:HIGH {0:g}".format(dV+lV))
        self._instr.write(":SOURce2:VOLTage:LOW {0:g}".format(lV))

    def tune(self):
#         self._instr.write(":COUPling:PHASe:DEViation 340")
        var1 = sys.argv[1]
        self._instr.write(":COUPling:PHASe:DEViation "+var1)

    def normal_run(self):
        '''normal_run'''
        pass

    def test_volatile(self):
        freq = 500
        offset = 0.5
        self._instr.write(":SOURce1:FUNCtion USER")
        self._instr.write(":SOURce1:FREQ %g" % freq)
        self._instr.write(":PA:OFFSet ON".format(offset))                       #set output offset, default value 1V 
        self._instr.write(":PA:OFFSet:VALUe {0:.2f}".format(offset))                       #set output offset, default value 1V 

        a = self._instr.read(':PA:OFFSet:VALUe?')
#         a = self._instr.read(':PA:OFFSet?')
#         self.s3.send(':PA:OFFSet:VALUe?\n')
#         a = self.s3.recv(20)
        print(a)
#         self._instr.write("FUNC:USER VOLATILE")

#         return
        string = ':DATA:DAC VOLATILE,'
        string += ','.join(['{0:d}'.format(int(x*16300/120)) for x in range(120)])
#         string += ','.join(['{0:.2f}'.format(1.-0.01*x) for x in range(20)])

        print(string)
        self._instr.write(string)

    def setup_tail_pulse3(self, freq=100, xp=16, np=1024, alpha=0.01):
        self._instr.write("FUNC USER")
        time.sleep(0.5)
        self._instr.write("FREQ %g" % freq)
        time.sleep(0.5)

        amax = 16383
        vals=[0 for i in range(np)]
        k = np/1024.

        alpha /= k
        pp = 0 ### the pulse will always be at around 0.5 ms of the sample
        dp = pp+int(0.00002*freq*np) ### keep high voltage for 0.01 ms
        for i in range(pp): vals[i] = int(amax*(1-math.exp(-(i+np-dp)*alpha)))
        for i in range(dp,np): vals[i] = int(amax*(1-math.exp(-(i-dp)*alpha)))

        string = "DATA:DAC VOLATILE"
        for i in range(np):
            string += (",%d"% vals[i])
#         print(string)
        self._instr.write(string)
        time.sleep(1.0)
        self._instr.write("FUNC:USER VOLATILE")
        time.sleep(0.5)

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

    def test1(self, freq):
        self.s3.send(":SOURce1:FREQuency %s\n"%freq)          #set output frequency, default value 1MHz 
        self.s3.send(":SOURce1:VOLTage 1\n")                 #set output amplitude
        self.s3.send(":PA:OFFSet:VALUe 1\n")                       #set output offset, default value 1V 

    def tuneConfig(self,fq=1250, dV=0.2):
        self.calibration(fq)
        self.setPhaseDev(300)
        self.setPulseV(dV)

    def setTTPulse(self, dV, fT=None, fq=100, ch=None):
        '''Set to produce pulse with pp amplitude dV [V], falling time fT [us], and frequency fq [Hz]'''
        chan = '' if ch is None else f':SOURce{ch}'

        if fT is None:
            self._instr.write(chan+f":APPLy:SQUare {fq},{dV},{dV*0.5+0.01}") #[:SOURce<n>]:APPLy:SQUare [<freq>[,<amp>[,<offset>[,<phase>]]]]
        else:
            self._instr.write(chan+f":APPLy:PULSe {fq},{dV},{dV*0.5+0.01}") #[:SOURce<n>]:APPLy:PULSe [<freq>[,<amp>[,<offset>[,<delay>]]]]
            time.sleep(0.5)
            self._instr.write(chan+f":PULSe:TRANsition:TRAiling {fT*1e-6}")#[:SOURce<n>]:PULSe:TRANsition:TRAiling <seconds>|MINimum|MAXimum
        time.sleep(0.5)
        
        if ch is None: ch = 1
        self._instr.write(f":OUTPut{ch} ON")

def test2():
    r1 = Rigol()
    r1.connect()
#     r1.setTTPulse(0.02,2,1000)
    r1._instr.write(":OUTPut1 OFF")
    time.sleep(0.5)
    print(r1._instr.read(":OUTPUT1?"))
#     r1.raiseT_test(100)
#     r1.test_volatile()
#     r1.calibration()
#     r1.setPulseV(0.2)
#     r1.tune()
#     r1.test(20)

def optimization(fq=1250):
    r1 = Rigol()
    r1.connect()
#     r1.calibration(fq)
    r1.setPhaseDev(300)
#     r1.setPulseV(0.2)

def tuneTestRigo(fq=1250,dV=0.2, phase=300):
    r1 = Rigol()
    r1.connect()
    r1.calibration(fq)
    r1.setPhaseDev(phase)
    r1.setPulseV(dV)

def test1():
    freq = 50
    Rig_hostname = '192.168.2.5'                    #rigol dds ip address
    Rig_port = 5555                                 #rigol dds instrument port
    s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #init local socket handle
    s3.connect((Rig_hostname, Rig_port))

    s3.send(":SOURce1:FREQuency %s\n"%freq)          #set output frequency, default value 1MHz 
    s3.send(":SOURce1:VOLTage 1\n")                 #set output amplitude
    s3.send(":PA:OFFSet:VALUe 1\n")                       #set output offset, default value 1V 
#    s3.send("OUTPut ON\n")                 #turn on channel1

    s3.close()

if __name__ == '__main__':
#     tuneTest()
    test2()
    #optimization()
