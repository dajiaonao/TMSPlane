#include <iostream>
#include <utility>
#include <cfloat>
#include <vector>
#include <cmath>
#include "common.h"
#include <TF1.h>
#include <TGraph.h>

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
  int w1;
  int w2;
  float Q;
  Sig(int t_im, int t_w1, int t_w2, float t_Q): im(t_im),w1(t_w1),w2(t_w2),Q(t_Q){};
};


class SignalProcessor{
 public:
  size_t nSamples{16384};
  size_t nAdcCh;
  vector< double > fltParam{100,200,300,-1};
  double* measParam{nullptr};
  size_t nMeasParam{2};
  float x_thre{0.05};
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
};

void SignalProcessor::test2(){
  std::cout << "testing 2" << std::endl;
  std::cout << sRanges.size() << std::endl;
}

float SignalProcessor::correction(size_t ich, float raw, int opt){
  /// need to add protections: empty function or graph; out of range
  return opt==0? corr_TF1[ich]->Eval(raw): corr_spine[ich]->Eval(raw);
}

void SignalProcessor::check_signal(size_t idx, vector< Sig >* v){

  float halfQ = 0.5*scrAry[idx];
  /// find the low edge
  size_t il = idx;
  for(; il>0; il--){if(scrAry[il]<halfQ) break;}

  /// find the high edge
  size_t ih = idx;
  for(; ih<nSamples; ih++){if(scrAry[ih]<halfQ) break;}

  /// find the middle point
  size_t im = (size_t) (0.5*(il+ih));
  float newQ = 0.;
  const size_t N = 10;
  for(size_t i=-N; i<N; i++){newQ += scrAry[im+i];} 
  newQ /= N;


  float Q1 = 0.1*newQ;
  size_t il1 = im;
  for(; il1>0; il1--){if(scrAry[il1]<Q1) break;}
  size_t ih1 = im;
  for(; ih1<nSamples; ih1++){if(scrAry[ih1]<Q1) break;}

  float Q2 = 0.9*newQ;
  size_t il2 = im;
  for(; il2>0; il2--){if(scrAry[il2]<Q1) break;}
  size_t ih2 = im;
  for(; ih2<nSamples; ih2++){if(scrAry[ih2]<Q1) break;}

  //// save what? ih1-il1, ih2-il2, newQ, im
  v->emplace_back(im, ih1-il1, ih2-il2, newQ);

  return;
}


int SignalProcessor::measure_pulse2(const AWBT *adcData, int chan)
{
  /// do it for each channel
  std::cout << "dda" << std::endl;
  for(size_t iCh=0; iCh<nAdcCh; iCh++) {
    if(chan>=0 && chan != int(iCh)) continue;

    std::cout << "chan " << iCh << std::endl;
    /// create the vector if not exist yet
    if(signals[iCh]) {
      signals[iCh]->clear();
     }else{
      signals[iCh] = new vector< Sig >();
      signals[iCh]->reserve(10);
     }
    auto sigV = signals[iCh];
    std::cout << "dd1" << std::endl;

    /// locate samples
    const AWBT* adcChData = adcData + nSamples * iCh;
    double* measChParam = measParam + nMeasParam * iCh;

    //// apply the filter
    filters_trapezoidal(nSamples, adcChData, scrAry, (size_t)fltParam[1], (size_t)fltParam[2], (double)fltParam[3]);
    return 0;

    //// Start working on the filtered sample
    //// find the largest point, if it's bigger than the threshold, find other local maximum
    int g_max_i = -999;
    int l_max_i = -999;
    float g_max_x = -999.;
    float l_max_x = -1999.;

    for(size_t i=0; i<nSamples; ++i){
      if(scrAry[i]>x_thre){
        if(scrAry[i]>l_max_x){
          l_max_i = i;
          l_max_x = scrAry[i];
         }else{
          if(l_max_i>0){
            check_signal(l_max_i, sigV);
            
            /// update the global maximum
            if(g_max_x<l_max_x){
              g_max_i = l_max_i;
              g_max_x = g_max_x;
             }

            /// reset, not the value of l_max_x is different with the inital one to indicate that there is at least one pass the threshold
            l_max_i = -1;
            l_max_x = -999.;
         } }
       }else{
        if(l_max_i<-10 && scrAry[i]>g_max_x){
          g_max_i = i;
          g_max_x = scrAry[i];
       } }

      //// if the is no maxima pass the threshold, process the global maximum -- it should be lower than the threshold.
      if(l_max_i<-10){
        check_signal(g_max_i, sigV);
   } } }

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
  if(order != CF_order){
    /// free the existing momery
    if(CF_order>=0){
      free(m_A); free(m_d1); free(m_d2); free(m_w0); free(m_w1); free(m_w2);
     }
    CF_order = order;

    //// create the new memory if needed
    if(CF_order>=0){
      m_A  = (double *)malloc(order *sizeof(double));
      m_d1 = (double *)malloc(order *sizeof(double));
      m_d2 = (double *)malloc(order *sizeof(double));
      m_w0 = (double *)calloc(order, sizeof(double));
      m_w1 = (double *)calloc(order, sizeof(double));
      m_w2 = (double *)calloc(order, sizeof(double));
    }
  }

  return;
 }

void Filter_ibl::apply(const AWBT *inWav){
  /* Reference: http://www.exstrom.com/journal/sigproc/ */
  /* https://github.com/ymei/WaveformAnalysis/blob/master/filters.c */

  /* order should be an even number.  if odd, it is rounded down */
  double a = tan(M_PI * CF_fc);
  double a2 = a*a;
  int lowpass = (CF_order>0);
  CF_order = abs(CF_order) / 2;

  for(ssize_t i=0; i<CF_order; i++) {
      double r = sin(M_PI*(2.0*i+1.0)/(4.0*CF_order));
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
      for(ssize_t j=0; j<CF_order; j++) {
          m_w0[j] = m_d1[j]*m_w1[j] + m_d2[j]*m_w2[j] + s;
          s = m_A[j]*(m_w0[j] + a*2.0*m_w1[j] + m_w2[j]);
          m_w2[j] = m_w1[j];
          m_w1[j] = m_w0[j];
      }
      outWav[i] = s;
  }

  return;
}
