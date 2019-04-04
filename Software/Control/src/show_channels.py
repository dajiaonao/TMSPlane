#!/usr/bin/env python

from ROOT import TTree, TCanvas, TLatex, gDirectory, TH1F, gPad, gDirectory, TGraphErrors, gStyle
from rootUtil import waitRootCmdX, useLHCbStyle
from array import array

lt = TLatex()
c1 = TCanvas()
c1.Divide(5,4)

dofit_src = '''
void fitENC(TObject *c){
  TH1* h1 = (TH1*)c;
  h1->Fit("gaus");
  TF1* fun = h1->GetFunction("gaus");
  fun->SetLineColor(2);

  double x1 = 700*fun->GetParameter(2)/fun->GetParameter(1);
  cout << x1 << endl;

  TLatex lt;
  lt.DrawLatexNDC(.2,0.9, Form("ENC=%.1f",x1));
  gPad->Update();
}
'''
def add_fit_menu(h=None):
    from ROOT import gROOT, TClassMenuItem
    gROOT.ProcessLine(dofit_src)

    if h is None: h = TH1F()
    cl = h.IsA();
    l = cl.GetMenuList();

    n = TClassMenuItem(TClassMenuItem.kPopupUserFunction,cl,"fit ENC","fitENC",0,"TObject*",2);
    l.AddFirst(n);

def test1(fname='tt2.dat'):
    add_fit_menu()

    t1 = TTree()
    t1.ReadFile(fname)

    t1.Show(0)

    for i in range(18):
        c1.cd(i+1)
        lt.DrawLatexNDC(0.2,0.4,'Ch={0:d}'.format(i))
        t1.Draw('A','ch=={0:d}'.format(i))

    #     t1.Draw('A>>h1','ch=={0:d}'.format(i),'goff')
    #     h1 = gDirectory.Get('h1')
    #     h1.SetName('ch'+str(i))
    # 
    #     c1.cd(i)
    #     h1.Draw()
    #     if i>1: break
    c1.cd()
    waitRootCmdX()

def test1a(fname='data/fpgaLin/dp02a_Mar04C1a_data_0.root'):
    add_fit_menu()

    t1 = TChain('reco')
    t1.Add(fname)

    t1.Show(0)
    V = 200
    gr1 = TGraphErrors()

    for i in range(19):
        c1.cd(i+1)
        lt.DrawLatexNDC(0.2,0.4,'Ch={0:d}'.format(i))
        t1.Draw('Q[{0:d}]>>hx{0:d}'.format(i),'tID!=7')
        hx = gPad.GetPrimitive('hx{0:d}'.format(i))
        hx.Fit('gaus')
        fun1 = hx.GetFunction('gaus')
        encN = 7.40*V*fun1.GetParameter(2)/fun1.GetParameter(1)
        encE = 7.40*V*fun1.GetParError(2)/fun1.GetParameter(1)

        gr1.SetPoint(i,i,encN)
        gr1.SetPointError(i,0,encE)

    c1.cd(20)
    gr1.Draw('AP')

    c1.cd()
    waitRootCmdX()



def test2():
    add_fit_menu()
    t150 = TTree()
    t150.ReadFile('Jan05a_150mV.dat')
    t150.ReadFile('Jan05a_50mV.dat')
#     t150.ReadFile('Jan05a_100mV.dat')
    t150.ReadFile('tt2.dat')
    t150.ReadFile('Jan05a_250mV.dat')

    t150.Draw('A','ch==12')
    waitRootCmdX()

def inspectCh(ds, chs):
    t = TTree()
    t.SetFillColor(0)
    t.SetFillStyle(0)
    for d in ds:
        t.ReadFile(d[1])

    cv1 = TCanvas()
    cv1.Divide(2,4)

    icv = 1
    for ch in chs:
        cv1.cd(icv)
        t.Draw('A','ch=={0:d}'.format(ch))
        hx = gPad.GetPrimitive('htemp')
        hx.GetXaxis().SetTitle('U_{Out} [V]')
        hx.SetName('h{0:d}'.format(ch))
        
        lt.DrawLatexNDC(0.7,0.9,"Ch {0:d}".format(ch))

        icv += 1

    cv1.cd(0)
    waitRootCmdX()

