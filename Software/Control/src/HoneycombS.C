#include "helix.C"
void HoneycombS(TH2Poly* h, Double_t a, Int_t n)
 {
   Double_t x[6], y[6];
   float B = 0.5*a;
   float A = B/TMath::Sqrt(3);

   double x0, y0;
   for(int i=0;i<n;i++){
     hex_l2xy(a,i,&x0,&y0);

     x[0] = x0 - A;
     y[0] = y0 - B;
     x[1] = x[0] - A;
     y[1] = y[0] + B;
     x[2] = x[1] + A;
     y[2] = y[1] + B;
     x[3] = x[2] + 2*A;
     y[3] = y[2];
     x[4] = x[3] + A;
     y[4] = y[3] - B;
     x[5] = x[4] - A;
     y[5] = y[4] - B;

     h->AddBin(6, x, y);
    }

   return;
 }


