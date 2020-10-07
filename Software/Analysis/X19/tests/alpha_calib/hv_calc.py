#!/usr/bin/env python3

import sys
from ROOT import TMatrixD

script=sys.argv[0]
usage = f'{script} HV_D HV_F'



class HVDevice:
    def __init__(self,name='unknown', R=0.001):
        self.name = name
        self.R = R

class TPCSystem:
    def __init__(self,name='unknown',driftEProvider=None, collectionEProvider=None):
        self.version = "Unknown" 
        self.name = name
        self.dEProvider = driftEProvider
        self.cEProvider = collectionEProvider
        self.dU_RCFilter_R = 8 # MOhm
        self.cU_RCFilter_R = 16 # MOhm
        self.dU_R = 150 # MOhm
        self.dU_mR = 0.0976 # MOhm, ~ 100k
        self.cU_R = 30  # MOhm
        self.cU_mR = 0.0098 # MOhm, ~ 10k
        self.driftOnly = False
        self.mr2s = None
        self.ms2r = None
        self.mfun = self.mr2s

    def buildMatrix(self):
        self.mr2s = TMatrixD(2,2)
        self.mr2s[0][0] = 1. + ((self.dEProvider.R+self.dU_RCFilter_R)/self.dU_R)
        self.mr2s[0][1] = 1.
        self.mr2s[1][0] = -((self.cEProvider.R+self.cU_RCFilter_R)/self.dU_R)
        self.mr2s[1][1] = 1. +  (self.cEProvider.R+self.cU_RCFilter_R)/self.cU_R
        self.ms2r = self.mr2s.Clone()
        self.ms2r.Invert()

        self.mfun = self.mr2s

    def getConfig(self,dU,cU=None):
        if cU is None:
            return (1+(self.dEProvider.R+self.dU_RCFilter_R+self.cU_R)/self.dU_R)*dU
        else:

            mi = TMatrixD(2,1)
            mo = TMatrixD(2,1)
            mi[0][0] = dU
            mi[1][0] = cU

            mo.Mult(self.mfun,mi)
            return mo[0][0], mo[1][0]

    def showSystemConfig(self):
        print("x "*30)
        print(f"Drift device   : {self.dEProvider.name}")
        print(f"      device  R: {self.dEProvider.R} MOhm")
        print(f"Drift         R: {self.dU_R} MOhm")
        print(f"Drift RC      R: {self.dU_RCFilter_R} MOhm")
        print("= "*30)
        print(f"Collection device   : {self.cEProvider.name}")
        print(f"           device  R: {self.cEProvider.R} MOhm")
        print(f"Collection         R: {self.cU_R} MOhm")
        print(f"Collection RC      R: {self.cU_RCFilter_R} MOhm")
        print("+ "*30)

    def showConfig(self,dU,cU=None, debug=False):
        print("* "*30)
        print("*"*2+f"     {self.name}/{self.version}     "+'*'*2)
        print("* "*30)
        print()
        if cU is None:
            U1 =  (1+(self.dEProvider.R+self.dU_RCFilter_R+self.cU_R)/self.dU_R)*dU 
            print(f"Drift HV: {dU:.0f}")

            print('-'*10)
            print(f"[{self.dEProvider.name}]")
            print(f"Drift")
            print(f"{U1:.0f}")

        else:
            mi = TMatrixD(2,1)
            mo = TMatrixD(2,1)
            mi[0][0] = dU
            mi[1][0] = cU

            mo.Mult(self.mfun,mi)

            if debug:
                self.mfun.Print()
                mi.Print()
                mo.Print()


            current_D = dU/self.dU_R
            current_C = cU/self.cU_R-current_D
