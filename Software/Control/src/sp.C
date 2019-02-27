#include <iostream>
#include <utility>
#include <cfloat>
#include <vector>
#include <cmath>
#include "common.h"
#include <TF1.h>
#include <TGraph.h>

using namespace std;

typedef ANALYSIS_WAVEFORM_BASE_TYPE AWBT;

/// trapezoidal filter
int filters_trapezoidal(size_t wavLen, const AWBT *inWav, AWBT *outWav,
                        size_t k, size_t l, double M)
{
    double s, pp;
    ssize_t j, jk, jl, jkl;
    double vj, vjk, vjl, vjkl, dkl;

    s = 0.0; pp = 0.0;

    for(size_t i=0; i<wavLen; i++) {
        j=i; jk = j-k; jl = j-l; jkl = j-k-l;
        vj   = j>=0   ? inWav[j]   : inWav[0];
        vjk  = jk>=0  ? inWav[jk]  : inWav[0];
        vjl  = jl>=0  ? inWav[jl]  : inWav[0];
        vjkl = jkl>=0 ? inWav[jkl] : inWav[0];

        dkl = vj - vjk - vjl + vjkl;
        pp = pp + dkl;
        if(M>=0.0) {
            s = s + pp + dkl * M;
        }
        else { /* infinite decay time, so the input is a step function */
            s = s + dkl;
        }
        outWav[i] = s / (fabs(M) * (double)k);
    }
    return 0;
}

struct Sig{
  int im;
  int idx;
  int w0;
  int w1;
  int w2;
  float Q;
  Sig(int t_im, int t_idx, int t_w0, int t_w1, int t_w2, float t_Q): im(t_im),idx(t_idx),w0(t_w0),w1(t_w1),w2(t_w2),Q(t_Q){};
};


class SignalProcessor{
 public:
  size_t nSamples{16384};
  size_t nAdcCh{20};
  vector< double > fltParam{100,200,300,-1};
  double* measParam{nullptr};
  size_t nMeasParam{2};
  vector< float > ch_thre{20, 0.005};
  float x_thre{0.005};
//   void set_threshold(float x){x_thre = x;}

  vector< pair<size_t, size_t> > sRanges;
  vector< vector <Sig>* > signals{nAdcCh, nullptr};

  vector< TF1* > corr_TF1;
  vector< TGraph* > corr_spine;

//   SignalProcessor():scrAry(nullptr){};
  ~SignalProcessor(){
    if(scrAry) free(scrAry); 
   }

//  private:
  AWBT* scrAry{nullptr};

 public:
  void test(){
    std::cout << "testing" << std::endl;
  }

  void test2();
  void check_signal(size_t idx, vector< Sig >* v);
  int measure_pulse(const AWBT *adcData, int chan=-1);
  int measure_pulse2(const AWBT *adcData, int chan=-1);

  float correction(size_t ich, float raw, int opt=0);

 private:
  int get_indices(float q, size_t m);
};

void SignalProcessor::test2(){
  std::cout << "testing 2" << std::endl;
  std::cout << sRanges.size() << std::endl;
}

float SignalProcessor::correction(size_t ich, float raw, int opt){
  /// need to add protections: empty function or graph; out of range
  return opt==0? corr_TF1[ich]->Eval(raw): corr_spine[ich]->Eval(raw);
}


int SignalProcessor::get_indices(float q, size_t m){
  size_t il1 = m;
  for(; il1>0; il1--){if(scrAry[il1]<q) break;}
  size_t ih1 = m;
  for(; ih1<nSamples; ih1++){if(scrAry[ih1]<q) break;}

  return ih1-il1;
}

