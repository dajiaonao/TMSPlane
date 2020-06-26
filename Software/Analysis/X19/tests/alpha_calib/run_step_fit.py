#!/usr/bin/env python3
from array import array
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm, kstest
from math import sqrt

pA = 1e-12

def test():
    a = StepFitter()
    a.test()

    datax = [4,5,33.4,17]
    data = array('f', datax)
    a.fit(len(datax), data)

def funx(x):
    return x[0]+3*x[0]*x[0]

def remove_outlier2(data1, x1):
    ### find seed: 1) 5 sigma away from mean of the rsidual, 2) the one before are after are more than 3 sigma away
    N = len(data1)
    rsd = [data1[i]-ffunY(x1, i) for i in range(N)]
    x5 = int(x1[5]) if x1[5] is not None else N
    x4 = int(x1[4]) if x1[4] is not None else 0
    print(x4,x5)
    std1 = np.std(rsd[:x4]+rsd[x5:])
    std2 = np.std(rsd[x4:x5])

    seeds = []
    print(std1, std2)
    for i in range(N):
        std = std2 if x4 < i < x5 else std1
        if std>3: std = 5
        if abs(rsd[i] + (rsd[i-1] if i>0 else 0) + (rsd[i+1] if i<N-1 else 0))>12*std: seeds.append(i)
#         print(rsd[i], 5*std, rsd[i-1] if i>0 else None, 3*std, rsd[i+1] if i<N-1 else None)
#         if abs(rsd[i])>5*std and (i==0 or abs(rsd[i-1])>3*std) and (i>N-2 or abs(rsd[i+1])>3*std): seeds.append(i)

    print(seeds)
    ### find range: find the begining and end where it's on the other side of  the mean
    for s in seeds:
        j = 1
        while s+j<N and rsd[s+j] > 0: j += 1

        k = -1
        while s+k>=0 and rsd[s+k] >0: k -= 1

        ### mask the range, and add two more points
        for m in range(s+k-10, s+j+10):
            if 0<=m<N: data1[m] = None

    return [l for l in data1 if l is not None]

def remove_outlier(x):
    '''To deal with HV trips'''
    N = len(x)
    y = [0]*N
    for i in range(N):
        vp = x[i]+20
        vm = x[i]-20
        if i>=15 and ( (x[i-11]<vm and x[i-12]<vm and x[i-13]<vm and x[i-14]<vm and x[i-15]<vm) or (x[i-11]>vp and x[i-12]>vp and x[i-13]>vp and x[i-14]>vp and x[i-15]>vp) ):
            y[i] = 1
        if i<N-15 and ( (x[i+11]<vm and x[i+12]<vm and x[i+13]<vm and x[i+14]<vm and x[i+15]<vm) or (x[i+11]>vp and x[i+12]>vp and x[i+13]>vp and x[i+14]>vp and x[i+15]>vp) ):
            y[i] = 1

    for i in range(N):
        if y[i] >0: 
            for j in range(-10,10):
                if 0 <= i+j < N:
                    x[i+j] = None
                    print(f"setting {i+j}")

    return [a for a in x if a is not None]


class SPlusBPdf:
    def __init__(self, pars=[0]):
        self.pars = pars

    def func(self):
        return x[0]+pars[0]*x[0]*x[0]

def ffunY(x, i):
    y = x[0]+x[1]*i+x[2]*i*i
    if x[4]<i<x[5]: y -= x[3]

    return y

def ffun(x, data1, Vs=(1,1)):
    '''Calculate chi2 using given variance in Vs'''
    L = 0
    for i in range(len(data1)):
        y = ffunY(x,i)
        v = Vs[1] if x[4]<i<x[5] else Vs[0] ### variance
        L += pow(y-data1[i],2)/v
    return L

def test3b():
    res = minimize(funx,[3])
    print(res.x)
    

    pdf1 = SPlusBPdf([33])
    res2 = minimize(pdf1.func, [20])
    print(res2.x)

def getRange(i01, nMax=100, show=False):
    NT = len(i01)
    i2 = [0]*NT

    for i in range(NT):
        if i<nMax: i2[i] = np.mean(i01[:i+1])-np.mean(i01[i:2*(i+1)])
        elif i==NT-1: i2[i] = 0
        elif i>=NT-nMax: i2[i] = np.mean(i01[2*(i+1)-NT:i+1])-np.mean(i01[i+1:])
        else: i2[i] = np.mean(i01[i+1-nMax:i+1])-np.mean(i01[i+1:i+1+nMax])

    if show:
        plt.plot(i2)
        plt.show()


    ### find max
    index1, value1 = max(enumerate(i2), key=lambda x:x[1])
#     print(index1, value1)

    index2, value2 = min(enumerate(i2), key=lambda x:x[1])
#     print(index2, value2)

    v = max([abs(value1),abs(value2)])

    if index1 > index2:
        index1,index2 = index2, index1
        v *= -1

    d = index2 - index1
    start0 = index1 - d
    start1 = index1
    end1 = index2
    end2 = index2 + d

    if start0 <= 0: start0 = None
    if end2 >= NT: end2 = None

    return (start0, start1, end1, end2, d, v)


