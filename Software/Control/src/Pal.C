void Pal2()
{
   static Int_t  colors[100];
   static Bool_t initialized = kFALSE;
   const int NP = 4;
   Double_t Red[NP]    = { 0., 1, 0.0, 1};
   Double_t Green[NP]  = { 0., 1, 0.5, 0};
   Double_t Blue[NP]   = { 0., 1, 1.0, 0};
   Double_t Length[NP] = { 0, 0.05 ,0.1, 1.0};
   if(!initialized){
      Int_t FI = TColor::CreateGradientColorTable(NP,Length,Red,Green,Blue,98);
      for (int i=0; i<98; i++) colors[i+2] = FI+i;
      initialized = kTRUE;

      colors[0] = 1;
      colors[1] = 1;
      colors[2] = 1;
      colors[3] = 1;
      colors[4] = 1;
      colors[5] = 1;
      colors[6] = 1;
      colors[7] = 1;
      colors[8] = 1;
      colors[9] = 0;
      colors[10] = 0;
      gStyle->SetPalette(100,colors);
//       for(int i=0; i<100; i++){cout << colors[i] << endl;}
//       cout << "Done 1" << endl;
      return;
   }
   gStyle->SetPalette(100,colors);
//    cout << "Done" << endl;
}
// Pal2();