void SignalProcessor::check_signal(size_t idx, vector< Sig >* v){

  float halfQ = 0.5*scrAry[idx];
  /// find the low edge
  size_t il = idx;
  for(; il>0; il--){if(scrAry[il]<halfQ) break;}

  /// find the high edge
  size_t ih = idx;
  for(; ih<nSamples; ih++){if(scrAry[ih]<halfQ) break;}

//   cout << "il=" << il << " ih=" << ih << endl;

  /// find the middle point
  size_t im = (size_t) (0.5*(il+ih));
  float newQ = scrAry[im];
//   float newQ = 0.;
//   const int N = 10;
//   for(int i=-N; i<N; i++){
// //     cout << i << "->" << newQ << " / " << scrAry[idx] << " / " << scrAry[im] << endl;
//     newQ += scrAry[im+i];
//   } 
//   newQ /= (2*N);

  float Q2 = 0.9*newQ;
  size_t il2 = im;
  for(; il2>0; il2--){if(scrAry[il2]<Q2) break;}
  size_t ih2 = im;
  for(; ih2<nSamples; ih2++){if(scrAry[ih2]<Q2) break;}
//   cout << "il2=" << il2 << " ih2=" << ih2 << endl;

  float Q1 = 0.1*newQ;
  size_t il1 = il2;
  for(; il1>0; il1--){if(scrAry[il1]<Q1) break;}
  size_t ih1 = ih2;
  for(; ih1<nSamples; ih1++){if(scrAry[ih1]<Q1) break;}
//   cout << "il1=" << il1 << " ih1=" << ih1 << endl;

  size_t il0 = im;
  for(; il0>0; il0--){if(scrAry[il0]<x_thre) break;}
  size_t ih0 = im;
  for(; ih0<nSamples; ih0++){if(scrAry[ih0]<x_thre) break;}
//   cout << "il0=" << il0 << " ih0=" << ih0 << endl;

  //// save what? ih1-il1, ih2-il2, newQ, im
//   cout << v->size() << ": " << im << " " << idx << " " << ih0-il0 << " " << ih1-il1 << " " << ih2-il2 << " " << newQ << endl;
  v->emplace_back(im, idx, ih0-il0, ih1-il1, ih2-il2, newQ);
//   cout << "here" << endl;

  return;
}


