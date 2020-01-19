#include<iostream>
#include <TTree.h>
#include "ROOT/RDataFrame.hxx"
#include "ROOT/RDF/HistoModels.hxx"
#include <TPad.h>
#include <TProfile.h>
#include <vector>

using namespace std;
using namespace ROOT::RDF;

// RVec<int> compute_maxXY(float U, int startU)
// {
//   RVec<int> idx(3);
// 
//   double x,y;
//   hex_l2XY(0.8, id, x, y);
// 
//   xy[0] = x;
//   xy[1] = y;
// 
//   return xy;
// }

void do_real_job(){
  /// create tchain from data
  TTree tr1("tr1","A simple tree");
  tr1.ReadFile("project_51/current.dat","time/C:I/F:T/F:U/F");
  tr1.Show(0);
  cout << tr1.GetEntries() << endl;

  //// create dataframe
  ROOT::RDataFrame df0(tr1);
  cout << df0.Count().GetValue() << endl;

  /// add more info to make selection easier
  int i0(0);
  int i1(0);
  int rdx(0);
  int preU(0);
  int startU(120);
  auto df1 = df0.Define("rU","int(-U+0.1)")\
             .Define("pAI","I*1e12")\
             .Define("idx1",[&i1, &i0](int u){if(i0==u){i1+=1;} else{i1=0; i0=int(u);} return i1;}, {"rU"})\
             .Define("rd1",[&rdx, &startU, &preU](int u){if(startU==u && preU!=u){rdx+=1;} preU=u; return rdx;}, {"rU"})\
             .Filter("pAI<10&&pAI>-60");

  /// make selctions
  auto df2 = df1.Filter("idx1>2000");

  /// create tprofiles
  TProfile1DModel p("profName1", "Round 1;Plane HV [V];I [pA]", 13, -5, 125);
  int nRound = df2.Max("rd1").GetValue();

//   vector< TProfile* > pfV(nullptr, size_t(nRound));
  vector< TProfile* > pfV;
//   vector< RResultPtr< TProfile > > pfV;
  pfV.resize(nRound+1);

  for(int i=0; i<nRound+1; i++){
    cout << i << endl;
    auto myProf1 = df2.Filter([&i](int ird){return ird==i;},{"rd1"}).Profile1D(p, "rU","pAI");
//     pfV[i] = myProf1;
    pfV[i] = (TProfile*) myProf1->Clone(TString::Format("rd_%d", i));
//     pfV[i] = (TProfile*) myProf1->Clone(TString::Format("rd_%d", i));
   }

  pfV[0]->Draw();
  for(auto x: pfV){
    x->DrawCopy("same");
   }

  return;

  auto myProf1 = df2.Filter("rd1==1").Profile1D({"profName1", "Round 1;Plane HV [V];I [pA]", 13, -5, 125}, "rU","pAI");
  auto myProf2 = df2.Filter("rd1==2").Profile1D({"profName2", "Round 2", 13, -5, 125}, "rU","pAI");
  auto myProf3 = df2.Filter("rd1==3").Profile1D({"profName3", "Ref", 13, -5, 125}, "rU","pAI");
  auto myProf4 = df2.Filter("rd1==4").Profile1D({"profName4", "Ref4", 13, -5, 125}, "rU","pAI");
  auto a = df2.Max("rd1");
  cout << a.GetValue() << endl;

  myProf1->SetLineColor(2);
  myProf1->SetMarkerColor(2);
  myProf1->SetMarkerStyle(24);
  myProf2->SetLineColor(4);
  myProf2->SetMarkerColor(4);
  myProf2->SetMarkerStyle(26);
  myProf1->DrawCopy("");
  myProf2->DrawCopy("same");
  auto p3 = myProf3->DrawCopy("same");

  myProf4->SetMarkerColor(3);
  myProf4->DrawCopy("same");

  auto myProf1_d = new TH1F("myProf1_d","Round 1, I_{#alpha}",13, -5, 125);
  auto myProf2_d = new TH1F("myProf2_d","Round 2, I_{#alpha}",13, -5, 125);

  for(int i=0; i<myProf3->GetNbinsX()+1; i++){
    myProf1_d->SetBinContent(i, myProf1->GetBinContent(i)-myProf3->GetBinContent(i));
    myProf1_d->SetBinError(i, sqrt(pow(myProf1->GetBinError(i),2)+pow(myProf3->GetBinError(i),2)));
    myProf2_d->SetBinContent(i, myProf2->GetBinContent(i)-myProf3->GetBinContent(i));
    myProf2_d->SetBinError(i, sqrt(pow(myProf2->GetBinError(i),2)+pow(myProf3->GetBinError(i),2)));
    cout << i << " / " << myProf2->GetBinContent(i) << "-" << myProf3->GetBinContent(i) << "=" << myProf2_d->GetBinContent(i) << endl;
   }

  myProf1_d->SetLineColor(2);
  myProf1_d->SetLineStyle(2);
  myProf1_d->SetMarkerColor(2);
  myProf1_d->SetMarkerStyle(25);
  myProf2_d->SetLineColor(4);
  myProf2_d->SetLineStyle(5);
  myProf2_d->SetMarkerColor(4);
  myProf2_d->SetMarkerStyle(27);
  myProf1_d->Draw("same");
  myProf2_d->Draw("same");

  gPad->SetGridy();
  gPad->BuildLegend();
  gPad->Update();
  return;
}


