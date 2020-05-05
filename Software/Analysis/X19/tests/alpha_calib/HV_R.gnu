set xlabel "HV [V]"
set ylabel "I [A]"
dir1="/data/Samples/TMSPlane/HVCheck/"
plot dir1."R_iseg.dat" using (-1.*$5):(-1.*$2), dir1."R_picometer.dat" using 5:(-1.*$2) with points ls 3, dir1."R_Dongwen.dat" using (-1.*$5):(-1.*$2) with points ls 4

pause -1
