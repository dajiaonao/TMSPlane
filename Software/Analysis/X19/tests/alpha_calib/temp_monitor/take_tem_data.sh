#!/usr/bin/bash
cd /home/TMSTest/PlacTests/TMSPlane/temp_tests
./c4
fname=`date +%Y%m%d_%H%M%S`
mv webcam_capture.jpg temp_data/${fname}.jpg
