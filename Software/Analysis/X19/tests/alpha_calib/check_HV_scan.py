#!/usr/bin/env python3
from dateutil.parser import parse
from math import sqrt
from datetime import timedelta
from ROOT import TGraphErrors

### measured value class
class MV:
    def __init__(self):
        self.total = 0.
        self.total2 = 0.
        self.n = 0
    def add(self,x):
        self.total += x
        self.total2 += x*x
        self.n += 1
    def get(self):
        if self.n == 0: return None, None
        mean = self.total/self.n
        return mean, sqrt(self.total2 - self.n*mean*mean)/self.n

def getAverage():
    pName = 'project_41'

    dT = timedelta(seconds=90)
#     dat1 = parse('2019-12-25_18:36:40'.replace('_',' '))
#     print(dat1, type(dat1))
#     return

    date0 = '2019-12-25'
    vList = []
#     vList.append((1000,'18:50','19:39'))
#     vList.append((1000,'19:15','19:39'))
    vList.append((1000,'19:32','19:39'))
    vList.append((0   ,'19:39','19:55'))
    vList.append((1001,'19:55','20:08'))
    vList.append((2000,'20:08','20:19'))
    vList.append((350 ,'20:19','20:30'))
    vList.append((750 ,'20:30','20:41'))
    vList.append((100 ,'20:41','20:53'))
    vList.append((900 ,'20:53','21:07'))
    vList.append((200 ,'21:07','21:29'))
    vList.append((500 ,'21:29','21:45'))
    vList.append((1500,'21:45','23:39'))

    vPList = []
    for v in vList: vPList.append((v[0],parse(date0+' '+v[1])+dT,parse(date0+' '+v[2])-dT))
    for v in vPList: print(v[0],v[1],v[2])
#     return

    IList = {}
    for v in vList: IList[v[0]] = MV()

    lines = None
    with open(pName+'/current.dat','r') as fin1:
        lines = fin1.readlines()

    scale = 1e12
    for line in lines:
        fs = line.rstrip().split(' ')
        t1 = parse(fs[0].replace('_',' '))
        
        for v in vPList:
            if t1>v[1] and t1<v[2]:
                IList[v[0]].add(float(fs[1])*scale)

#         return
    vx2 = []
    baseV = 0.
    for v in IList:
        x = IList[v].get()
        vx2.append((v,x[0],x[1]))
        if v == 0: baseV = x[0]
        print(v, x[0],x[1])
#         print(v, IList[v].get())

    baseV = 0.
    gr = TGraphErrors()
    for v in sorted(vx2,key=lambda x:x[0]):
        n1 = gr.GetN()
        gr.SetPoint(n1, v[0], v[1]-baseV)
        gr.SetPointError(n1, 0, v[2])

    gr.Draw()
    a = input("waiting...")
#         self.Times = [(parse(date+x[0]),parse(date+x[1])) for x in times]

def test():
    getAverage()

if __name__ == '__main__':
    test()