#             current_C = (mo[1][0]-cU)/(self.cEProvider.R+self.cU_RCFilter_R)

            print(f"Drift HV: {dU:.0f}")
            print(f"Focus HV: {cU:.0f}")

            print('-'*10)
            print(f"[{self.dEProvider.name: >10}]     [{self.cEProvider.name: >10}]")
            print(f"Drift             Focus")
            print(f"{mo[0][0]: >10.0f}     {mo[1][0]: >10.0f}     V")
            print(f"{current_D: >10.3g}     {current_C: >10.3g}    uA")
            print(f"{dU/self.dU_R*self.dU_mR: >10.3g}     {cU/self.cU_R*self.cU_mR: >10.3g}     V")

            print('\n'+"- "*10 + "Safe ramp" + '- '*10)
#             print(f"{self.cU_R/(self.cU_R+self.cEProvider.R+self.cU_RCFilter_R):.2f} < Ud[{self.dEProvider.name}]/Uc[{self.cEProvider.name}] < {(self.cU_R+self.dEProvider.R+self.dU_RCFilter_R+self.dU_R)/self.cU_R:.2f}")
#             print(f"{self.cU_R/(self.cU_R+self.cEProvider.R+self.cU_RCFilter_R):.2g} < Ud[{self.dEProvider.name}]/Uc[{self.cEProvider.name}] < {(self.cU_R+self.dEProvider.R+self.dU_RCFilter_R+self.dU_R)/self.cU_R:.2g}\n")
            print(f"{self.cU_R/(self.cU_R+self.cEProvider.R+self.cU_RCFilter_R):.2g} Uc[{self.cEProvider.name}] < Ud[{self.dEProvider.name}] < {(self.cU_R+self.dEProvider.R+self.dU_RCFilter_R+self.dU_R)/self.cU_R:.2g} Uc[{self.cEProvider.name}]\n")

#             Ud * self.cU_R/(self.cU_R+self.dEProvider.R+self.dU_RCFilter_R+self.dU_R < Uc
#             Ud > Uc * self.cU_R/(self.cU_R+self.cEProvider.R+self.cU_RCFilter_R)

def checkConfig0(Ud=None, Uc=None):
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-0'
    tpc.dU_RCFilter_R = 0
    tpc.cU_RCFilter_R = 0
    tpc.buildMatrix()

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    vO = tpc.showConfig(Ud, Uc)


def checkConfig1(Ud=None, Uc=None):
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-1'
    tpc.dU_RCFilter_R = 8
    tpc.cU_RCFilter_R = 16
    tpc.buildMatrix()
    

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    vO = tpc.showConfig(Ud, Uc)



def checkConfig2(Ud=None, Uc=None):
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-2'
    tpc.dU_RCFilter_R = 0
    tpc.cU_RCFilter_R = 0
    tpc.buildMatrix()
    

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    vO = tpc.showConfig(Ud, Uc)

def printInfo(tpc, Ud, Uc, show):
    tpc.buildMatrix()

    if len(sys.argv)>1 and sys.argv[1] == 'tpc':
        tpc.showSystemConfig()
        return

    if sys.argv[-1]=='s2r': tpc.mfun = tpc.ms2r

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    if show:
        vO = tpc.showConfig(Ud, Uc)
    else:
        return tpc.getConfig(Ud, Uc)



