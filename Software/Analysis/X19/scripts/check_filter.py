#!/usr/bin/env python3
from filterChecker import filterChecker

fc1 = filterChecker()
#fc1.filterPars = [100,100,300,300]
fc1.recoCfg = 'Lithium/C7_shortA'
fc1.chan = 16
# fc1.offline_check('/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_100mV_data_0.root')
# fc1.offline_check('/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_40mV_data_0.root')
# fc1.offline_check('/home/TMSTest/PlacTests/TMSPlane/Software/Control/src/data/fpgaLin/Oct07_TMS/test1_data_30.root')
#fc1.offline_check('/data/TMS_data/raw/Oct08_TMS/test_DC50_PP1500_data_0.root')
fc1.offline_check('/data/TMS_data/raw/Oct19_TMS/C7_Argon_Pulse100Hz100mVpp_data_9.root')
#fc1.online_check()

