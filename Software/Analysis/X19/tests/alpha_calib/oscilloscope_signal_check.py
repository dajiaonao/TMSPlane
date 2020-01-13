#!/usr/bin/env python3
import matplotlib.pyplot as plt
# from scipy import signal
from scipy.signal import find_peaks

signIt = lambda t: t if t<127 else t-256

def test():
    with open('tek0002CH2.isf','rb') as f1:
        b0 = f1.read(1024)
        b1i = b0.find(b':CURVE')
        b = b0[:b1i]
        c = b.split(b';')

        b2 = b0[b1i:]
        c += [b2]

        pars = {}
        for v in c:
            a = v.find(b" ")
#             print(v,a)
            pars[v[:a]] = v[a+1:]
#         print(pars)        

        wav = pars[b':CURVE'][10:]
        wav += f1.read()
        wav1 = [signIt(int(x)) for x in wav[::2]]
#         wav1 = [from_bytes(x,'big',signed=True) for x in wav[::2]]
#         wav1 = [ax(j) for j in wav[::2]]
        print(len(wav1), wav1[:10])
#         return

        wav2 = wav1[:500000]
#         peaks = signal.find_peaks(wav2) 
#         peaks, _ = find_peaks(wav2, height=10, distance=150) 
        peaks, _ = find_peaks(wav2, height=8, width=150, distance=850) 
#         print(peaks)
        plt.plot(wav2)
        wav3 = [wav2[ix] for ix in peaks]
        plt.plot(peaks, wav3, "x")
        plt.show()

        peaks, _ = find_peaks(wav1, height=8, width=150, distance=850)
        print(len(peaks))

        x2 = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
        fig, ax = plt.subplots()

        num_bins = 50
        # the histogram of the data
        n, bins, patches = ax.hist(x2, num_bins)
        plt.show()

#         n, bins, patches = ax.hist([wav1[ix] for ix in peaks], num_bins)
#         plt.show()



if __name__ == '__main__':
    test()
