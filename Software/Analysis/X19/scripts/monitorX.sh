#!/bin/bash

# trap ctrl_c INT
# 
# function ctrl_c() {
#         echo "** Trapped CTRL-C"
#       pkill gnuplot
# }

while [ ! -s test.dat ]; do
	sleep 10
done

proj=$1
/usr/bin/gnuplot -e "projname='$proj'" show_Q_hist.gnu &
/usr/bin/gnuplot -e "projname='$proj'" show_Q_total.gnu
