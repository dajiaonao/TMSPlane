/// \file
/// \ingroup tutorial_fit
/// \notebook -nodraw
/// Example on how to use the new Minimizer class in ROOT
///  Show usage with all the possible minimizers.
/// Minimize the Rosenbrock function (a 2D -function)
/// This example is described also in
/// http://root.cern.ch/drupal/content/numerical-minimization#multidim_minim
/// input : minimizer name + algorithm name
/// randomSeed: = <0 : fixed value: 0 random with seed 0; >0 random with given seed
///
/// \macro_code
///
/// \author Lorenzo Moneta

#include "Math/Minimizer.h"
#include "Math/Factory.h"
#include "Math/Functor.h"
#include "TRandom2.h"
#include "TError.h"
#include "TF1.h"
#include "TLegend.h"
#include "TGraphErrors.h"
#include <iostream>

TGraphErrors* gr0(nullptr);
TGraphErrors* gr1(nullptr);
TGraphErrors* gr2(nullptr);

TGraphErrors* corrected_gr(const TGraphErrors* gr, double yC){
  int N = gr->GetN();
  auto Xs = gr->GetX();
  auto Ys = gr->GetY();
  auto EYs = gr->GetEY();
  auto EXs = gr->GetEX();

  TGraphErrors* grO = new TGraphErrors();
  for(int i=1;i<N;i++){
    grO->SetPoint(i, Xs[i], Ys[i]+yC);
    grO->SetPointError(i, EXs[i], EYs[i]);
   }
 
  return grO;
}


double polx3(double x, double a, double b, double c){
  return a*x + b*x*x + c*x*x*x;
}

double getChi2(const TGraphErrors* gr, const double *xx, const int tt=0)
{
  double chi2(0);
  int N = gr->GetN();
  auto Xs = gr->GetX();
  auto Ys = gr->GetY();
  auto EYs = gr->GetEY();
  auto EXs = gr->GetEX();

  for(int i=1;i<N;i++){
    double calc_y = polx3(Xs[i], xx[3],xx[4],xx[5]);
    double calc_yE = polx3(Xs[i]+EXs[i], xx[3],xx[4],xx[5])-calc_y;
    double d2 = pow(Ys[i]+xx[tt]-calc_y,2)/(EYs[i]*EYs[i]+calc_yE*calc_yE);
//     cout << tt << " << " << i << " d2=" << d2 << endl;
    chi2 += d2;
//     cout << i << " d=" << d << endl;
//     chi2 += d*d;
   }

  return chi2;
}

double RosenBrock(const double *xx )
{
  
  double chi2(0);
  chi2 += getChi2(gr0, xx, 0);
  chi2 += getChi2(gr1, xx, 1);
  chi2 += getChi2(gr2, xx, 2);

  return chi2;
}

double RosenBrock0(const double *xx )
{
  double chi2 = 0;

  /// first dataset
  int N = gr0->GetN();
  auto Xs = gr0->GetX();
  auto Ys = gr0->GetY();
  auto EYs = gr0->GetEY();
  auto EXs = gr0->GetEX();
  for(int i=1;i<N;i++){
    double calc_y = polx3(Xs[i], xx[3],xx[4],xx[5]);
    double calc_yE = polx3(Xs[i]+EXs[i], xx[3],xx[4],xx[5])-calc_y;
    double d2 = pow(Ys[i]-xx[0]-calc_y,2)/(EYs[i]*EYs[i]+calc_yE*calc_yE);
//     cout << i << " d2=" << d2 << endl;
    chi2 += d2;
//     cout << i << " d=" << d << endl;
//     chi2 += d*d;
   }


  /// 2nd dataset
  N = gr1->GetN();
  Xs = gr1->GetX();
  Ys = gr1->GetY();
  EYs = gr1->GetEY();
  for(int i=0;i<N;i++){
    double calc_y = xx[3]*Xs[i]+xx[4]*Xs[i]*Xs[i]+xx[5]*Xs[i]*Xs[i]*Xs[i];
    double d = (Ys[i]-xx[1]-calc_y)/EYs[i];

    chi2 += d*d;
   }

  /// 3rd dataset
  N = gr2->GetN();
  Xs = gr2->GetX();
  Ys = gr2->GetY();
  EYs = gr2->GetEY();
  for(int i=0;i<N;i++){
    double calc_y = xx[3]*Xs[i]+xx[4]*Xs[i]*Xs[i]+xx[5]*Xs[i]*Xs[i]*Xs[i];
    double d = (Ys[i]-xx[2]-calc_y)/EYs[i];

    chi2 += d*d;
   }

  cout << "chi2=" << chi2 << endl;
  return chi2;
}

