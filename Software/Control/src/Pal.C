void Pal2()
{
   static Int_t  colors[100];
   static Bool_t initialized = kFALSE;
   Double_t Red[3]    = { 0.00, 0.50, 1.00};
   Double_t Green[3]  = { 0.50, 0.00, 1.00};
   Double_t Blue[3]   = { 1.00, 0.00, 0.50};
   Double_t Length[3] = { -100, 0   , 0.5};
   if(!initialized){
      Int_t FI = TColor::CreateGradientColorTable(3,Length,Red,Green,Blue,100);
      for (int i=0; i<100; i++) colors[i] = FI+i;
      initialized = kTRUE;
      gStyle->SetPalette(100,colors);
      cout << "Done 1" << endl;
      return;
   }
   gStyle->SetPalette(100,colors);
   cout << "Done" << endl;
}
// Pal2();
