set xlabel "HV [V]"
set ylabel "I [A]"
dir1="/data/Samples/TMSPlane/HVCheck/"
#plot dir1."R_iseg.dat" using (-1.*$5):(-1.*$2), dir1."R_picometer.dat" using 5:(-1.*$2) with points ls 3, dir1."R_Dongwen.dat" using (-1.*$5):(-1.*$2) with points ls 4
#set xrange [-2600:0]
set xrange [-2600:]
#plot dir1."R1_Iseg8.dat" using (-1.*$5):(-1.*$2)
#plot dir1."R1_Iseg8.dat" using 5:(-1.*$2)
plot dir1."R1_Iseg8.dat" using (-1.*$5):(-1.*$2)
#, dir1."R2_pico1.dat" using 5:(-1.*$2) with points ls 3

pause -1
