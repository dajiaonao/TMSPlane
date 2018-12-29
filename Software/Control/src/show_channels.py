#!/usr/bin/env python

from ROOT import TTree, TCanvas, TLatex, gDirectory, TH1F
from rootUtil import waitRootCmdX

t1 = TTree()
t1.ReadFile('test1bbb.dat')

t1.Show(0)

lt = TLatex()
c1 = TCanvas()
c1.Divide(6,3)

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

add_fit_menu()
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
