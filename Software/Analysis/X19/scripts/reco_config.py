#!/usr/bin/env python
from check_decay import FilterConfig
from math import sqrt

def apply_config(sp1, config_code):

    ## Put the common ones here
    sp1.nSamples = 16384 
    sp1.nAdcCh = 20





    ## now the variations
    if config_code == 'Hydrogen':
        ### search window
        sp1.CF_uSize = 600
        sp1.CF_dSize = 1100

        ## threshold
        thre = [0.005]*sp1.nAdcCh
#         thre[2] = 0.0008
#         thre[4] = 0.001
#         thre[6] = 0.001
#         thre[7] = 0.001
#         thre[10] = 0.001
#         thre[11] = 0.0007
#         thre[14] = 0.0007
#         thre[17] = 0.001
        thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ## enable channels
        sp1.CF_chan_en.clear()
        for i in range(20): sp1.CF_chan_en.push_back(1)

        ### filter configuration
        fc1 = FilterConfig('filter_config.json')
        fc1.load()
#         print(fc1.data[0])

        sp1.fltParam.clear()
#         flt = [50, 100, 500, -1./fc1.data[0][2]] # dp01a
        flt = [50, 100, 300, -1./fc1.data[0][2]] # dp01a
        for x in flt: sp1.fltParam.push_back(x)

        for i in range(sp1.nAdcCh): sp1.CF_decayC[i] = -sqrt(2)/fc1.data[i][2]
        scale = 10
        sp1.CF_decayC[19] = 1./0.006/2500/1024*5000000*scale; ### 0.5 ms
#         print(sp1.CF_decayC)

        return "H1/a" ### anything after slash is a development tag, frozen configurations does not have a slash

    if config_code == 'Hydrogen/c3':
        ### search window
        sp1.CF_uSize = 600
        sp1.CF_dSize = 1100

        ## threshold
        thre = [0.005]*sp1.nAdcCh
        thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ## enable channels
        sp1.CF_chan_en.clear()
        for i in range(20): sp1.CF_chan_en.push_back(1)

        ### filter configuration
        fc1 = FilterConfig('C3_filter_config.json')
        fc1.load()

        sp1.fltParam.clear()
        flt = [50, 100, 300, -1./fc1.data[0][2]] # dp01a
        for x in flt: sp1.fltParam.push_back(x)

        for i in range(sp1.nAdcCh): sp1.CF_decayC[i] = -sqrt(2)/fc1.data[i][2]
        scale = 10
        sp1.CF_decayC[19] = 1./0.006/2500/1024*5000000*scale; ### 0.5 ms

        return "H1/b" ### anything after slash is a development tag, frozen configurations does not have a slash

    elif config_code == 'Helium':
        ### search window
        sp1.CF_uSize = 600
        sp1.CF_dSize = 1100

        ## threshold
        thre = [0.005]*sp1.nAdcCh
        thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)


        ### filter configuration
        sp1.fltParam.clear()

        scale = 1
        P = 1./0.006/2500/1024*5000000*scale;
        for x in [30, 50, 200, P]: sp1.fltParam.push_back(x)

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
            sp1.CF_decayC[i] = P

        ### we are done
        return "He4/a" ### anything after slash is a development tag, frozen configurations does not have a slash

    elif config_code == 'TEST1':
        ## enable channels
        sp1.ch_thre.clear()
        sp1.CF_chan_en.clear()
        for i in range(20):
            sp1.CF_chan_en.push_back(1)
            sp1.ch_thre.push_back(0.002)

        sp1.fltParam.clear()
        flt = [50, 100, 300, 1./0.001348] # dp01a
        for x in flt: sp1.fltParam.push_back(x)

        sp1.CF_decayC[10] = sqrt(2)/0.001348;

        return 'TEST1a'

    return 0
