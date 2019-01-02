#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from PyDE import *
import threading
from Queue import Queue
import time

def test1():
    print("testing")


class tuner(threading.Thread):
    def __init__(self, idx):
        threading.Thread.__init__(self)
        self.idx = idx
        self.rx_qs = None
        self.tx_qs = None
        self.atBounds = [(-10,10),(-10,10),(-10,10),(-10,10),(-10,10),(-10,10)] 
        self.atMaxIters = 100

    def run(self):
        de = DE(self.auto_tune_fun, self.atBounds, maxiters=self.atMaxIters)
        ret = de.solve()
        self.tx_qs[self.idx] = None
        self.rx_qs[self.idx] = None
        print("Done {0:d}\n".format(self.idx))
 
        time.sleep(self.idx*1+1)
        print('-'*10, self.idx)
        print(ret)
       
    def auto_tune_fun1(self, x):
        return sum([(a-self.idx)*(a-self.idx) for a in x])

    def auto_tune_fun(self, x):
        ### put x to the queue
#         print(self.idx, 'sending', x)
        self.tx_qs[self.idx].put(x)
#         print('+++sent:['+','.join([str(a) for a in x]))

        ### wait for the returned value
        gg = self.rx_qs[self.idx].get()
#         print('+++get:{0:g}'.format(gg))
        return gg

class Train(threading.Thread):
    def __init__(self, nChan=5):
        threading.Thread.__init__(self)
        self.tx_qs = None
        self.rx_qs = None
        self.pars = [None]*nChan
        self.meas = [None]*nChan
        self.on = True
        self.mask = [0]*nChan
    def run(self):
        while self.on:
            cnt = 0
            cnt1 = 0
            for i,q in enumerate(self.rx_qs):
                if q is None: continue
                cnt += 1
#                 x = q.get()
#                 self.pars[i] = x

                if not q.empty():
                    cnt1 += 1
                    x = q.get()
                    self.mask[i] = 1
#                     print('--- {0:d} get'.format(i)+' ['+','.join([str(a) for a in x])+']')
                    self.pars[i] = x

            if cnt == 0: self.on = False
            if cnt1 == 0: continue

            #### calculation
            for i,p in enumerate(self.pars):
                if p is not None:
                    self.meas[i] = sum([(x-i+5)*(x-i+5) for x in p])
#                     print('--- {0:d}--->{1:g}'.format(i,self.meas[i]))

            ### return
            for i,t in enumerate(self.tx_qs):
                if self.mask[i] == 1:
                    t.put(self.meas[i])
                    self.mask[i] = 0
#                     print("--- {0:d} {1:g}".format(i, self.meas[i]))
        print('Stopping the train.....')


class TestClass:
    def __init__(self, nAdcCh=20):
        self.x = None
        self.tx_qs = [None]*nAdcCh
        self.rx_qs = [None]*nAdcCh
        self.nAdcCh = nAdcCh

    def test_tune(self):
        tr1 = Train(self.nAdcCh)
        tr1.tx_qs = self.rx_qs
        tr1.rx_qs = self.tx_qs
        tr1.on = True

        for i in range(self.nAdcCh):
            self.tx_qs[i] = Queue()
            self.rx_qs[i] = Queue()
            th1 = tuner(i)
            th1.tx_qs = self.tx_qs
            th1.rx_qs = self.rx_qs            
            th1.start()
#         time.sleep(2)
        tr1.start()


def test1():
    tc1 = TestClass(8)
    tc1.test_tune()

if __name__ == '__main__':
    test1()