def checkConfig4a(Ud=None, Uc=None, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4'
    tpc.dU_RCFilter_R = 0
    tpc.cU_RCFilter_R = 0
    tpc.dU_R = 180
    tpc.cU_R = 24

    printInfo(tpc, Ud, Uc, show)

def checkConfig4b(Ud=None, Uc=None, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4b'
    tpc.dU_RCFilter_R = 0
    tpc.cU_RCFilter_R = 0
    tpc.dU_R = 180
    tpc.cU_R = 32

    printInfo(tpc, Ud, Uc, show)

def checkConfig4(Ud=None, Uc=None, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4b'
    tpc.dU_RCFilter_R = 8
    tpc.cU_RCFilter_R = 16
    tpc.dU_R = 180
    tpc.cU_R = 32

    return printInfo(tpc, Ud, Uc, show)

def checkConfig4Aug12(Ud=None, Uc=None, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4b'
    tpc.dU_RCFilter_R = 8
    tpc.cU_RCFilter_R = 16
    tpc.dU_R = 150
    tpc.cU_R = 30

    return printInfo(tpc, Ud, Uc, show)

def checkConfig4Aug12b(Ud=None, Uc=None, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4b'
    tpc.dU_RCFilter_R = 0
    tpc.cU_RCFilter_R = 0
    tpc.dU_R = 150
    tpc.cU_R = 30

    return printInfo(tpc, Ud, Uc, show)



def checkConfig4DriftOnly(Ud=None, Uc=None, cU_R=32, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=IsegHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4'
    tpc.dU_RCFilter_R = 8
    tpc.cU_RCFilter_R = 16
    tpc.dU_R = 180
    tpc.cU_R = cU_R

    return printInfo(tpc, Ud, Uc, show)

def checkConfig4DriftOnlyAug12(Ud=None, Uc=None, cU_R=10.4, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=IsegHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4'
    tpc.dU_RCFilter_R = 8
    tpc.cU_RCFilter_R = 16
    tpc.dU_R = 150
    tpc.cU_R = cU_R

    return printInfo(tpc, Ud, Uc, show)
    
def checkConfig4DriftOnlyAug13(Ud=None, Uc=None, cU_R=10.4, show=True):
    '''Used in HV spark check'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-4'
    tpc.dU_RCFilter_R = 8
    tpc.cU_RCFilter_R = 16
    tpc.dU_R = 150
    tpc.cU_R = cU_R

    return printInfo(tpc, Ud, Uc, show)
 
def checkConfig3(Ud=None, Uc=None, show=True):
    '''Check the code'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-3'
    tpc.dU_RCFilter_R = 500
    tpc.cU_RCFilter_R = 16
    tpc.buildMatrix()
    

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    if show:
        vO = tpc.showConfig(Ud, Uc)
    else:
        return tpc.getConfig(Ud, Uc)

def checkConfig3b(Ud=None, Uc=None, show=True):
    '''Using Iseg HV for drifting, but use the collection HV port, to access higher voltage'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=IsegHV)
    tpc.version = 'Config-3b'
    tpc.dU_RCFilter_R = 16
    tpc.cU_RCFilter_R = -999
#     tpc.buildMatrix()
    

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    if show:
        vO = tpc.showConfig(Ud, Uc)
    else:
        return tpc.getConfig(Ud, Uc)

def specialConfigA(Ud=None, Uc=None):
    '''Based on checkConfig3, but cU_R is set to 7.5 MOhm, 30 || 10 M from multimeter'''
    DongwenHV = HVDevice("Dongwen")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", driftEProvider=DongwenHV, collectionEProvider=IsegHV)
    tpc.version = 'Config-3'
    tpc.dU_RCFilter_R = 500
    tpc.cU_RCFilter_R = 16
    tpc.cU_R = 30
    tpc.dU_R = 141
    tpc.buildMatrix()
    

    if Ud is None:
        if len(sys.argv)<2:
            print("Ud is not provided")
            return
        Ud = int(sys.argv[1])
    if Uc is None and len(sys.argv)>2: Uc = int(sys.argv[2])

    vO = tpc.showConfig(Ud, Uc)



def testConfig():
    DongwenHV = HVDevice("Dongwen")
    picoHV = HVDevice("Pico")
    IsegHV = HVDevice("Iseg", 10)

    tpc = TPCSystem("tpc1", DongwenHV, IsegHV)
#     tpc = TPCSystem("tpc1", IsegHV, picoHV)
    tpc.dU_RCFilter_R = 500
    tpc.buildMatrix()
#     vO = tpc.showConfig(500, 1000)
    vO = tpc.showConfig(500)
    return
#     print(vO)

    print("Vd/F:Vc:VOD:VOC")  
    for vD in range(100, 5000, 100):
        for vC in range(100, 5000, 100):
            vO = tpc.getConfig(vD, vC)
            print(vD, vC, vO[0], vO[1])


def get_Vd(vd):
    '''A callable function for HV scan. Using Iseg for drifting'''
    R_D = 150. # resistor for drift field, in MOhm
    R_C = 30. # resistor for collection field, in MOhm
    R_D_extra = 10. + 8 # Other restisters in the drift HV supply chain, in MOhm ## using Iseg
    R_C_extra = 0. + 16 # Other resistors in the collection field HV chain, in MOhm ### using pAM

    hv1 = (1+(R_D_extra+R_C)/R_D)*vd

    return hv1
 

def calc_v4():
    '''New version with a general form'''
    print('v'*10, ' V4 ', 'v'*10)
    R_D = 150. # resistor for drift field, in MOhm
    R_C = 30. # resistor for collection field, in MOhm
    R_D_extra = 10. + 8 # Other restisters in the drift HV supply chain, in MOhm ## using Iseg
    R_C_extra = 0. + 16 # Other resistors in the collection field HV chain, in MOhm ### using pAM


    vd = float(sys.argv[1])
    if sys.argv[2] == '-':
        hv1 = (1+(R_D_extra+R_C)/R_D)*vd
        print(f"Drift HV: {vd:.0f}")

        print('-'*10)
        print(f"[Iseg]   [pAM]")
        print(f"Drift     Focus")
        print(f"{hv1:.0f}      -")

        print(f'\nVx = {vd*R_C/(R_D_extra+R_D+R_C):.0f}')

    else:
        vc = float(sys.argv[2])
        
        print(f"Drift HV: {vd:.0f}")
        print(f"Focus HV: {vc:.0f}")

        hv1 = vc + (1+R_D_extra/R_D)*vd
        hv2 = vc + (vc/R_C - vd/R_D)*R_C_extra

        print('-'*10)
        print(f"[Iseg]   [pAM]")
        print(f"Drift     Focus")
        print(f"{hv1:.0f}      {hv2:.0f}")

def calc_v3b():
    '''Based on v3, but use Iseg for drifting and Dongwen for focusing'''
    print('v'*10, ' V3B ', 'v'*10)
    R_D = 150. # resistor for drift field, in MOhm
    R_C = 30. # resistor for collection field, in MOhm
    R_D_extra = 10. + 8 # Other restisters in the drift HV supply chain, in MOhm
    R_C_extra = 0. + 16 # Other resistors in the collection field HV chain, in MOhm


    vd = float(sys.argv[1])
    if sys.argv[2] == '-':
        hv1 = (1+(R_D_extra+R_C)/R_D)*vd
        print(f"Drift HV: {vd:.0f}")

        print('-'*10)
        print(f"[Iseg]   [Dongwen]")
        print(f"Drift     Focus")
        print(f"{hv1:.0f}      -")

        print(f'\nVx = {vd*R_C/(R_D_extra+R_D+R_C):.0f}')

    else:
        vc = float(sys.argv[2])
        
        print(f"Drift HV: {vd:.0f}")
        print(f"Focus HV: {vc:.0f}")

        hv1 = vc + (1+R_D_extra/R_D)*vd
        hv2 = vc + (vc/R_C - vd/R_D)*R_C_extra

        print('-'*10)
        print(f"[Iseg]   [Dongwen]")
        print(f"Drift     Focus")
        print(f"{hv1:.0f}      {hv2:.0f}")


def calc_v3():
    '''New version with a general form'''
    print('v'*10, ' V3 ', 'v'*10)
    R_D = 150. # resistor for drift field, in MOhm
    R_C = 30. # resistor for collection field, in MOhm
    R_D_extra = 0. + 8 # Other restisters in the drift HV supply chain, in MOhm
    R_C_extra = 10. + 16 # Other resistors in the collection field HV chain, in MOhm
#     R_D_extra = 0. # Other restisters in the drift HV supply chain, in MOhm
#     R_C_extra = 10. # Other resistors in the collection field HV chain, in MOhm


    vd = float(sys.argv[1])
    if sys.argv[2] == '-':
        hv1 = (1+(R_D_extra+R_C)/R_D)*vd
        print(f"Drift HV: {vd:.0f}")

        print('-'*10)
        print(f"[Dongw]   [Iseg]")
        print(f"Drift     Focus")
        print(f"{hv1:.0f}      -")

        print(f'\nVx = {vd*R_C/(R_D_extra+R_D+R_C):.0f}')

    else:
        vc = float(sys.argv[2])
        
        print(f"Drift HV: {vd:.0f}")
        print(f"Focus HV: {vc:.0f}")

        hv1 = vc + (1+R_D_extra/R_D)*vd
        hv2 = vc + (vc/R_C - vd/R_D)*R_C_extra

        print('-'*10)
        print(f"[Dongw]   [Iseg]")
        print(f"Drift     Focus")
        print(f"{hv1:.0f}      {hv2:.0f}")

def calc_v2():
    '''Based on v1, but the resistance between the '''
    print('x'*10, ' V2 ', 'x'*10)
    if len(sys.argv)<3:
       print(usage)

    device1 = ('')

    if sys.argv[2] == '-':
        hv1 = float(sys.argv[1])
        print(f"Drift HV: {hv1:.0f}")

        scale1 = 188./150
        hv2 = 0

        print('-'*10)
        print(f"[Dongw]   [Iseg]")
        print(f"Drift     Focus")
        print(f"{hv2 + hv1*scale1:.0f}      -")

    else:
        hv1 = float(sys.argv[1])
        hv2 = float(sys.argv[2])

        scale1 = 158./150 ### 165 MOhm for Drifting, 8 MOhm in HV filter, inner resistance of Dongwen neglected
        scale2 = 56./30 ### 15 MOhm on the TPC, 16 MOhm in HV filter, and 10 MOhm inside the Iseg device
        scale3 = 26./150


        print(f"Drift HV: {hv1:.0f}")
        print(f"Focus HV: {hv2:.0f}")

        print('-'*10)
        print(f"[Dongw]   [Iseg]")
        print(f"Drift     Focus")
        print(f"{hv2 + hv1*scale1:.0f}      {hv2*scale2-hv1*scale3:.0f}")
def calc_v1():
    if len(sys.argv)<3:
       print(usage)

    device1 = ('')


    if sys.argv[2] == '-':
        hv1 = float(sys.argv[1])
        print(f"Drift HV: {hv1:.0f}")

        scale1 = 188./165
        hv2 = 0

        print('-'*10)
        print(f"[Dongw]   [Iseg]")
        print(f"Drift     Focus")
        print(f"{hv2 + hv1*scale1:.0f}      -")

    else:
        hv1 = float(sys.argv[1])
        hv2 = float(sys.argv[2])

        scale1 = 173./165 ### 165 MOhm for Drifting, 8 MOhm in HV filter, inner resistance of Dongwen neglected
        scale2 = 41./15 ### 15 MOhm on the TPC, 16 MOhm in HV filter, and 10 MOhm inside the Iseg device
        scale3 = 26./165

        print(f"Drift HV: {hv1:.0f}")
        print(f"Focus HV: {hv2:.0f}")

        print('-'*10)
        print(f"[Dongw]   [Iseg]")
        print(f"Drift     Focus")
        print(f"{hv2 + hv1*scale1:.0f}      {hv2*scale2-hv1*scale3:.0f}")

if __name__ == '__main__':
#     calc_v2()
#     calc_v4()
#     testConfig()
#     checkConfig0()
#     checkConfig1()
#     checkConfig3()
#     checkConfig4a()
#    checkConfig4b()
#    checkConfig4()
#     checkConfig4DriftOnly()
#     checkConfig4DriftOnlyAug12() #drift only default
#     checkConfig4DriftOnlyAug13()
     checkConfig4Aug12() # HV default
#     checkConfig4Aug12b() # HV glass default
#     checkConfig3b()
#     specialConfigA()
#     checkConfig2()
#     calc_v3()
#     calc_v3b()
#     calc_v5()