void do_real_job1(){
  /// create tchain from data
  TTree tr1("tr1","A simple tree");
  tr1.ReadFile("project_51/current.dat","time/C:I/F:T/F:U/F");
  tr1.Show(0);
  cout << tr1.GetEntries() << endl;

  //// create dataframe
  ROOT::RDataFrame df0(tr1);
  cout << df0.Count().GetValue() << endl;

  /// add more info to make selection easier
  int i0(0);
  int i1(0);
  int rdx(0);
  int preU(0);
  int startU(120);
  auto df1 = df0.Define("rU","int(-U+0.1)")\
             .Define("pAI","I*1e12")\
             .Define("idx1",[&i1, &i0](int u){if(i0==u){i1+=1;} else{i1=0; i0=int(u);} return i1;}, {"rU"})\
             .Define("rd1",[&rdx, &startU, &preU](int u){if(startU==u && preU!=u){rdx+=1;} preU=u; return rdx;}, {"rU"})\
             .Filter("pAI<10&&pAI>-60");

  auto df2 = df1.Filter("idx1>1000");
//   auto a = df2.Max("rd1");
//   cout << a.GetValue() << endl;
//   cout << df2.Count().GetValue() << endl;

//   auto h1 = df2.Histo1D("rU");
//   auto h1 = df2.Histo1D("rd1");
//   h1->DrawCopy("PLC PMC");
//   return;

  /// create tprofiles
  TProfile1DModel p("profName1", "Round 1;Plane HV [V];I [pA]", 13, -5, 125);
  auto myProf1 = df2.Filter("rd1==1").Profile1D(p, "rU","pAI");
  myProf1->SetName("profName1");
  myProf1->SetTitle("profName1");
//   auto myProf1 = df2.Filter("rd1==1").Profile1D({"profName1", "Round 1;Plane HV [V];I [pA]", 13, -5, 125}, "rU","pAI");
  cout << myProf1->GetEntries() << endl;
  auto myProf2 = df2.Filter("rd1==2").Profile1D(p, "rU","pAI");
  myProf2->SetName("profName2");
  myProf2->SetTitle("profName2");
//   auto myProf3 = df2.Filter("rd1==3").Profile1D(p, "rU","pAI");
//   auto myProf4 = df2.Filter("rd1==4").Profile1D(p, "rU","pAI");
//   auto myProf5 = df2.Filter("rd1==5").Profile1D(p, "rU","pAI");
//   auto myProf6 = df2.Filter("rd1==6").Profile1D(p, "rU","pAI");
//   auto myProf7 = df2.Filter("rd1==7").Profile1D(p, "rU","pAI");
//   auto myProf8 = df2.Filter("rd1==8").Profile1D(p, "rU","pAI");

  myProf1->DrawCopy("PLC PMC");
  myProf2->DrawCopy("PLC PMC same");

  gPad->SetGridy();
  gPad->BuildLegend();
  gPad->Update();
  return;
}



