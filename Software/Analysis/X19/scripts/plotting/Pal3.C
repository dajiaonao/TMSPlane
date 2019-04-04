void Pal3()
{
   static Int_t  colors[100];
   static Bool_t initialized = kFALSE;
   const int NP = 4;
   Double_t Red[NP]    = { 0, 1, 1, 1};
   Double_t Green[NP]  = { 0, 1, 1, 0};
   Double_t Blue[NP]   = { 0, 1, 0, 0};
   Double_t Length[NP] = { 0, 0.02 ,0.1, 1.0};
   if(!initialized){
      Int_t FI = TColor::CreateGradientColorTable(NP,Length,Red,Green,Blue,100);
      for (int i=0; i<100; i++) colors[i] = FI+i;
      initialized = kTRUE;
      gStyle->SetPalette(100,colors);
      gStyle->SetNumberContours(99);
      return;
   }
   gStyle->SetPalette(100,colors);
   gStyle->SetNumberContours(99);
}
