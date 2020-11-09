#!/usr/bin/env python3
from filterChecker import filterChecker

fc1 = filterChecker()
#fc1.filterPars = [100,100,300,300]
fc1.recoCfg = 'Lithium/C7_shortA'
#fc1.recoCfg = 'TEST2'
fc1.chan = 0
# fc1.offline_check('/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_100mV_data_0.root')
# fc1.offline_check('/data/Samples/TMSPlane/fpgaLin/raw/Nov04c/Nov04c_40mV_data_0.root')
# fc1.offline_check('/home/TMSTest/PlacTests/TMSPlane/Software/Control/src/data/fpgaLin/Oct07_TMS/test1_data_30.root')
#fc1.offline_check('/data/TMS_data/raw/Oct08_TMS/test_DC50_PP1500_data_0.root')
# fc1.offline_check('/data/TMS_data/raw/Oct20_TMS/C7_addedsource_P10to30PSI_Pulse100Hz100mVpp_driftV3p8kV_data_21.root')
# fc1.offline_check('/data/TMS_data/raw/Oct25_TMS/C7Ch5_gamma_P10_30PSI_Pulse100Hz100mVpp_driftV3p8kV_Oct251305_data_94.root')
#fc1.offline_check('/data/TMS_data/raw/Oct26_TMS/C7Ch5_gamma_ArFlow_10PSI_Pulse100Hz100mVpp_fc1500_fd1500_Oct261941_data_2.root')
#fc1.offline_check('/data/TMS_data/raw/Oct27_TMS/C7Ch5_gamma_Ar_12PSI_Pulse100Hz300mVpp_fc1500_fd1500_Oct271304_data_8.root')
#fc1.offline_check('/data/TMS_data/raw/Oct27_TMS/C7Ch5_alpha_Ar_12PSI_Pulse100Hz100mVpp_fc1500_fd1500_Oct271257_data_3.root')
#fc1.offline_check('/data/TMS_data/raw/Oct20_TMS/C7_addedsource_Argon30PSI_Pulse100Hz100mVpp_driftV3p8kV_data_5.root')
#fc1.offline_check('/data/TMS_data/raw/Oct25_TMS/C7Ch5_gamma_P10_30PSI_Pulse100Hz100mVpp_driftV3p8kV_Oct251305_data_159.root')
# fc1.offline_check('/data/TMS_data/raw/Nov02_TMS/C7Ch0_gamma_Ar_20PSI_Pulse100Hz100mV_fc1500_fd1500_Nov021221_data_12.root')
#fc1.offline_check('/data/TMS_data/raw/Nov02_TMS/C7Ch0_alpha_P10_to20PSI_Pulse100Hz1000mV_fc1500_fd1500_Nov021601_data_180.root')
#fc1.offline_check('/data/TMS_data/raw/Nov02_TMS/C7Ch0_gamma_P10_20PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov021651_data_227.root')
#fc1.offline_check('/data/TMS_data/raw/Nov02_TMS/C7Ch0_gamma_P10_20PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov021651_data_317.root')
#fc1.offline_check('/data/TMS_data/raw/Nov02_TMS/C7Ch0_alpha_Ar_20PSI_Pulse100Hz100mV_fc1500_fd1500_Nov021540_data_163.root')
#fc1.offline_check('/data/TMS_data/raw/Nov02_TMS/C7Ch0_alpha_Ar_to1atm_Pulse100Hz100mV_fc1500_fd1500_Nov021545_data_168.root')
#fc1.offline_check('/data/TMS_data/raw/Nov03_TMS/C7Ch0_gamma_P10_22PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov031257_data_29.root')
fc1.offline_check('/data/TMS_data/raw/Nov03_TMS/C7Ch0_gamma_P10_26PSI_Pulse100Hz100mV_fc1800_fd1800_Nov041809_data_1581.root')
#fc1.online_check()

