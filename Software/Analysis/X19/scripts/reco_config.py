#!/usr/bin/env python3
from check_decay import FilterConfig
from math import sqrt

def apply_config(sp1, config_code='default'):

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

#         ### filter configuration
#         sp1.fltParam.clear()
#         flt = [50, 100, 300, 1] # dp01a
#         for x in flt: sp1.fltParam.push_back(x)

        fc1 = FilterConfig('C1_filter_config.json')
        fc1.load()

        sp1.fltParam.clear()
        flt = [50, 100, 300, -1./fc1.data[0][2]] # dp01a
        for x in flt: sp1.fltParam.push_back(x)

        scale = 1
        P = 1./0.006/2500/1024*5000000*scale;
        for x in [30, 50, 200, P]: sp1.fltParam.push_back(x)
        for i in range(sp1.nAdcCh):
            print -sqrt(2)/fc1.data[i][2]
            sp1.CF_decayC[i] = -sqrt(2)/fc1.data[i][2]

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
#             sp1.CF_decayC[i] = P

        ### we are done
        return "He4/a" ### anything after slash is a development tag, frozen configurations does not have a slash
    elif config_code == 'Lithium':
        ### search window
        sp1.CF_uSize = 600
        sp1.CF_dSize = 1100

        ## threshold
        thre = [0.001]*sp1.nAdcCh
        thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
