#!/usr/bin/env python
from __future__ import print_function
# #!/usr/bin/env python36
from ROOT import TChain, TF1, gStyle, gPad
from rootUtil3 import waitRootCmdX
import json
from array import array
import sys
# from os
from ROOT import gROOT
gROOT.LoadMacro("sp.C+")
# from sigproc import SigProc

from ROOT import filters_trapezoidal
import matplotlib.pyplot as plt

class FilterConfig:
    def __init__(self,fName=None):
        self.comment = ''
        self.data = []
        self.configFName = 'temp_filter_config.json' if fName is None else fName

    def load(self,fName=None):
        configFName = self.configFName if fName is None else fName
        with open(configFName, 'r') as fp:
            config = json.load(fp)
        self.comment = config['comment']
        self.data = config['data']

    def save(self,fName=None):
        configFName = self.configFName if fName is None else fName
        config = {'comment':self.comment, 'data':self.data}
        with open(configFName, 'w') as fp:
            fp.write(json.dumps(config, sort_keys=True, indent=4))

def test():
    gStyle.SetOptFit(1011)
    ch1 = TChain('tree1')
    ch1.Add('/data/Samples/TMSPlane/fpgaLin/Mar07C1a_100mV_f1000.root')

    print(ch1.GetEntries())

    nAdcCh = 20
    fc1 = FilterConfig()
    fc1.comment = 'from Mar07C1a_100mV_f1000.root. Content: (p0,p1,p2,prob,rangeL,rangeH)'
    fc1.data = [None]*nAdcCh

#     fc1.data[0] = (1,2,3,4)
#     fc1.save()
#     return

    rL = 2500
    rH = 2800
    for ich in range(nAdcCh):
#         if ich !=10: continue ## use the first for testing
        ch1.Draw('adc[{0:d}]:Iteration$>>p1(500,2350,2850)'.format(ich),'','prof')
        p1 = gPad.GetPrimitive('p1')
        fun1 = TF1('fun1','pol0+expo(1)',rL,rH)
        fun1.SetParameter(0, p1.GetBinContent(1))
        fun1.SetParameter(1, 10)
        fun1.SetParameter(2, 0)
        print(p1.GetBinContent(1))
        p1.Fit(fun1,"","",rL,rH)
        r = p1.Fit(fun1,"S","",rL,rH)
        print(ich, r.Prob())

        fc1.data[ich] = (fun1.GetParameter(0), fun1.GetParameter(1), fun1.GetParameter(2), r.Prob(), rL,rH)
#         p1.Fit('pol0+expo(1)',"","",2500,2800)
#         waitRootCmdX()
    fc1.save()

def process_C3():
    gStyle.SetOptFit(1011)
    ch1 = TChain('tree1')
    ch1.Add('data/fpgaLin/Apr22T1a_data_362.root')

    print(ch1.GetEntries())

    nAdcCh = 20
    fc1 = FilterConfig()
    fc1.comment = 'from Apr22T1a_data_363.root. Content: (p0,p1,p2,prob,rangeL,rangeH)'
    fc1.data = [None]*nAdcCh

    rL = 2500
    rH = 2800
    for ich in range(nAdcCh):
        ch1.Draw('adc[{0:d}]:Iteration$>>p1(500,2350,2850)'.format(ich),'','prof')
        p1 = gPad.GetPrimitive('p1')
        fun1 = TF1('fun1','pol0+expo(1)',rL,rH)
        fun1.SetParameter(0, p1.GetBinContent(1))
        fun1.SetParameter(1, 10)
        fun1.SetParameter(2, 0)
        print(p1.GetBinContent(1))
        p1.Fit(fun1,"","",rL,rH)
        r = p1.Fit(fun1,"S","",rL,rH)
        print(ich, r.Prob())

        fc1.data[ich] = (fun1.GetParameter(0), fun1.GetParameter(1), fun1.GetParameter(2), r.Prob(), rL,rH)
#         p1.Fit('pol0+expo(1)',"","",2500,2800)
#         waitRootCmdX()
    fc1.save()

def process_C1():
    gStyle.SetOptFit(1011)
    ch1 = TChain('tree1')
    ch1.Add('/data/Samples/TMSPlane/data/Sep19a/Sep19a_data_0.root')

    print(ch1.GetEntries())

    nAdcCh = 20
    fc1 = FilterConfig()
    fc1.comment = 'from Sep19a/Sep19a_data_0.root. Content: (p0,p1,p2,prob,rangeL,rangeH)'
    fc1.data = [None]*nAdcCh

    rL = 3000
    rH = 3200
    for ich in range(nAdcCh):
        ch1.Draw('adc[{0:d}]:Iteration$>>p1(500,2800,3300)'.format(ich),'','prof')
        p1 = gPad.GetPrimitive('p1')
        fun1 = TF1('fun1','pol0+expo(1)',rL,rH)
        fun1.SetParameter(0, p1.GetBinContent(1))
        fun1.SetParameter(1, 10)
        fun1.SetParameter(2, 0)
        print(p1.GetBinContent(1))
        p1.Fit(fun1,"","",rL,rH)
        r = p1.Fit(fun1,"S","",rL,rH)
        print(ich, r.Prob())

        fc1.data[ich] = (fun1.GetParameter(0), fun1.GetParameter(1), fun1.GetParameter(2), r.Prob(), rL,rH)
