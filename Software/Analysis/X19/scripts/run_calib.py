#!/usr/bin/env python36
'''The script is used to calculate the calibration parameters'''

from ROOT import TChain, gDirectory, TFile, TNtuple, TGraphErrors
from array import array
from rootUtil3 import waitRootCmdX

def make_calibration_file():
    dir1 = '/home/dzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/'

    ch1 = TChain('reco')
    ch1.Add(dir1+'Mar08D1a/tpx01a_Mar08D1a_data_*.root')

    vlist = []
#     vlist.append(('v20mV', 0.02, 'w2[19]>200&&(im[0]-im[19])>900&&(im[0]-im[19])<950&&run>100&&run<120'))

    vlist.append(('v40mV',  0.04, 'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>-1&&run<48'))
    vlist.append(('v200mV', 0.2,  'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>48&&run<70'))
    vlist.append(('v320mV', 0.32, 'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>70&&run<83'))
    vlist.append(('v80mV',  0.08, 'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>83&&run<92'))
    vlist.append(('v400mV', 0.4,  'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>92&&run<109'))
    vlist.append(('v20mV',  0.02, 'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>109&&run<117'))
    vlist.append(('v120mV', 0.12, 'im[19]<15500&&w2[19]>200&&(im[{0:d}]-im[19])>900&&(im[{0:d}]-im[19])<950&&run>117&&run<133'))

#     est = [(0.17212905199020656, 0.22174582859078348), (0.16079272333604147, 0.23471298272887056), (-0.001302937592833715, -4.621511331574358), (0.13632007342712146, 0.3159682807188622), (0.15803662877668728, 0.13902808192224678), (0.08620209544794977, 0.14013506152043326), (0.11456876608094842, 0.23925329600875966), (0.08134243416477327, 0.19948247612443978), (0.005442892449509963, 0.8875965007915377), (0.2211384400475029, 0.11827482151964498), (0.13455648428225397, 0.3508197462861181), (0.05548485463913555, 0.20451936716277572), (0.18416619542399212, 0.23546844798848812), (0.09426043598754809, 0.19711582957379015), (0.047546367382578954, 0.5249384526518839), (0.1523372518269591, 0.18800468879412868), (0.19024732100624941, 0.27459103900595555), (0.1121625239134882, 0.1468283044797153), (0.194140644353606, 0.13697072917725264)]
#     est = [(0.17151804649165348, 0.000751543069447149), (0.16044978139595478, 0.0007501127424230879), (0.0003274741243165923, 0.00022091504494392274), (0.13589952654970727, 0.0008500113368533045), (0.15766832588975024, 0.0004289215799395516), (0.08615600869065161, 0.00023157256035933756), (0.11451137372995769, 0.0005462440373753035), (0.08104268738822586, 0.0003211239956348413), (0.0058205564348078566, 9.834968036528331e-05), (0.22127102805717322, 0.000510295561808027), (0.13341967387517953, 0.0009357373087099658), (0.055526276960555065, 0.00022441209409340774), (0.1842900906282299, 0.000865063887373536), (0.09412670413189951, 0.00036363706832611185), (0.048915929203843266, 0.0006650772682925401), (0.15238978572550832, 0.0005636821067693204), (0.1902078512672581, 0.0010676024453752971), (0.11213521841877704, 0.0003257379328649152), (0.19375155818330708, 0.0005172058639266957)]
    est = [(0.21022370123491813, 0.0008741161563643704), (0.19629371426485331, 0.0009121788768669809), (-2.9240373043105834e-05, 0.0001299896098810482), (0.1636330548911822, 0.0009869011104165029), (0.1557281174864831, 0.0004713441812800613), (0.08165197997497343, 0.0002599914611321653), (0.12921528380497121, 0.0006022973770565171), (0.08212465152837047, 0.0008805863461647292), (-0.0009507593531406199, 0.001174828585932144), (0.2245892308053989, 0.0005665017186336387), (0.15689959575915818, 0.0012273326442494626), (0.05964015545309604, 0.00027919815982878804), (0.17694975233278912, 0.0008966022944452189), (0.10315954550972423, 0.001328182705596258), (0.07822323979066328, 0.0017089007391025324), (0.17768504663053067, 0.0006502947947728483), (0.24610372781569553, 0.0012768341750616628), (0.1139013588428892, 0.0003449015240679468), (0.21924261276723744, 0.0005712269654350105)]


    nCh = 19
    d1 = [0]*nCh


    fout = TFile('calib_out.root','recreate')
    tup1 = TNtuple('calib','calibration info','chan:V:nEvt:mean:meanErr:sigma:sigmaErr:fProb:fStatus')

    for v in vlist:
        for ich in range(nCh):
#             gDirectory.DeleteAll('h1*')

            e = est[ich]
            mean = abs(e[0]*v[1])
            sigma3 = abs(5.* e[1])
            print(mean, sigma3)

            hName = 'h_'+str(ich)+'_'+v[0]
#             n = ch1.Draw('Q[{0:d}]>>h1(100,{1:.2g},{2:.2g})'.format(ich,mean-sigma3,mean+sigma3),v[2].format(ich),'goff')
            n = ch1.Draw('Q[{0:d}]>>{1}'.format(ich,hName,mean-sigma3,mean+sigma3),v[2].format(ich)+'&&Q[{0:d}]>{1:.2g}&&Q[{0:d}]<{2:.2g}'.format(ich,0.2*mean,5*mean),'goff')
            print(n)
            if n<1: 
                tup1.Fill(ich,v[1],n,-1, -1, -1, -1, -1,-1)
                continue
            h1 = gDirectory.Get(hName)
            r = h1.Fit('gaus','S')
            fun1 = h1.GetFunction('gaus')
            nC = 7400.*v[1]
            enc = nC*fun1.GetParameter(2)/fun1.GetParameter(1)

            tup1.Fill(ich,v[1],n,fun1.GetParameter(1), fun1.GetParError(1), fun1.GetParameter(2), fun1.GetParError(2), r.Prob(), r.Status())

            print(enc, r.Prob())

            fout.cd()
            h1.Write()

#             h1.Draw()
#             waitRootCmdX()

            d1[ich] = (fun1.GetParameter(1)/v[1],fun1.GetParameter(2))
    print(d1)

    tup1.Write()

    for ich in range(nCh):
        gr = get_gr(tup1,ich)
        gr.Write('calib_gr_'+str(ich))

    fout.Close()

def get_gr(ch,chan):
    n = ch.Draw('V:mean:meanErr',f'abs(chan)=={chan}','goff')
    v1 = ch.GetV1()
    v2 = ch.GetV2()
    v3 = ch.GetV3()

    nElectronPerV = 7410.

    dx = sorted([(v1[i]*nElectronPerV,v2[i],v3[i]) for i in range(n)]+[(0,0,0)], key=lambda x:x[0])

    n1 = len(dx)
    px = lambda t: array('f',[dx[i][t] for i in range(n1)])
    gr0 = TGraphErrors(n1, px(1), px(0), px(2), array('f',[0]*n1))

    return gr0

def test():
    make_calibration_file()

if __name__ == '__main__':
    test()