int SignalProcessor::measure_pulse2(const AWBT *adcData, int chan)
{
  /// create the needed memory 
  if(!scrAry) scrAry = (AWBT*)calloc(nSamples, sizeof(AWBT));
  if(!measParam){
    nMeasParam = 2*sRanges.size()+2;
    measParam = (double*) calloc(nMeasParam*nAdcCh, sizeof(double));
   }

  /// do it for each channel
  for(size_t iCh=0; iCh<nAdcCh; iCh++) {
    if(chan>=0 && chan != int(iCh)) continue;

    x_thre = ch_thre[iCh];
//     std::cout << "chan " << iCh << std::endl;
    /// create the vector if not exist yet
    if(signals[iCh]) {
      signals[iCh]->clear();
     }else{
      signals[iCh] = new vector< Sig >();
      signals[iCh]->reserve(10);
     }
    auto& sigV = signals[iCh];
//     std::cout << "sigV: " << sigV->size() << std::endl;

    /// locate samples
    const AWBT* adcChData = adcData + nSamples * iCh;
    double* measChParam = measParam + nMeasParam * iCh;


    size_t nBl = (size_t)fltParam[0];
    double bl = 0.0;
    double bln = 0.0;
    for(size_t i=0; i<nBl; i++) {
//       cout << iCh << " " <<  i << " " << adcChData[i] << endl; 
      bl += adcChData[i];
      bln += adcChData[i] * adcChData[i];
     }
    bl /= (double)nBl;
    bln = (bln - (double)nBl * bl*bl)/(nBl - 1.0);
    measChParam[0] = bl;
    measChParam[1] = bln>0?sqrt(bln):-sqrt(-bln);
//     cout << " ------ " << measChParam[0] << " " << measChParam[1] << endl; 

    //// apply the filter
//     std::cout << "apply the filter" << std::endl;
    filters_trapezoidal(nSamples, adcChData, scrAry, (size_t)fltParam[1], (size_t)fltParam[2], (double)fltParam[3]);
//     std::cout << "apply the filter done" << std::endl;

    //// Start working on the filtered sample
    //// find the largest point, if it's bigger than the threshold, find other local maximum
    int g_max_i = -999;
    int l_max_i = -999;
    float g_max_x = -999.;
    float l_max_x = -1999.;

    const float c_thre = 0.5;
    const int nSmaller = 20; /// if nSmaller data less than the maximum, it will be considered as a local maximum. To avoid too many local maximum in vincinty due to fluctuation.
    const int nLarger = 20; /// start recount 

    int ismaller(0), ilarger(0);
    for(size_t i=0; i<nSamples; ++i){
      if(scrAry[i]>l_max_x){
        ilarger++;
        l_max_i = i;
        l_max_x = scrAry[i];
        ismaller = 0;
       }else{
        if(scrAry[i]<l_max_x*c_thre) ismaller++;
//         if(sigV->size()==0 && scrAry[i]>x_thre) cout << i << ": l_max_i " << l_max_i << ", l_max_x " << l_max_x << ", ilarger " << ilarger << ", ismaller " << ismaller << endl;

        if(ismaller>nSmaller){
          if(ilarger>nLarger && l_max_x > x_thre){
//             cout << "l_max_i " << l_max_i << endl;
//             cout << "l_max_x " << l_max_x << endl;
//             cout << "ilarger " << ilarger << endl;
//             cout << "ismaller " << ismaller << endl;
            check_signal(l_max_i, sigV);
           }

          /// update the global maximum
          if(g_max_x<l_max_x){
            g_max_i = l_max_i;
            g_max_x = l_max_x;
           }

          /// reset anyway
          ilarger = 0;
          l_max_i = -1;
          l_max_x = -999.;
       } }
      /// update the global maximum
      if(g_max_x<l_max_x){
        g_max_i = l_max_i;
        g_max_x = l_max_x;
       }

     }
    if(sigV->size()==0) check_signal(g_max_i, sigV);
   }


//       if(scrAry[i]>x_thre){
//         if(scrAry[i]>l_max_x){
//           l_max_i = i;
//           l_max_x = scrAry[i];
//           ismaller = 0; /// reset the counter
//           ilarger++;
//           std::cout << "larger++" << l_max_i << " "  << l_max_x << " " << ilarger << endl;
// 
//          }else{
//           if(scrAry[i]<l_max_x*c_thre) ismaller++;
//           if(ismaller>1) std::cout << i << " " << scrAry[i]  << " < " << l_max_x << " ->" << l_max_x*c_thre << " " << ismaller << endl;
// 
//           if(ismaller>nSmaller){
//             std::cout << "hey : " << ilarger << std::endl;
//             if(ilarger>nLarger){
//               std::cout << "find local: " << l_max_i << std::endl;
//               check_signal(l_max_i, sigV);
//               ilarger = 0;
//              }else{
//                std::cout << "larger--" << l_max_i << " "  << l_max_x << " " << ilarger << endl;
//              }
//             
//             /// update the global maximum
//             if(g_max_x<l_max_x){
//               g_max_i = l_max_i;
//               g_max_x = g_max_x;
//              }
// 
//             /// reset, not the value of l_max_x is different with the inital one to indicate that there is at least one pass the threshold
//             l_max_i = -1;
//             l_max_x = -999.;
//          } }
//        }else{
//         if(l_max_i<-10 && scrAry[i]>g_max_x){
//           g_max_i = i;
//           g_max_x = scrAry[i];
//      } } }
      
      //// if the is no maxima pass the threshold, process the global maximum -- it should be lower than the threshold.
//       if(l_max_i<-10){
//         check_signal(g_max_i, sigV);
//      } }

  return 0;
}

int SignalProcessor::measure_pulse(const AWBT *adcData, int chan)
{
    size_t nBl;
    const AWBT *adcChData;
    double *measChParam, v, bl, bln;

    nBl = (size_t)fltParam[0];
    if(!scrAry) scrAry = (AWBT*)calloc(nSamples, sizeof(AWBT));
    if(sRanges.size()==0){
      sRanges.emplace_back(std::make_pair(0,nSamples));
     }
    nMeasParam = 2*sRanges.size()+2;
    if(!measParam){
      measParam = (double*) calloc(nMeasParam*nAdcCh, sizeof(double));
     }

    for(size_t iCh=0; iCh<nAdcCh; iCh++) {
        if(chan>=0 && chan != int(iCh)) continue;

        adcChData = adcData + nSamples * iCh;
        measChParam = measParam + nMeasParam * iCh;
        /* baseline and baseline noise */
        bl = 0.0; bln = 0.0;
        for(size_t i=0; i<nBl; i++) {
            bl += adcChData[i];
            bln += adcChData[i] * adcChData[i];
        }
        bl /= (double)nBl;
        bln = (bln - (double)nBl * bl*bl)/(nBl - 1.0);
//         if(bln<=0){printf("%g %g %ld\n", bln, bl, nBl);}
        measChParam[0] = bl;
        measChParam[1] = bln>0?sqrt(bln):-sqrt(-bln);
        /* peak location and height */
        filters_trapezoidal(nSamples, adcChData, scrAry, (size_t)fltParam[1], (size_t)fltParam[2], (double)fltParam[3]);

        size_t t=2;
        for(auto& x: sRanges){
          v = -DBL_MAX; 
          size_t j = 0;
          for(size_t i=x.first; i<x.second; i++) {
              if(scrAry[i] > v) {
                  v = scrAry[i];
                  j = i;
              }
          }
          measChParam[t] = j;
          measChParam[t+1] = v;
          t += 2;
        }
    }

    return 0;
}