def test3():
    ds = [(50, 'Jan05a_50mV.dat'), (100, 'Jan05a_100mV.dat'), (150, 'Jan05a_150mV.dat'), (250, 'Jan05a_250mV.dat'), (400, 'Jan05a_400mV.dat')]
    chs = [12, 8, 1, 4, 6, 9, 13,15]
    inspectCh(ds,chs)

    return

#     pars = array('d',[0]*3)
#     errs = array('d',[0]*3)
#     print(max(chs))
#     return
    nch = max(chs)+1
    g1s = [None]*nch
    g2s = [None]*nch

    g1M = -1
    g2M = -1
    for d in ds:
        tr = TTree()
        tr.ReadFile(d[1])

        for ch in chs:
            gDirectory.DeleteAll('h1*')
            tr.Draw('A>>h1','ch=={0:d}'.format(ch),'goff')
            h1 = gDirectory.Get('h1')
            h1.Fit('gaus')
            
            fun1 = h1.GetFunction('gaus')
            fun1.SetLineColor(4)
            errs = fun1.GetParErrors()
            pars = fun1.GetParameters()
#             print(d[0],'--'*20)
#             print(pars[0],errs[0])
#             print(pars[1],errs[1])
#             print(pars[2],errs[2])

            if g1s[ch] is None:
                g1s[ch] = TGraphErrors()
                g2s[ch] = TGraphErrors()

            g1 = g1s[ch]
            g2 = g2s[ch]
            n = g1.GetN()
            g1.SetPoint(n, d[0]*7, pars[1])
            g1.SetPointError(n, 0, errs[1])
            g2.SetPoint(n, d[0]*7, pars[2]*d[0]*7/pars[1])
            g2.SetPointError(n, 0, errs[2]*d[0]*7/pars[1])

            if pars[1]+errs[1]>g1M: g1M = pars[1]+errs[1]
            t = (pars[2]+errs[2])*d[0]*7/pars[1]
            if t>g2M: g2M = t
    opt = 'A'
    h1x = None
    for g1 in g1s:
        if g1 is None: continue
        g1.Draw('PL PMC PLC'+opt)
        opt = ' same'
        if h1x is None: h1x = g1.GetHistogram()
    h1x.GetYaxis().SetRangeUser(0, g1M*1.1)
    h1x.GetYaxis().SetTitle("U_{Out} [V]")
    h1x.GetXaxis().SetTitle("N_{Sig} [e^{-}]")
    waitRootCmdX()
    opt = 'A'

    h2x = None
    for g2 in g2s:
        if g2 is None: continue
        g2.Draw('PL PMC PLC'+opt)
        opt = ' same'
        if h2x is None: h2x = g2.GetHistogram()
    h2x.GetYaxis().SetRangeUser(0, g2M*1.1)
    h2x.GetYaxis().SetTitle("ENC [e^{-}]")
    h2x.GetXaxis().SetTitle("N_{Sig} [e^{-}]")
    waitRootCmdX()

def compareX():
#     fl = ['Jan05a_100mV.dat', 'Jan08a_100mV_r30p0us.dat','Jan08a_100mV_r40p0us.dat','Jan08a_100mV_r50p0us.dat']
#     fl = ['Jan05a_100mV.dat', 'Jan08a_100mV_r30p0us.dat','Jan08a_100mV_r40p0us.dat','Jan08a_100mV_r50p0us.dat']
    fl = ['data/fpgaLin/Jan22a_C2_100mV_f{0:d}.dat'.format(x) for x in [100,200,500,1000]]
    fs = [TTree() for f in fl]
    opt = ''

    chx = TTree()
    for f in fl: chx.ReadFile(f)

    chx.Draw('A','ch==12','axis')

    opt = 'same'
    for i in range(len(fl)):
        fs[i].ReadFile(fl[i])
        fs[i].SetFillStyle(0)
        fs[i].SetLineColor(i+1)

        fs[i].Draw('A','ch==12',opt)
    waitRootCmdX()


if __name__ == '__main__':
#     useLHCbStyle()
#     compareX()
#     test1('Jan08a_100mV_r50p0us.dat')
#     test1('Jan05a_100mV.dat')
#     test1('temp1.dat')
    test1a()
#     test2()
