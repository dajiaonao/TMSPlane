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

class SignalProcessor{
 public:
  size_t nSamples{16384};
  size_t nAdcCh;
  vector< double > fltParam{100,200,300,-1};
  double* measParam{nullptr};
  size_t nMeasParam{2};
  vector< pair<size_t, size_t> > sRanges;

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
  int measure_pulse(const AWBT *adcData, int chan=-1);

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