#         fltParam = [100,200,900,500]
#         fltParam = [100,200,2000,-1]
        fltParam = [100,800,1200,4000]
        fltParam = [100,500,1500,3500]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        scale = 1
        P = fltParam[-1];

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
            sp1.CF_decayC[i] = P

        ### we are done
        return "Li7/a" ### anything after slash is a development tag, frozen configurations does not have a slash
    elif config_code == 'Lithium/b':
        ### search window
        sp1.CF_uSize = 600
        sp1.CF_dSize = 1100

        ## threshold
        thre = [0.001]*sp1.nAdcCh
        thre[5] = 0.002
        thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
        fltParam = [100,300,400,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        scale = 1
        P = 3000;

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
            sp1.CF_decayC[i] = P

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        sp1.CF_decayC[0] = -1
        sp1.CF_decayC[1] = 3000
        sp1.CF_decayC[2] = 5
        sp1.CF_decayC[3] = -1
        sp1.CF_decayC[4] = 900
        sp1.CF_decayC[5] = 10
        sp1.CF_decayC[6] = -1
        sp1.CF_decayC[7] = 5000
        sp1.CF_decayC[8] = -1
        sp1.CF_decayC[9] = -1
        sp1.CF_decayC[10] = -1
        sp1.CF_decayC[11] = 5000
        sp1.CF_decayC[12] = 4000
        sp1.CF_decayC[13] = 4000
        sp1.CF_decayC[14] = -1
        sp1.CF_decayC[15] = 3000
        sp1.CF_decayC[16] = -1
        sp1.CF_decayC[17] = 600
        sp1.CF_decayC[18] = 4000
        
        ### we are done
        return "Li7/b" ### anything after slash is a development tag, frozen configurations does not have a slash
    elif config_code == 'Lithium/c':
        ## chip 7
        ### search window
        sp1.CF_uSize = -100
        sp1.CF_dSize = 100

        sp1.CF_trig_ch = 3
        ## threshold
        thre = [0.001]*sp1.nAdcCh
        thre[4] = 0.002
#         thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
#         fltParam = [100,300,350,80]
        fltParam = [100,100,350,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        sp1.CF_decayC[0] = 450
        sp1.CF_decayC[1] = 6000
        sp1.CF_decayC[2] = 6000
        sp1.CF_decayC[3] = 410
        sp1.CF_decayC[4] = 2000
        sp1.CF_decayC[5] = 410
        sp1.CF_decayC[6] = 2300
        sp1.CF_decayC[7] = 2200
        sp1.CF_decayC[8] = 2200
        sp1.CF_decayC[9] = 2200
        sp1.CF_decayC[10] = 3900
        sp1.CF_decayC[11] = 2000
        sp1.CF_decayC[12] = 1800
        sp1.CF_decayC[13] = 1400
        sp1.CF_decayC[14] = 1400
        sp1.CF_decayC[15] = 2000
        sp1.CF_decayC[16] = 5
        sp1.CF_decayC[17] = 1200
        sp1.CF_decayC[18] = 3200
        sp1.CF_decayC[19] = -1

        for i in range(sp1.nAdcCh):
            sp1.CF_fltParams[i].setV(100, 100,300,sp1.CF_decayC[i])
        sp1.CF_fltParams[16].setV(100,10,210,sp1.CF_decayC[16])

        ### we are done
        return "Li7/c" ### anything after slash is a development tag, frozen configurations does not have a slash
    elif config_code == 'Lithium/d':
        ## chip 7, for Dec17a data analysis
        ### search window
        sp1.CF_uSize = -100
        sp1.CF_dSize = 100

        sp1.CF_trig_ch = 16
        ## threshold
        thre = [0.00001]*sp1.nAdcCh
        thre[4] = 0.002
        thre[5] = 0.005
#         thre[19] = 0.02

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
#         fltParam = [100,300,350,80]
        fltParam = [100,100,350,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        sp1.CF_decayC[0] = 450
        sp1.CF_decayC[1] = 6000
        sp1.CF_decayC[2] = 6000
        sp1.CF_decayC[3] = 410
        sp1.CF_decayC[4] = 2000
#         sp1.CF_decayC[5] = 410
        sp1.CF_decayC[5] = -1
        sp1.CF_decayC[6] = 2300
        sp1.CF_decayC[7] = 2200
        sp1.CF_decayC[8] = 2200
        sp1.CF_decayC[9] = 2200
        sp1.CF_decayC[10] = 3900
        sp1.CF_decayC[11] = 2000
        sp1.CF_decayC[12] = 1800
        sp1.CF_decayC[13] = 1400
        sp1.CF_decayC[14] = 1400
        sp1.CF_decayC[15] = 2000
        sp1.CF_decayC[16] = 5
        sp1.CF_decayC[17] = 1200
        sp1.CF_decayC[18] = 3200
        sp1.CF_decayC[19] = -1

        for i in range(sp1.nAdcCh):
            sp1.CF_fltParams[i].setV(100, 100,300,sp1.CF_decayC[i])
        sp1.CF_fltParams[16].setV(100,10,210,sp1.CF_decayC[16])

        ### we are done
        return "Li7/d" ### anything after slash is a development tag, frozen configurations does not have a slash
    elif config_code == 'Lithium/C7_shortA':
        ## chip 7, for Dec17a data analysis
        ### search window
        sp1.CF_uSize = -100
        sp1.CF_dSize = 100

        #sp1.CF_trig_ch = 0 #5 # 7 18 0
        sp1.CF_trig_ch = 7 # Nov11 0,7,11,15
        ## threshold
#         thre = [0.00001]*sp1.nAdcCh
        thre = [0.002]*sp1.nAdcCh

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
#         fltParam = [100,300,350,80]
        fltParam = [100,100,350,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        #sp1.CF_decayC[0] = 5000
        #sp1.CF_decayC[0] = 500 # Nov03?
        #sp1.CF_decayC[0] = 320 # Nov09_TMS 20-24 25-29
        #sp1.CF_decayC[0] = 380 # Nov09_TMS 30-34
        #sp1.CF_decayC[0] = 430 # Nov09_TMS 0-4 slow drifting from 430 to 280... !!
        #sp1.CF_decayC[0] = 280 # Nov09_TMS 3-4 5-9
        #sp1.CF_decayC[0] = 1500 # Nov09_TMS 10-14
        #sp1.CF_decayC[0] = 1600 # Nov11 <269
        #sp1.CF_decayC[0] = 3000 # Nov11 
        sp1.CF_decayC[0] = 500 # Nov16
        sp1.CF_decayC[1] = 6000
        sp1.CF_decayC[2] = 6000
        sp1.CF_decayC[3] = 410
        sp1.CF_decayC[4] = 2000
        sp1.CF_decayC[5] = 450 # 
#         sp1.CF_decayC[5] = 20 # 
        sp1.CF_decayC[6] = 2300
        #sp1.CF_decayC[7] = 150
        #sp1.CF_decayC[7] = 1500 #Nov11
        sp1.CF_decayC[7] = 6000 #Nov16
        sp1.CF_decayC[8] = 2200
        sp1.CF_decayC[9] = 2200
        sp1.CF_decayC[10] = 3900
        #sp1.CF_decayC[11] = 2000
        #sp1.CF_decayC[11] = 1800 #Nov11
        sp1.CF_decayC[11] = 5000 #Nov16
        sp1.CF_decayC[12] = 1800
        sp1.CF_decayC[13] = 1400
        sp1.CF_decayC[14] = 1400
        #sp1.CF_decayC[15] = 2000
        #sp1.CF_decayC[15] = 1000 #Nov11
        sp1.CF_decayC[15] = 700 #Nov16
        sp1.CF_decayC[16] = 400
        sp1.CF_decayC[17] = 1200
        sp1.CF_decayC[18] = 250
        sp1.CF_decayC[19] = -1

        for i in range(sp1.nAdcCh):
            #sp1.CF_fltParams[i].setV(100, 100,300,500)
            sp1.CF_fltParams[i].setV(50, 200,400,sp1.CF_decayC[i]) # Oct22 processing
            #sp1.CF_fltParams[i].setV(, 100,200,50)
            #sp1.CF_fltParams[i].setV(50, 200,250,sp1.CF_decayC[i])

        ### we are done
        return "Li7/C7_shortA" ### anything after slash is a development tag, frozen configurations does not have a slash
    elif config_code == 'Lithium/C7_Nov11Gamma':
        ## chip 7, for Nov11 data analysis
        ### search window
        sp1.CF_uSize = -100
        sp1.CF_dSize = 100

        #sp1.CF_trig_ch = 0 #5 # 7 18 0
        sp1.CF_trig_ch = 7 # Nov11 0,7,11,15
        ## threshold
#         thre = [0.0015]*sp1.nAdcCh
        thre = [0.0008]*sp1.nAdcCh

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
        fltParam = [100,100,120,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
        sp1.CF_chan_en[1] = 0
        sp1.CF_chan_en[19] = 0

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        sp1.CF_decayC[0] = 1887
        sp1.CF_decayC[1] = 6000
        sp1.CF_decayC[2] = 6000
        sp1.CF_decayC[3] = 410
        sp1.CF_decayC[4] = 2000
        sp1.CF_decayC[5] = 450 # 
        sp1.CF_decayC[6] = 2300
        sp1.CF_decayC[7] = 1316.49
        sp1.CF_decayC[8] = 2200
        sp1.CF_decayC[9] = 2200
        sp1.CF_decayC[10] = 3900
        sp1.CF_decayC[11] = 1460.08
        sp1.CF_decayC[12] = 1800
        sp1.CF_decayC[13] = 1846.62
        sp1.CF_decayC[14] = 292.6
        sp1.CF_decayC[15] = 991.991
        sp1.CF_decayC[16] = 400
        sp1.CF_decayC[17] = 1200
        sp1.CF_decayC[18] = 250
        sp1.CF_decayC[19] = -1

        for i in range(sp1.nAdcCh):
            sp1.CF_fltParams[i].setV(50, 100,120,sp1.CF_decayC[i]) # Oct22 processing

        ### we are done
        return "Li7/C7_Nov11Gamma" ### anything after slash is a development tag, frozen configurations does not have a slash
  
    elif config_code == 'Lithium/C4_Nov24':
        ## chip 7, for Nov11 data analysis
        ### search window
        sp1.CF_uSize = -100
        sp1.CF_dSize = 100

        #sp1.CF_trig_ch = 0 #5 # 7 18 0
        sp1.CF_trig_ch = 0 # Nov11 0,7,11,15
        ## threshold
#         thre = [0.0015]*sp1.nAdcCh
        thre = [0.0015]*sp1.nAdcCh

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
        fltParam = [100,100,120,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
        sp1.CF_chan_en[1] = 0
        sp1.CF_chan_en[19] = 0

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        sp1.CF_decayC[0] = 1887
        sp1.CF_decayC[1] = 500
        sp1.CF_decayC[2] = 450
        sp1.CF_decayC[3] = 2000
        sp1.CF_decayC[4] = 2000
        sp1.CF_decayC[5] = 1000 
        sp1.CF_decayC[6] = 2300
        sp1.CF_decayC[7] = 3000
        sp1.CF_decayC[8] = 2200
        sp1.CF_decayC[9] = 2200
        sp1.CF_decayC[10] = 1000
        sp1.CF_decayC[11] = 1460.08
        sp1.CF_decayC[12] = 1800
        sp1.CF_decayC[13] = 6000
        sp1.CF_decayC[14] = 600
        sp1.CF_decayC[15] = 2000
        sp1.CF_decayC[16] = 450
        sp1.CF_decayC[17] = 1200
        sp1.CF_decayC[18] = 700
        sp1.CF_decayC[19] = -1

        for i in range(sp1.nAdcCh):
            sp1.CF_fltParams[i].setV(50, 100,120,sp1.CF_decayC[i]) # Oct22 processing

        ### we are done
        return "Li7/C7_Nov20" ### anything after slash is a development tag, frozen configurations does not have a slash

    elif config_code == 'Lithium/C7_Nov20':
        ## chip 7, for Nov11 data analysis
        ### search window
        sp1.CF_uSize = -100
        sp1.CF_dSize = 100

        #sp1.CF_trig_ch = 0 #5 # 7 18 0
        sp1.CF_trig_ch = 0 # Nov11 0,7,11,15
        ## threshold
#         thre = [0.0015]*sp1.nAdcCh
        thre = [0.0015]*sp1.nAdcCh

        sp1.ch_thre.clear()
        for x in thre: sp1.ch_thre.push_back(x)

        ### filter configuration
        fltParam = [100,100,120,80]
        sp1.fltParam.clear()
        for p in fltParam: sp1.fltParam.push_back(p) ## decay constant 500, means decay as e^{-i/500}

        ## channelwise configuration
        sp1.CF_chan_en.clear()
        sp1.IO_mAvg.clear()
        for i in range(sp1.nAdcCh):
            sp1.CF_chan_en.push_back(1)
            sp1.IO_mAvg.push_back(0.)
        sp1.CF_chan_en[1] = 0
        sp1.CF_chan_en[19] = 0

        ## from /media/dzhang/dzhang/tms_data/Nov13b/Nov13b_HV0p5b_data_0.root.1.1
        sp1.CF_decayC[0] = 1887
        sp1.CF_decayC[1] = 500
        sp1.CF_decayC[2] = 450
        sp1.CF_decayC[3] = 2000
        sp1.CF_decayC[4] = 2000
        sp1.CF_decayC[5] = 1000 
        sp1.CF_decayC[6] = 2300
        sp1.CF_decayC[7] = 3000
        sp1.CF_decayC[8] = 2200
        sp1.CF_decayC[9] = 2200
        sp1.CF_decayC[10] = 1000
        sp1.CF_decayC[11] = 1460.08
        sp1.CF_decayC[12] = 1800
        sp1.CF_decayC[13] = 6000
        sp1.CF_decayC[14] = 600
        sp1.CF_decayC[15] = 2000
        sp1.CF_decayC[16] = 450
        sp1.CF_decayC[17] = 1200
        sp1.CF_decayC[18] = 700
        sp1.CF_decayC[19] = -1

        for i in range(sp1.nAdcCh):
            sp1.CF_fltParams[i].setV(50, 100,120,sp1.CF_decayC[i]) # Oct22 processing

        ### we are done
        return "Li7/C7_Nov20" ### anything after slash is a development tag, frozen configurations does not have a slash

    elif config_code == 'default':
        apply_config('Lithium/c')

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
    elif config_code == 'TEST2':
        print(f"Using configuration {config_code}")
        ## enable channels
        sp1.ch_thre.clear()
        sp1.CF_chan_en.clear()
        for i in range(20):
            sp1.CF_chan_en.push_back(1)
            sp1.ch_thre.push_back(0.0001)

        sp1.fltParam.clear()
        flt = [50, 550, 1000, -1] # dp01a
        for x in flt: sp1.fltParam.push_back(x)

#         sp1.CF_decayC[5] = -1;
        sp1.CF_fltParams[5].setV(50, 250,500,450)


        return 'TEST2a'


    return 0