def fit_ds(ds, show=False, check=False):
#     r = getRange(ds, show=True)
    r = getRange(ds)
    if show: print('r=',r)

    data1 = None
    if r[0]: data1 = ds[r[0]:]
    elif r[3]: data1 = ds[:r[3]]
    else: data1 = ds

    V0 = (1,1) ### initial variance
    res = minimize(ffun, [-53,0,0,r[5],r[1],r[2]], args=(data1, V0), method='Powell')
#     print(res)

    ### redo the fit with the uncertainty difference taken into account
    rsd = [data1[i]-ffunY(res.x, i) for i in range(len(data1))]
    V1 = (np.var(rsd[:int(res.x[4])]+rsd[int(res.x[5]):]), np.var(rsd[int(res.x[4]):int(res.x[5])]))
#     print("using", V1)

#     plt.plot(data1)
#     data1 = remove_outlier2(data1, res.x)
#     plt.plot(data1)
#     plt.show()

    res = minimize(ffun, res.x, args=(data1, V1), method='Powell')

#     rsd2 = [data1[i]-ffunY(res.x, i) for i in range(len(data1))]
#     V2 = (np.var(rsd[:int(res.x[4])]+rsd[int(res.x[5]):]), np.var(rsd[int(res.x[4]):int(res.x[5])]))
#     print("V1:", V1)
#     print("V2:", V2)


    rsd1 = rsd[int(res.x[4]):int(res.x[5])]
    rsd2 = rsd[:int(res.x[4])]+rsd[int(res.x[5]):]
    if res.x[3]<0: rsd1,rsd2 = rsd2,rsd1 ### on, off


    ### calculation
    on_std = np.std(rsd1)
    off_std = np.std(rsd2)

    on_err = on_std/sqrt(len(rsd1))
    off_err = off_std/sqrt(len(rsd2))
    tot_err = sqrt(on_err*on_err + off_err*off_err)


    if show:
        print(res)
        reco1 = [ffunY(res.x, i) for i in range(len(data1))]

        plt.plot(data1)
        plt.plot(reco1)
        plt.show()


    if check:
#         print(res)
        rsd = [data1[i]-ffunY(res.x, i) for i in range(len(data1))]
        plt.plot(rsd)
        plt.show()

        loc1, scale1 = norm.fit(rsd1)
        good1 = kstest(rsd1/scale1, 'norm')
        print('rsd1:', loc1, scale1, good1)

        loc2, scale2 = norm.fit(rsd2)
        good2 = kstest(rsd2/scale2, 'norm')
        print('rsd2:', loc2, scale2, good2)


        print(f"on: {on_std:.3g} [{on_err:.3g}]; off: {off_std:.3g} [{off_err:.3g}] --> tot: {tot_err:.3g}")

#         V1 = (on_std*on_std, off_std*off_std) if res.x[3]>0 else (off_std*off_std, on_std*on_std)
#         res = minimize(ffun, res.x, args=(data1, V1), method='Powell')
#         print(res)
# 
#         reco1 = [ffunY(res.x, i) for i in range(len(data1))]
# 
#         plt.plot(data1)
#         plt.plot(reco1)
#         plt.show()

        ### plot
        plt.hist(rsd1,alpha=0.5, label='alpha on')
        plt.hist(rsd2,alpha=0.5, label='alpha off')
        plt.legend(loc='upper right')
        plt.show()

    return res.x[3], tot_err

def test2():
    '''Check data'''
#     fname = '/data/TMS_data/raw/Jun17a/Air_acceptanceMeasureD4mm_FocusOn_Uc2000V_read1000.dat'
    fname = '/data/TMS_data/raw/Jun17a/Air_acceptanceMeasureD4mm_FocusOn_Uc1500V.dat'

    dList = {}
    with open(fname,'r') as fin1:
        lines = fin1.readlines()

    for line in lines:
        fs = line.split()
        if float(fs[2])<6000: continue

        try:
            dList[fs[0]].append(float(fs[1])/pA)
        except KeyError:
            dList[fs[0]] = [float(fs[1])/pA]

    results = []
    i0 = None
    for k,v in dList.items():
        print(k, len(v))
#         if i0 is None: i0 = (k, v)
#         fr = fit_ds(v, show=True)
        fr = fit_ds(v, show=False, check=False)
#         fr = fit_ds(v, show=False, check=True)

#         return

        results.append(fr)

#     plt.plot(results)
    plt.hist([abs(a[0]) for a in results])
    plt.show()

#     print(i0[0], i0[1])

#     a = StepFitter()
#     data = array('f', i0[1])
#     a.fit(len(data), data)

#     fit_ds(i0[1])

