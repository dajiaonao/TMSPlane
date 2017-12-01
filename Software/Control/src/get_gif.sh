#!/bin/bash

figs=`ls ls figs_2017Nov28/png/plot_5_*.png|sort -t_ -k4 -n|xargs`
echo $figs

convert -loop 0 -delay 10 ${figs} out_P5_Nov28.gif