#         p1.Fit('pol0+expo(1)',"","",2500,2800)
#         waitRootCmdX()
    fc1.save()

def testFit():
    '''A test of a new method, fitting the calibration pulse wavefroms to find the proper parameter'''

    ''' We first need a good figure of merit for the tune
    1. It should be close to the amplitude in the raw waveform;
    2. It should be flat enough.

    So we will do: 1) find the largest difference between signal+background and background only, then using the nearby points to calculate the slope of the waveform.
    '''
    #Let's get one waveform first
#     fname1 = '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5c_data_20.root'
#     fname1 = '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5_data_0.root'
#     fname1 = '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5c_data_100.root'
#     fname1 = '/media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1'
#     fname1 = '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5b_data_0.root.1.1'
#     fname1 = '/data/Samples/TMSPlane/fpgaLin/Nov13b/Nov13b_HV0p5b_data_1.root'
    fname1 = '/data/Samples/TMSPlane/fpgaLin/Dec05b/Dec05b_data_15.root'
    tree1 = TChain('tree1')
    tree1.Add(fname1)
    tree1.Show(0)

    waveLen = 16384
    data1 = array('f',[0]*(waveLen*20))
    data2 = array('f',[0]*waveLen)
    #Get one entry 
    tree1.SetBranchAddress('adc',data1)

    plt.ion()
#     plt.figsize=(13, 12.5)
    plt.rc('figure', figsize=(15, 6))
    plt.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.05, hspace=0, wspace=0)
    plt.show()

    nAdcCh = 20
    ievt = -1
    ich = 5
    par1 = 300
    par2 = 400
    par3 = 80

    nevt = 0
    while True:
        print('--------------')
        print('Ch:', ich)
        print('Event:', nevt)
        print('Pars:', par1, par2, par3)
        print('--------------')
        ### get the new data when needed
        if nevt != ievt:
            tree1.GetEntry(nevt)
            ievt = nevt

        ### processing data
        data1a = data1[ich*waveLen:(ich+1)*waveLen]
        filters_trapezoidal(waveLen,data1a,data2,par1,par2, par3)
#         SigProc.filters_trapezoidal(waveLen, data1a,data2,[500, par1,par2, par3])

        ### plotting
        plt.cla()
        data1b = [x - data1a[0] for x in data1a]
        plt.plot(data1b)
        plt.plot(data2)
#         plt.show()

        ### decide the next move
        while True:
            x = raw_input("Next:")
            if x=='q': sys.exit()
            elif len(x)>0 and x[0] == 's':
                for name in x.split()[1:]:
                    dirx = os.path.dirname(name)
                    if not os.path.exists(dirx): os.makedirs(dirx)
                    plt.savefig(name)
                    print("saved figure to", name)
            elif len(x)>2 and x[:2] == 'ch':
                try:
                    ch_temp = int(x[2:]) 
                    if ch_temp<nAdcCh:
                        print("Switching to channel:", ich)
                        ich = ch_temp
                    else: print("Channel number out of range:", ch_temp, "Max:", nAdcCh-1)
                    break
                except ValueError:
                    continue
            elif len(x)>2 and x[:2] == 'fp':
                try:
                    fp_temp = x[2:].strip().split(' ')
                    par1 = int(fp_temp[0])
                    par2 = int(fp_temp[1])
                    par3 = float(fp_temp[2])

                    print("Move to use filter:", par1, par2, par3)
                    break
                except ValueError:
                    print('ValueError in fp:', fp_temp)
                    continue
            else:
                try:
                    nevt = int(x)
                except ValueError:
                    nevt = ievt+1
                break

def test_json(mode=3):

    configFName = 'test_filter_config.json'
    if mode&1:
        print("writing")
        l1 = {'comment':'', 'data':[(0,1,2),(2,3,4)]}
        with open(configFName, 'w') as fp:
            fp.write(json.dumps(l1, sort_keys=True, indent=4))
    if mode & 2:
        print("reading")
        config = None
        with open(configFName, 'r') as fp:
            config = json.load(fp)
        print(config)

if __name__ == '__main__':
#     test()
#     process_C3()
#     process_C1()
    testFit()
#     test_json()
