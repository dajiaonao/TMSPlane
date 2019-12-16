#include "ROOT/RDataFrame.hxx"
#include "TChain.h"
#include "TGraphErrors.h"
#include "ROOT/RVec.hxx"
#include "ROOT/RDF/RInterface.hxx"
#include "ROOT/RDF/HistoModels.hxx"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2Poly.h"
#include "TMath.h"
#include "TLatex.h"
#include "TLegend.h"
#include "Math/Vector4Dfwd.h"
#include "TStyle.h"
#include "HoneycombS.C"
#include "plotting/Pal3.C"

using namespace ROOT::VecOps;
using RNode = ROOT::RDF::RNode;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;

const auto z_mass = 91.2;

// Select interesting events with four muons
RNode selection_4mu(RNode df)
{
   auto df_ge4m = df.Filter("nMuon>=4", "At least four muons");
   auto df_iso = df_ge4m.Filter("All(abs(Muon_pfRelIso04_all)<0.40)", "Require good isolation");
   auto df_kin = df_iso.Filter("All(Muon_pt>5) && All(abs(Muon_eta)<2.4)", "Good muon kinematics");
   auto df_ip3d = df_kin.Define("Muon_ip3d", "sqrt(Muon_dxy*Muon_dxy + Muon_dz*Muon_dz)");
   auto df_sip3d = df_ip3d.Define("Muon_sip3d", "Muon_ip3d/sqrt(Muon_dxyErr*Muon_dxyErr + Muon_dzErr*Muon_dzErr)");
   auto df_pv = df_sip3d.Filter("All(Muon_sip3d<4) && All(abs(Muon_dxy)<0.5) && All(abs(Muon_dz)<1.0)",
                                "Track close to primary vertex with small uncertainty");
   auto df_2p2n = df_pv.Filter("nMuon==4 && Sum(Muon_charge==1)==2 && Sum(Muon_charge==-1)==2",
                               "Two positive and two negative muons");
   return df_2p2n;
}

TFile* fin1 = new TFile("/data/repos/TMSPlane/Software/Analysis/X19/scripts/C7a_calib_out.root","read");
auto* calib_gr_0 = (TGraphErrors*)fin1->Get("calib_gr_0");
auto* calib_gr_1 = (TGraphErrors*)fin1->Get("calib_gr_1");
auto* calib_gr_2 = (TGraphErrors*)fin1->Get("calib_gr_2");
auto* calib_gr_3 = (TGraphErrors*)fin1->Get("calib_gr_3");
auto* calib_gr_4 = (TGraphErrors*)fin1->Get("calib_gr_4");
auto* calib_gr_5 = (TGraphErrors*)fin1->Get("calib_gr_5");
auto* calib_gr_6 = (TGraphErrors*)fin1->Get("calib_gr_6");
auto* calib_gr_7 = (TGraphErrors*)fin1->Get("calib_gr_7");
auto* calib_gr_8 = (TGraphErrors*)fin1->Get("calib_gr_8");
auto* calib_gr_9 = (TGraphErrors*)fin1->Get("calib_gr_9");
auto* calib_gr_10 = (TGraphErrors*)fin1->Get("calib_gr_10");
auto* calib_gr_11 = (TGraphErrors*)fin1->Get("calib_gr_11");
auto* calib_gr_12 = (TGraphErrors*)fin1->Get("calib_gr_12");
auto* calib_gr_13 = (TGraphErrors*)fin1->Get("calib_gr_13");
auto* calib_gr_14 = (TGraphErrors*)fin1->Get("calib_gr_14");
auto* calib_gr_15 = (TGraphErrors*)fin1->Get("calib_gr_15");
auto* calib_gr_16 = (TGraphErrors*)fin1->Get("calib_gr_16");
auto* calib_gr_17 = (TGraphErrors*)fin1->Get("calib_gr_17");
auto* calib_gr_18 = (TGraphErrors*)fin1->Get("calib_gr_18");

const size_t nCh = 19;
std::vector< TGraphErrors* > calib_grs{calib_gr_0,calib_gr_1,calib_gr_2,calib_gr_3,calib_gr_4,calib_gr_5,calib_gr_6,calib_gr_7,calib_gr_8,calib_gr_9,calib_gr_10,calib_gr_11,calib_gr_12,calib_gr_13,calib_gr_14,calib_gr_15,calib_gr_16,calib_gr_17,calib_gr_18};


RVec<float> compute_corrected(rvec_f Q)
{
  RVec<float> cQ(nCh);
  for(size_t ich=0; ich<nCh; ich++){
    cQ[ich] = calib_grs[ich]->Eval(Q[ich]);
   }

  return cQ;
}

RVec<float> compute_maxXY(int id)
{
  RVec<float> xy(2);

  double x,y;
  hex_l2XY(0.8, id, x, y);

  xy[0] = x;
  xy[1] = y;

  return xy;
}

RVec<int> getQInexes(rvec_f cQ)
{
  RVec<int> Qrank(nCh);
  auto it = Qrank.begin();
  TMath::SortItr(cQ.begin(), cQ.end(), it, true);

  return Qrank;
}

