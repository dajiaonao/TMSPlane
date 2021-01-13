#!/usr/bin/env python3
from filterChecker import filterChecker

fc1 = filterChecker()
#fc1.filterPars = [100,100,300,300]
#fc1.recoCfg = 'Lithium/C4_Nov24'
#fc1.recoCfg = 'Lithium/C8_Dec18a'
#fc1.recoCfg = 'Lithium/C8_Dec21'
#fc1.recoCfg = 'Lithium/C8_Dec25'
# fc1.recoCfg = 'Lithium/C8_Dec30'
# fc1.recoCfg = 'Lithium/C8_Jan06'
#fc1.recoCfg = 'Lithium/C8_Jan02'
fc1.recoCfg = 'Lithium/C8_Jan08'
#fc1.recoCfg = 'TEST2'
fc1.chan = 18
fc1.waitTime = 1000
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
#fc1.offline_check('/data/TMS_data/raw/Nov03_TMS/C7Ch0_gamma_P10_26PSI_Pulse100Hz100mV_fc1800_fd1800_Nov041809_data_1581.root')
#fc1.offline_check('/data/TMS_data/raw/Nov09_TMS/C7Ch0_alpha_P10_26PSI_Pulse100Hz1000mV_fc900_fd900_Nov091638_data_20.root')
# fc1.offline_check('/data/TMS_data/raw2/Nov09_TMS/C7Ch0_alpha_P10_26PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov091651_data_25.root')
#fc1.offline_check('/data/TMS_data/raw/Nov09_TMS/C7Ch0_alpha_P10_26PSI_Pulse100Hz1000mV_fc600_fd600_Nov091701_data_31.root')
#fc1.offline_check('/data/TMS_data/raw/Nov09_TMS/C7Ch0_alpha_P10_0PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov091600_data_0.root')
#fc1.offline_check('/data/TMS_data/raw/Nov09_TMS/C7Ch0_alpha_P10_0PSI_Pulse100Hz1000mV_fc600_fd600_Nov091616_data_14.root')
#fc1.offline_check('/data/TMS_data/raw/Nov09_TMS/C7Ch0_alpha_P10_0PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov091600_data_3.root')
#fc1.offline_check('/data/TMS_data/raw/Nov09_TMS/C7Ch0_alpha_P10_0PSI_Pulse100Hz1000mV_fc900_fd900_Nov091609_data_5.root')
#fc1.offline_check('/data/TMS_data/raw/skimmed/Nov03_TMS_S0/skimmed_C7Ch0_gamma_P10_22PSI_Pulse100Hz1000mV_fc1800_fd1800_Nov031257_data_40.root')
#fc1.offline_check('/data/TMS_data/raw/Nov11_TMS/C7Ch071115_gamma_P10_28PSI_Pulse100Hz100mV_fc1800_fd1800_Nov111534_data_8.root')
#fc1.offline_check('/data/TMS_data/raw/Nov16_TMS/C7Ch071115_alpha_P10_0PSI_Pulse100Hz500mV_fc1800_fd1800_Nov161026_data_84.root')
# fc1.offline_check('/data/TMS_data/raw/Nov20_TMS/C7_alpha_P10_30PSIdown_Pulse100Hz100mV_fc1200_fd1300_Nov201434_data_8.root')
#fc1.offline_check('/data/TMS_data/raw/Nov11_TMS/C7Ch071115_gamma_P10_28PSI_Pulse100Hz100mV_fc1800_fd1800_Nov111534_data_245.root')
#fc1.offline_check('/data/TMS_data/raw/Nov11_TMS/C7Ch071115_gamma_P10_28PSI_Pulse100Hz100mV_fc1800_fd1800_Nov111534_data_867.root')
# fc1.offline_check('/data/TMS_data/raw/Nov11_TMS/C7Ch071115_gamma_P10_28PSI_Pulse100Hz50mV_fc1800_fd1800_Nov121550_data_4365.root')
#fc1.offline_check('/data/TMS_data/raw3/Nov11_TMS_archive3/Nov11_TMS_1400_1449/C7Ch071115_gamma_P10_28PSI_Pulse100Hz50mV_fc1800_fd1800_Nov121550_data_1431.root')
#fc1.offline_check('/data/TMS_data/raw/skimmed/Nov11_TMS_S0/skimmed_C7Ch071115_gamma_P10_28PSI_Pulse100Hz100mV_fc1800_fd1800_Nov111534_data_245.root')
#fc1.offline_check('/data/TMS_data/raw/Nov16_TMS/C7Ch071115_alpha_15LongDecay_P10_0PSI_Pulse100Hz500mV_fc1800_fd1800_Nov161609_data_259.root')
#fc1.offline_check('/data/TMS_data/raw/Dec18_TMS/C8_alpha_P10Min_Pulse100Hz200mV_fc500_fd500_5Mohm_Dec181805_data_4.root')
#fc1.offline_check('/data/TMS_data/raw/Dec24_TMS/C8_alpha_pulse_200mV_Dec242033_data_0.root')
#fc1.offline_check('/data/TMS_data/raw/Dec25_TMS/C8_alpha_23591314antenna_P10Min_Pulse100Hz200mV_fd500_fc300_Dec252116_data_9.root')
# fc1.offline_check('/data/TMS_data/raw/Dec30_TMS/C8_alpha_23591314antenna_P10Min_Pulse100Hz200mV_fd900_fc1620_Dec301649_data_64.root')
# fc1.offline_check('/data/TMS_data/raw/Jan06_TMS/C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd500_fc850_2021Jan061715_data_41.root')
fc1.offline_check('/data/TMS_data/raw/Jan08_TMS/C8_alpha_23591314hignAntenna_P10Min_Pulse100Hz200mVDC0p2V_fd800_fc1360_2021Jan081639_data_45.root')
#fc1.offline_check('/data/TMS_data/raw/Dec30_TMS/C8_alpha_23591314antenna_P10Min_Pulse100Hz200mV_fd1000_fc2000_Dec301649_data_35.root')
#fc1.offline_check('/data/TMS_data/raw/Jan02_TMS/C8_alpha_23591314antenna_P10Min_Pulse100Hz200mVDC5V_fd1000_fc1000_2021Jan021643_data_5.root')
#fc1.offline_check('/data/TMS_data/raw/Dec21_TMS/C8_alpha_pulse_test_Dec211913_data_2.root')
#fc1.online_check()

