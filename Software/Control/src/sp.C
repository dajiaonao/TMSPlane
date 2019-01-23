#include <iostream>
#include <utility>
#include <cfloat>
#include <vector>
#include "common.h"

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

};

void SignalProcessor::test2(){
  std::cout << "testing 2" << std::endl;
  std::cout << sRanges.size() << std::endl;
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
        if(chan>=0 && chan != iCh) continue;

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
