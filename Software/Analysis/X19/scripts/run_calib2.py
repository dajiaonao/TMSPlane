#!/usr/bin/env python36
'''The script is used to calculate the calibration parameters'''
from rootUtil3 import waitRootCmdX
from rootHelper import getRDF
# import ROOT
from ROOT import RDataFrame, TChain, RDF, TF1


class Calibrator:
    def __init__(self):
        pass
    def run_calibration(self):
        dir1 = '/home/dzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/Apr22T1a_tpx02a/'

        ch1 = TChain('reco')
        ch1.Add(dir1+'tpx02a_Apr22T1a_data_5*.root')
        ch1.Add(dir1+'tpx02a_Apr22T1a_data_60*.root')
        ch1.Add(dir1+'tpx02a_Apr22T1a_data_61*.root')
        ch1.Add(dir1+'tpx02a_Apr22T1a_data_62*.root')
        nCh = 20

        d1 = RDataFrame(ch1)
        print(d1.Count().GetValue())

        runnList = []
        runnList.append((0.02, [(524,530),(573,579)]))
        runnList.append((0.04, [(530,535),(579,584)]))
        runnList.append((0.08, [(535,567),(584,590)]))
        runnList.append((0.12, [(500,502),(590,596)]))
        runnList.append((0.2,  [(502,508),(596,602)]))
        runnList.append((0.32, [(508,513),(602,607)]))
        runnList.append((0.4,  [(513,519),(607,613)]))
        runnList.append((0.5,  [(519,524),(613,618)]))
        runnList.append((0.8,  [(567,573),(618,624)]))

        d2 = d1.Filter('im[19]<15500')
        for i in range(nCh):
            d2 = d2.Define('Q_{0:d}'.format(i),'Q[{0:d}]'.format(i)).Define('im_{0:d}'.format(i),'im[{0:d}]'.format(i)).Define('w2_{0:d}'.format(i),'w2[{0:d}]'.format(i)).Define('im_{0:d}d'.format(i),'im[{0:d}]-im[19]'.format(i))

#         d2 = d2.Filter('(run>567&&run<573)||(run>618&&run<624)')
        d2 = d2.Filter('(w2_19>223&&w2_19<250)')
        d2 = d2.Filter('(Q_19>0.09&&Q_19<0.123)')


#         h1 = d2.Histo1D(RDF.TH1DModel('h2','h2',100,200,300),'w2_19')
#         h1 = d2.Histo1D(RDF.TH1DModel('h1','h1',100,0.05,0.15),'Q_19')
#         h1 = d2.Histo1D('Q_0')
#         h1 = d2.Histo1D(RDF.TH1DModel('h1','h1',100,0,0.05),'Q_0')
#         h1 = d2.Histo1D(RDF.TH1DModel('h1','h1',100,800,1100),'im_9d')
        h1 = d2.Filter('Q_9<0.01').Histo1D(RDF.TH1DModel('h1','h1',100,800,1100),'im_9d')
       
#         h2 = d2.Histo2D( RDF.TH2DModel('h2','h2',100,-0.01,0.05,100,200,300), 'Q_0','w2_19')
#         h2 = d2.Histo2D( RDF.TH2DModel('h2','h2',100,-200,1400,100,200,300), 'im_0d','w2_19')
#         h2 = d2.Histo2D( RDF.TH2DModel('h2','h2',100,0,0.02,100,-200,1400), 'Q_9','im_9d')

        h1.Draw()
        fun1 = TF1("PrevFitTMP","gaus(0)+pol1(3)",800,1100);
        fun1.SetParameter(0, 1000)
        fun1.SetParameter(1,h1.GetMean())
        fun1.SetParameter(2,h1.GetStdDev())
        h1.GetValue().Fit(fun1)
        waitRootCmdX()

        m = fun1.GetParameter(1)
        s = fun1.GetParameter(2)

        ich = 9
        d2a = d2.Filter('im_{0:d}d>{1:.1f}&&im_{0:d}d<{2:.1f}'.format(ich, m-2*s, m+2*s))
        h2 = d2a.Histo2D( RDF.TH2DModel('h2','h2',100,0,0.02,100,-200,1400), f'Q_{ich}',f'im_{ich}d')

        h1 = d2a.Histo1D(RDF.TH1DModel('h1','h1',100,0,0.05),f'Q_{ich}')
        h1.Draw()
        waitRootCmdX()

        h2.Draw('colz')
        waitRootCmdX()

        ### -----------------------------------------------------------
        ## get one done: channle 9, 800 mV
        print('||'.join(["(run>{0:d}&&run<{1:d})".format(t[0],t[1]) for t in runnList[-1][1]]))
        ds_800 = d2.Filter('||'.join(["(run>{0:d}&&run<{1:d})".format(t[0],t[1]) for t in runnList[-1][1]]))

        ich = 9
        ### create check the cuts
        h1 = ds_800.Histo1D(RDF.TH1DModel('h1','h1',100,800,1100),f'im_{ich}d')

        h1.Draw()
#         fun1 = TF1("PrevFitTMP","gaus(0)+pol1(3)",800,1100);
        fun1.SetParameter(0, 1000)
        fun1.SetParameter(1,h1.GetMean())
        fun1.SetParameter(2,h1.GetStdDev())
        h1.GetValue().Fit(fun1)
        waitRootCmdX()

        m = fun1.GetParameter(1)
        s = fun1.GetParameter(2)

        h1 = d2.Filter('im_{0:d}d>{1:.1f}&&im_{0:d}d<{2:.1f}'.format(ich, m-2*s, m+2*s)).Histo1D(f'Q_{ich}')
        h1.Draw()
        h1.Fit('gaus')
        waitRootCmdX()


        ### get enc



def test1():
    ct1 = Calibrator()
    ct1.run_calibration()


if __name__ == '__main__':
    test1()