class Filter_ibb{
 public:
   int CF_wavLen{-1};
   int CF_order{-1};
   double CF_fl{-1};
   double CF_fh{-1};
   AWBT *outWav{nullptr};

   Filter_ibb(int wavLen):CF_wavLen(wavLen){ if(wavLen>0) outWav = (AWBT *)malloc(wavLen *sizeof(AWBT)); }
   ~Filter_ibb(){
     if(outWav) free(outWav);
     setup(0, -1,-1);
   };
   void setup(int order, double fl, double fh);
   void apply(const AWBT *inWav);

 private:
  double *m_A{nullptr};
  double *m_d1{nullptr};
  double *m_d2{nullptr};
  double *m_d3{nullptr};
  double *m_d4{nullptr};
  double *m_w0{nullptr};
  double *m_w1{nullptr};
  double *m_w2{nullptr};
  double *m_w3{nullptr};
  double *m_w4{nullptr};
};

void Filter_ibb::setup(int order, double fl, double fh){
  CF_fl = fl;
  CF_fh = fh;

  if(abs(order) != abs(CF_order)){
    /// free the existing momery
    if(CF_order!=0){
      free(m_A); free(m_d1); free(m_d2); free(m_d3); free(m_d4); free(m_w0); free(m_w1); free(m_w2); free(m_w3); free(m_w4);
     }

    //// create the new memory if needed
    int order1 = abs(order)/4;
    if(order1!=0){
      m_A  = (double *)malloc(order1 *sizeof(double));
      m_d1 = (double *)malloc(order1 *sizeof(double));
      m_d2 = (double *)malloc(order1 *sizeof(double));
      m_d3 = (double *)malloc(order1 *sizeof(double));
      m_d4 = (double *)malloc(order1 *sizeof(double));
      m_w0 = (double *)calloc(order1, sizeof(double));
      m_w1 = (double *)calloc(order1, sizeof(double));
      m_w2 = (double *)calloc(order1, sizeof(double));
      m_w3 = (double *)calloc(order1, sizeof(double));
      m_w4 = (double *)calloc(order1, sizeof(double));
    }
  }
  CF_order = order;

  return;
 }


void Filter_ibb::apply(const AWBT *inWav){
    if(CF_order % 4 || CF_fl >= CF_fh) {
        error_printf("%s(): improper arguments, CF_order(=%d) must be 4, 8, 16... and fl(=%g)<fh(=%g).\n", __FUNCTION__, CF_order, CF_fl, CF_fh);
        return;
    }

    double a, a2, b, b2, r;

    int pass = (CF_order>0);
    int order = abs(CF_order)/4;
    a = cos(M_PI*(CF_fh+CF_fl)) / cos(M_PI*(CF_fh-CF_fl));
    a2 = a * a;
    b = tan(M_PI*(CF_fh-CF_fl));
    b2 = b * b;


    for(ssize_t i=0; i<order; i++) {
        r = sin(M_PI*(2.0*i+1.0)/(4.0*order));
        double s = b2 + 2.0*b*r + 1.0;

        if(pass) { /* bandpass */
            m_A[i] = b2/s;
        } else {   /* bandstop */
            m_A[i] = 1.0/s;
        }

        m_d1[i] = 4.0*a*(1.0+b*r)/s;
        m_d2[i] = 2.0*(b2-2.0*a2-1.0)/s;
        m_d3[i] = 4.0*a*(1.0-b*r)/s;
        m_d4[i] = -(b2 - 2.0*b*r + 1.0)/s;
    }

    if(pass == 0) { /* bandstop */
        r = 4.0*a;
        a = 4.0*a2+2.0;
    }

    for(ssize_t i=0; i<CF_wavLen; i++) {
        double s = inWav[i];
        for(ssize_t j=0; j<order; j++) {
            m_w0[j] = m_d1[j]*m_w1[j] + m_d2[j]*m_w2[j]+ m_d3[j]*m_w3[j]+ m_d4[j]*m_w4[j] + s;
            if(pass) {
                s = m_A[j]*(m_w0[j] - 2.0*m_w2[j] + m_w4[j]);
            } else {
                s = m_A[j]*(m_w0[j] - r*m_w1[j] + a*m_w2[j]- r*m_w3[j] + m_w4[j]);
            }
            m_w4[j] = m_w3[j];
            m_w3[j] = m_w2[j];
            m_w2[j] = m_w1[j];
            m_w1[j] = m_w0[j];
        }
        outWav[i] = s;
    }

    return;
}

