#!/usr/bin/env python

from ROOT import TTree, TCanvas, TLatex, gDirectory, TH1F, TChain, TGraphErrors, gPad
from rootUtil import waitRootCmdX, useLHCbStyle

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
    t150.ReadFile('tt2.dat')

    t150.Draw('A','ch==12')
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