RNode make_corection(RNode df){

  auto df1 = df.Define("cQ", compute_corrected, {"Q"});

  return df1;
}

RNode sortByQ(RNode df){
  auto df1a = df.Define("Qrank", getQInexes, {"cQ"});
  auto df1 = df1a.Define("Qd0", "cQ[Qrank[0]]-cQ[Qrank[1]]");

  return df1;
}


void df_sel()
{
 cout << "test1" << endl; 
//  gStyle->SetPalette(55);

 /// create the familiar TChain
 TChain ch("reco");
 ch.Add("temp3_out/trigCh3c_Dec05b_data_*.root");
 ch.Show(0);
 cout << ch.GetEntries() << endl;

 /// build dataframe from TChain
 ROOT::RDataFrame df0(ch);
 cout << df0.Count().GetValue() << endl;

 /// basic selections first
 auto df_preSel = df0.Filter("run<140").Filter("im[3]<2800||im[3]>3800").Filter("im[3]>400");

 /// apply the calibration
 auto df_corrected = make_corection(df_preSel);

 /// do the simple thing: find max
 auto df_Qsorted = sortByQ(df_corrected);

 /// check the max
 auto df_c = df_Qsorted.Define("Qrank0","Qrank[0]").Define("XY",compute_maxXY, {"Qrank0"}).Define("X","XY[0]").Define("Y","XY[1]");

 /// plot
//  gStyle->SetPalette();
 Pal3();
 auto hc = new TH2Poly();
 hc->SetTitle("TMS19Plane");
 hc->GetXaxis()->SetTitle("x [cm]");
 hc->GetYaxis()->SetTitle("y [cm]");
 hc->GetZaxis()->SetTitle("Events");
 HoneycombS(hc,0.8,19);
 auto hc2 = (TH2Poly*) hc->Clone("hc2");
 for(size_t i=0; i<nCh; i++){
   double X,Y;
   hex_l2XY(0.8, i, X, Y);
   hc2->Fill(X,Y,i+0.1);
  }

 df_c.Foreach([hc](float x, float y){ hc->Fill(x,y);}, {"X", "Y"});
//  auto th2d = df_c.Fill<float, float>(hc, {"XY[0]", "XY[1]"});
 hc->Draw("colz");
 gStyle->SetPaintTextFormat(".0f");
 hc2->Draw("text same");
 return;

 auto df1 = df_Qsorted.Filter("Qrank[0]==3").Define("cQ_3T7","cQ[3]+cQ[0]+cQ[4]+cQ[2]+cQ[11]+cQ[12]+cQ[10]");
 auto df2 = df_Qsorted.Filter("Qrank[0]==0").Define("cQ_0T7","cQ[0]+cQ[1]+cQ[2]+cQ[3]+cQ[4]+cQ[5]+cQ[6]").Define("E","cQ[0]+cQ[1]+cQ[2]+cQ[3]+cQ[4]+cQ[5]+cQ[6]+cQ[7]+cQ[8]+cQ[9]+cQ[10]+cQ[11]+cQ[12]+cQ[13]+cQ[14]+cQ[15]+cQ[16]+cQ[17]+cQ[18]").Define("E1","cQ[0]+cQ[1]+cQ[2]+cQ[3]+cQ[4]+cQ[5]+cQ[6]+cQ[7]+cQ[8]+cQ[9]+cQ[10]+cQ[11]+cQ[12]+cQ[13]+cQ[14]+cQ[15]+cQ[18]");

//  auto h1 = df1.Define("cQ0","cQ[0]").Histo1D("cQ0");
//  auto h1 = df1.Histo1D("Qd0");
//  auto h1 = df1.Define("Qd17", "cQ[Qrank[17]]-cQ[Qrank[18]]").Histo1D("Qd17");
//  auto h1 = df1.Define("Qr0", "Qrank[0]").Histo1D({"h1","h1;Chan;Events",19,0,19},"Qr0");
 ROOT::RDF::TH1DModel h0("h0","h0;Q [e^{-}];Events",180,-1000,17000); 
 auto h1 = df1.Histo1D(h0, "cQ_3T7");
 auto h2 = df2.Histo1D(h0, "cQ_0T7");
 auto h2b = df2.Histo1D(h0,"E");
 auto h2c = df2.Histo1D(h0,"E1");

 h1->SetTitle("3T7"); h1->SetName("h3T7");
 h2->SetTitle("0T7"); h2->SetName("h0T7");
 h2b->SetTitle("All"); h2b->SetName("hAll");
 h2c->SetTitle("All-16,17"); h2c->SetName("hAll_16_17");

 h2->SetLineColor(2);
 h1->SetLineColor(4);
 h2b->SetLineColor(1);
 h2c->SetLineColor(6);

 h2->DrawCopy("");
 h1->DrawCopy("same");
 h2b->DrawCopy("same");
 h2c->DrawCopy("same");

//  h2->DrawCopy("norm PLC");
//  h1->DrawCopy("norm PLC same");
//  h2b->DrawCopy("norm PLC same");
//  h2c->DrawCopy("norm PLC same");

 gPad->BuildLegend();
 gPad->Update();
}


int main()
{
   df_sel();
}