int NumericalMinimization(const char * minName = "Minuit",
                          const char *algoName = "" ,
                          int randomSeed = -1)
{
   // create minimizer giving a name and a name (optionally) for the specific
   // algorithm
   // possible choices are:
   //     minName                  algoName
   // Minuit /Minuit2             Migrad, Simplex,Combined,Scan  (default is Migrad)
   //  Minuit2                     Fumili2
   //  Fumili
   //  GSLMultiMin                ConjugateFR, ConjugatePR, BFGS,
   //                              BFGS2, SteepestDescent
   //  GSLMultiFit
   //   GSLSimAn
   //   Genetic
   ROOT::Math::Minimizer* minimum =
      ROOT::Math::Factory::CreateMinimizer(minName, algoName);

   // set tolerance , etc...
   minimum->SetMaxFunctionCalls(1000000); // for Minuit/Minuit2
   minimum->SetMaxIterations(10000);  // for GSL
   minimum->SetTolerance(0.001);
   minimum->SetPrintLevel(1);

   // create function wrapper for minimizer
   // a IMultiGenFunction type
   ROOT::Math::Functor f(&RosenBrock,6);
   minimum->SetFunction(f);

   // Set the free variables to be minimized !
   minimum->SetVariable(0,"x0",0, 0.0001);
   minimum->SetVariable(1,"x1",0, 0.0001);
   minimum->SetVariable(2,"x2",0, 0.0001);
   minimum->SetVariable(3,"p1",100, 0.01);
   minimum->SetVariable(4,"p2",0, 0.01);
   minimum->SetVariable(5,"p3",0, 0.01);

   // do the minimization
   minimum->Minimize();

   const double *xs = minimum->X();
   std::cout << "Minimum: f(" << xs[0] << "," << xs[1] << "): "
             << minimum->MinValue() << " vs " << f(xs) << std::endl;

   // expected minimum is 0
   if ( fabs(minimum->MinValue() - f(xs)) < 1.E-1)
      std::cout << "Minimizer " << minName << " - " << algoName
                << "   converged to the right minimum" << std::endl;
   else {
      std::cout << "Minimizer " << minName << " - " << algoName
                << "   failed to converge !!!" << std::endl;
      Error("NumericalMinimization","fail to converge");
   }

   /// start the check
   auto gr0c = corrected_gr(gr0, xs[0]);
   auto gr1c = corrected_gr(gr1, xs[1]);
   auto gr2c = corrected_gr(gr2, xs[2]);

   auto fun1 = new TF1("fun1","[0]*x+[1]*x*x+[2]*x*x*x", -1, 9);
   fun1->SetParameter(0,xs[3]);
   fun1->SetParameter(1,xs[4]);
   fun1->SetParameter(2,xs[5]);
   fun1->SetLineColor(3);

   fun1->Draw();
   fun1->GetXaxis()->SetTitle("U [kV]");
   fun1->GetYaxis()->SetTitle("I [#muA]");
   gr2c->SetLineColor(2);
   gr2c->SetMarkerColor(2);
   gr1c->SetLineColor(4);
   gr1c->SetMarkerColor(4);

   gr0c->Draw("P same");
   gr1c->Draw("P same");
   gr2c->Draw("P same");

   auto lg = new TLegend(0.2,0.8,0.4,0.93);
   lg->AddEntry(gr2c,"Picoammeter","P");
   lg->AddEntry(gr1c,"Iseg","P");
   lg->AddEntry(gr0c,"Dongwen","P");
   lg->Draw();

   return 0;
}

int testFit()
{
  auto fin1 = new TFile("fout1.root","read");
  gr0 = (TGraphErrors*)fin1->Get("gr0");
  gr1 = (TGraphErrors*)fin1->Get("gr1");
  gr2 = (TGraphErrors*)fin1->Get("gr2");

//   cout << gr0->GetN() << endl;
  return NumericalMinimization(); 
}
