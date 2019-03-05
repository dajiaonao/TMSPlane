#!/usr/bin/env python
import os, json
from TMS1mmX19Config import TMS1mmReg
import matplotlib.pyplot as plt
from matplotlib import cm
# import colormaps as cmaps

def read_config_file(configFName='config.json'):
    voltsNames = ['VBIASN', 'VBIASP', 'VCASN', 'VCASP', 'VDIS', 'VREF']
    nF = len(voltsNames)
    tr1 = TMS1mmReg()

    sensorV = []
    if os.path.isfile(configFName):
        with open(configFName, 'r') as fp:
            config = json.load(fp)
            for i in range(len(config)):
                sensorV.append([0]*nF)
                for j in range(nF):
                    sensorV[i][j] = tr1.dac_code2volt(config[repr(i)][voltsNames[j]])
    return sensorV

def showPars():
    pars1 = read_config_file()
    y = range(len(pars1[0]))
#     plt.plot([a[0] for a in pars1])
#     plt.register_cmap(name='viridis', cmap=cmaps.viridis)
#     viridis = cm.get_cmap('viridis', 20)
    viridis = plt.get_cmap('viridis', 20)
    i = 0
    for xx in pars1:
#         plt.plot(xx, y, 'o')
#         plt.plot(xx, y, label='chip #{0:d}'.format(i), color=(0.5,0.5,(i+1)/20.))
        plt.plot(xx, y, label='chip #{0:d}'.format(i), color=viridis(i/20.))
        i+=1
    plt.ylabel('some numbers')
    plt.legend()


#     legend = plt.legend(loc='upper center', shadow=True, fontsize='x-large')
# 
#     # Put a nicer background color on the legend.
#     legend.get_frame().set_facecolor('C0')

    plt.show()

def checkPars(fname,ch):
    pars1 = read_config_file(fname)
    print pars1[ch]

if __name__ == '__main__':
#     showPars()
#     checkPars('current_best_config.json',17)
    checkPars('Mar01Td_best_config.json',17)
    checkPars('config.json',17)