void do_real_job0(){
  cout << "Fun starts here..." << endl;

  /// create tchain from data
  TTree tr1("tr1","A simple tree");
//   tr1.ReadFile("project_48/current.dat","time/C:I/F:T/F:U/F");
  tr1.ReadFile("project_51/current.dat","time/C:I/F:T/F:U/F");
//   tr1.ReadFile("project_49/current.dat","time/C:I/F:T/F:U/F");
  tr1.Show(0);
  cout << tr1.GetEntries() << endl;

  //// create dataframe
  ROOT::RDataFrame df0(tr1);
  cout << df0.Count().GetValue() << endl;

  /// add more info to make selection easier
  int i0(0);
  int i1(0);
  int rdx(0);
  int preU(0);
  int startU(120);
  auto df1 = df0.Define("rU","int(-U+0.1)")\
             .Define("pAI","I*1e12")\
             .Define("idx1",[&i1, &i0](int u){if(i0==u){i1+=1;} else{i1=0; i0=int(u);} return i1;}, {"rU"})\
             .Define("rd1",[&rdx, &startU, &preU](int u){if(startU==u && preU!=u){rdx+=1;} preU=u; return rdx;}, {"rU"})\
             .Filter("pAI<10&&pAI>-60");

  auto df2 = df1.Filter("idx1>2000");
//   auto df2 = df1;

  /// make selctions
//   auto h1 = df2.Histo1D("idx1");
//   auto h1 = df1.Histo1D("U");
//   auto h1 = df1.Histo1D("T");
//   h1->DrawCopy();

//   auto h1 = df2.Filter("rd1==0").Histo1D("rU");
//   auto h1 = df2.Filter("rd1==0").Histo2D({"h2","h2",100,600000,800000,100,0,150},"T","rU");
//   auto h1 = df2.Histo2D({"h2","h2",100,600000,800000,100,0,150},"T","rU");
//   auto h1 = df2.Histo2D({"h2","h2;T;U",100,200000,900000,100,0,-150},"T","U");
//   auto h1 = df2.Histo2D({"h2","h2",100,600000,800000,100,0,150},"T","rU");
//   auto h1 = df2.Histo2D({"h2","h2",100,690000,750000,100,0,150},"T","rd1");
//   auto h1 = df2.Histo2D({"h2","h2",100,690000,950000,5,0,5},"T","rd1");
//   auto h1 = df1.Histo1D("rU");
//   h1->DrawCopy("colz");

//   return;

  /// create tprofiles
  auto myProf1 = df2.Filter("rd1==1").Profile1D({"profName1", "Round 1;Plane HV [V];I [pA]", 13, -5, 125}, "rU","pAI");
  auto myProf2 = df2.Filter("rd1==2").Profile1D({"profName2", "Round 2", 13, -5, 125}, "rU","pAI");
//   auto myProf3 = df2.Filter("T>675000").Profile1D({"profName3", "Ref", 13, -5, 125}, "rU","pAI");
  auto myProf3 = df2.Filter("rd1==3").Profile1D({"profName3", "Ref", 13, -5, 125}, "rU","pAI");
  auto myProf4 = df2.Filter("rd1==4").Profile1D({"profName4", "Ref4", 13, -5, 125}, "rU","pAI");
  auto a = df2.Max("rd1");
  cout << a.GetValue() << endl;

  myProf1->SetLineColor(2);
  myProf1->SetMarkerColor(2);
  myProf1->SetMarkerStyle(24);
  myProf2->SetLineColor(4);
  myProf2->SetMarkerColor(4);
  myProf2->SetMarkerStyle(26);
  myProf1->DrawCopy("");
  myProf2->DrawCopy("same");
  auto p3 = myProf3->DrawCopy("same");

  myProf4->SetMarkerColor(3);
  myProf4->DrawCopy("same");

  auto myProf1_d = new TH1F("myProf1_d","Round 1, I_{#alpha}",13, -5, 125);
  auto myProf2_d = new TH1F("myProf2_d","Round 2, I_{#alpha}",13, -5, 125);

  for(int i=0; i<myProf3->GetNbinsX()+1; i++){
    myProf1_d->SetBinContent(i, myProf1->GetBinContent(i)-myProf3->GetBinContent(i));
    myProf1_d->SetBinError(i, sqrt(pow(myProf1->GetBinError(i),2)+pow(myProf3->GetBinError(i),2)));
    myProf2_d->SetBinContent(i, myProf2->GetBinContent(i)-myProf3->GetBinContent(i));
    myProf2_d->SetBinError(i, sqrt(pow(myProf2->GetBinError(i),2)+pow(myProf3->GetBinError(i),2)));
    cout << i << " / " << myProf2->GetBinContent(i) << "-" << myProf3->GetBinContent(i) << "=" << myProf2_d->GetBinContent(i) << endl;
   }

  myProf1_d->SetLineColor(2);
  myProf1_d->SetLineStyle(2);
  myProf1_d->SetMarkerColor(2);
  myProf1_d->SetMarkerStyle(25);
  myProf2_d->SetLineColor(4);
  myProf2_d->SetLineStyle(5);
  myProf2_d->SetMarkerColor(4);
  myProf2_d->SetMarkerStyle(27);
  myProf1_d->Draw("same");
  myProf2_d->Draw("same");

  gPad->SetGridy();
  gPad->BuildLegend();
  gPad->Update();
  return;
}



int check_data(){
  cout << "testing" << endl;

  do_real_job1();

  return 0;
}

int main(){
  return check_data();
}
