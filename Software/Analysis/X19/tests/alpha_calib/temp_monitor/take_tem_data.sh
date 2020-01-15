#!/usr/bin/bash
##############3
# To add this as cron job, run `crontab -e` and add text in quot "*/5 * * * * /home/TMSTest/PlacTests/TMSPlane/temp_tests/take_tem_data.sh"
#

cd /home/TMSTest/PlacTests/TMSPlane/temp_tests
./c4
fname=`date +%Y%m%d_%H%M%S`
mv webcam_capture.jpg temp_data/${fname}.jpg