class Filter_ibl{
 public:
   int CF_wavLen{-1};
   int CF_order{-1};
   double CF_fc{-1};
   AWBT *outWav{nullptr};

   Filter_ibl(int wavLen):CF_wavLen(wavLen){ if(wavLen>0) outWav = (AWBT *)malloc(wavLen *sizeof(AWBT)); }
   ~Filter_ibl(){
     if(outWav) free(outWav);
     setup(-1, -1);
   };
   void setup(int order, double fc);
   void apply(const AWBT *inWav);

 private:
  double *m_A{nullptr};
  double *m_d1{nullptr};
  double *m_d2{nullptr};
  double *m_w0{nullptr};
  double *m_w1{nullptr};
  double *m_w2{nullptr};
};

void Filter_ibl::setup(int order, double fc){
  CF_fc = fc;
  if(abs(order) != abs(CF_order)){
    /// free the existing momery
    if(CF_order!=0){
      free(m_A); free(m_d1); free(m_d2); free(m_w0); free(m_w1); free(m_w2);
     }

    //// create the new memory if needed
    int order1 = abs(order)/2;
    if(order1!=0){
      m_A  = (double *)malloc(order1 *sizeof(double));
      m_d1 = (double *)malloc(order1 *sizeof(double));
      m_d2 = (double *)malloc(order1 *sizeof(double));
      m_w0 = (double *)calloc(order1, sizeof(double));
      m_w1 = (double *)calloc(order1, sizeof(double));
      m_w2 = (double *)calloc(order1, sizeof(double));
    }
    cout << "Done " << order1 << endl;
  }
  CF_order = order;


  return;
 }

void Filter_ibl::apply(const AWBT *inWav){
  /* Reference: http://www.exstrom.com/journal/sigproc/ */
  /* https://github.com/ymei/WaveformAnalysis/blob/master/filters.c */

  /* order should be an even number.  if odd, it is rounded down */
  double a = tan(M_PI * CF_fc);
  double a2 = a*a;
  int lowpass = (CF_order>0);
  int order = abs(CF_order) / 2;

  for(ssize_t i=0; i<order; i++) {
      double r = sin(M_PI*(2.0*i+1.0)/(4.0*order));
      double s = a2 + 2.0*a*r + 1.0;
      if(lowpass) {
          m_A[i] = a2/s;
      } else {
          m_A[i] = 1.0/s;
      }
      m_d1[i] = 2.0*(1-a2)/s;
      m_d2[i] = -(a2 - 2.0*a*r + 1.0)/s;
  }
  if(lowpass) {a = 1.0;} else {a = -1.0;}
  for(ssize_t i=0; i<CF_wavLen; i++) {
      double s = inWav[i];
      for(ssize_t j=0; j<order; j++) {
          m_w0[j] = m_d1[j]*m_w1[j] + m_d2[j]*m_w2[j] + s;
          s = m_A[j]*(m_w0[j] + a*2.0*m_w1[j] + m_w2[j]);
          m_w2[j] = m_w1[j];
          m_w1[j] = m_w0[j];
      }
      outWav[i] = s;
  }

  return;
}