#     r = getRange(i0[1])
#     print('r=',r)
# 
#     global data1, sRegions
# 
#     if r[0]: data1 = i0[1][r[0]:]
#     elif r[3]: data1 = i0[1][:r[3]]
#     else: data1 = i0[1]
# #     data1 = i0[1][30:]
#     sRegions = []
# 
#     res = minimize(ffun, [-53,0,0,r[5],r[1],r[2]], method='Powell')
#     print(res, res.x, ffun(res.x))
# 
#     reco1 = [ffunY(res.x, i) for i in range(len(data1))]
# 
#     plt.plot(data1)
#     plt.plot(reco1)
#     plt.show()

    return

    NT = len(i0[1])
    filter1 = False
    filter2 = True

    ### try filter 1
    if filter1 :
        N = 5

        i1 = [0]*NT
        i1e = [-1]*NT
        for j in range(NT):
            if j<N or j>= NT-N: i1[j] = i0[1][j]
            else:
    #             i1[j] = sum(i0[1][j-N:j+N])/(2*N)
                i1[j] = np.mean(i0[1][j-N:j+N])
                i1e[j] = np.std(i0[1][j-N:j+N])

        nE = 10
        for j in range(NT-nE):
            if i1[j+nE-2] > i1[j]+2*i1e[j] and i1[j+nE-1] > i1[j]+2*i1e[j] and i1[j+nE] > i1[j]+2*i1e[j]:
                print(j,'+')
            if i1[j+nE-2] < i1[j]-2*i1e[j] and i1[j+nE-1] < i1[j]-2*i1e[j] and i1[j+nE] < i1[j]-2*i1e[j]:
                print(j, '-')



        plt.plot(i0[1])
        plt.plot(i1)
    #     plt.plot(i1e)

    if filter2:
        i2 = [0]*NT
#         i01=i0[1]
#         i01=dList['2020-06-18_17:30:23']
        for k,v in dList.items():
            print(k)
            i01 = v
            nMax = 100
            for i in range(NT):
                if i<nMax: i2[i] = np.mean(i01[:i+1])-np.mean(i01[i:2*(i+1)])
                elif i==NT-1: i2[i] = 0
                elif i>=NT-nMax: i2[i] = np.mean(i01[2*(i+1)-NT:i+1])-np.mean(i01[i+1:])
                else: i2[i] = np.mean(i01[i+1-nMax:i+1])-np.mean(i01[i+1:i+1+nMax])
            plt.plot(i2)
        plt.show()

#             ax = input('next:')
#             plt.clear()


        i01=dList['2020-06-18_17:39:59']

        nMax = 100
        for i in range(NT):
            if i<nMax: i2[i] = np.mean(i01[:i+1])-np.mean(i01[i:2*(i+1)])
            elif i==NT-1: i2[i] = 0
            elif i>=NT-nMax: i2[i] = np.mean(i01[2*(i+1)-NT:i+1])-np.mean(i01[i+1:])
            else: i2[i] = np.mean(i01[i+1-nMax:i+1])-np.mean(i01[i+1:i+1+nMax])
        plt.plot(i2)

    plt.show()

def check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI.dat', startIdx=None):
    '''Check data'''
#     fname = '/data/TMS_data/raw/Jun25a/Argon_totalI.dat'

    dList = {}
    with open(fname,'r') as fin1:
        lines = fin1.readlines()

    for line in lines:
        fs = line.split()
        if startIdx is not None and float(fs[2])<startIdx: continue

        try:
            dList[fs[0]].append(float(fs[1])/pA)
        except KeyError:
            dList[fs[0]] = [float(fs[1])/pA]

    results = []
    i0 = None
    for k,v in dList.items():
        print(k, len(v))

#         print("ttt")
#         plt.plot(v)
#         ds1 = remove_outlier(v)
#         plt.plot(ds1)
#         plt.show()
# 
#         v = ds1
#         print("ttt")



        fr = fit_ds(v, show=True)
#         fr = fit_ds(v, show=True, check=True)
#         fr = fit_ds(v, show=False, check=True)
#         fr = fit_ds(v, show=False, check=False)

        results.append(fr)

#     plt.plot(results)
    plt.hist([abs(a[0]) for a in results])
    plt.show()

    x = range(len(results))
    y = [abs(a[0]) for a in results]
    e = [a[1] for a in results]
    plt.errorbar(x, y, yerr=e, fmt='o')
    plt.show()



if __name__ == '__main__':
#     test()
#     test2()
#     test3()
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI.dat')
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI_Fd1000.dat')
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI_Fd2500.dat')
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI_Fd3000.dat')
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI_Fd2000b.dat')
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI_Fd2000_Fc1000.dat.1')
#     check_ds(fname = '/data/TMS_data/raw/Jun25a/Argon_totalI_Fd1500_Fc1000.dat')
#     check_ds(fname = '/data/TMS_data/raw/Jun26a/Air_totalI.dat', startIdx=950)
#     check_ds(fname = '/data/TMS_data/raw/Jun26a/Air_I_Fd2000_Fc1000.dat', startIdx=5850)
#     check_ds(fname = '/data/TMS_data/raw/Jun26a/Air_I_Fd2000_Fc1000_close.dat', startIdx=None)
    check_ds(fname = '/data/TMS_data/raw/Jun26a/Air_I_Fd2000_close.dat', startIdx=9000)

