#!/usr/bin/env python
from ROOT import *
from rootUtil import waitRootCmdX
import json
# from os

class FilterConfig:
    def __init__(self,fName=None):
        self.comment = ''
        self.data = []
        self.configFName = 'temp_filter_config.json' if fName is None else fName

    def load(self,fName=None):
        configFName = self.configFName if fName is None else fName
        with open(configFName, 'r') as fp:
            config = json.load(fp)
        self.comment = config.comment
        self.data = config.data

    def save(self,fName=None):
        configFName = self.configFName if fName is None else fName
        config = {'comment':self.comment, 'data':self.data}
        with open(configFName, 'w') as fp:
            fp.write(json.dumps(config, sort_keys=True, indent=4))

def test():
    gStyle.SetOptFit(1011)
    ch1 = TChain('tree1')
    ch1.Add('/data/Samples/TMSPlane/fpgaLin/Mar07C1a_100mV_f1000.root')

    print ch1.GetEntries()

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
        print p1.GetBinContent(1)
        p1.Fit(fun1,"","",rL,rH)
        r = p1.Fit(fun1,"S","",rL,rH)
        print ich, r.Prob()

        fc1.data[ich] = (fun1.GetParameter(0), fun1.GetParameter(1), fun1.GetParameter(2), r.Prob(), rL,rH)
#         p1.Fit('pol0+expo(1)',"","",2500,2800)
#         waitRootCmdX()
    fc1.save()



def test_json(mode=3):

    configFName = 'test_filter_config.json'
    if mode&1:
        print "writing"
        l1 = {'comment':'', 'data':[(0,1,2),(2,3,4)]}
        with open(configFName, 'w') as fp:
            fp.write(json.dumps(l1, sort_keys=True, indent=4))
    if mode & 2:
        print "reading"
        config = None
        with open(configFName, 'r') as fp:
            config = json.load(fp)
        print config

if __name__ == '__main__':
    test()
#     test_json()
