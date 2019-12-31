set term x11 1 noraise
#set xrange [0:20]
#set xrange [*:*]
#set yrange [0:400]
##set size ratio -1
#if (GPVAL_DATA_X_MAX > 100) set xrange[GPVAL_DATA_X_MAX-100:GPVAL_DATA_X_MAX]; 
set xdata time
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
#show grid
#set timefmt x "%Y-%m-%d_%H:%M:%S"
set timefmt "%Y-%m-%d_%H:%M:%S"
if (!exists("projname")) projname='project_62/'
#if (!exists("projname")) projname='./'
#print projname
set ylabel "I [pA]"
set xlabel "Time"
#set terminal postscript eps enhanced colour dashed lw 1 "Helvetica" 14 
#set output projname.'test.eps'
#plot projname."current.dat" using 1:2 with lines

#set y2tics -150, 10
#set ytics nomirror
#plot projname."current.dat" using 1:($2<1?$2*1e12:1/0) with lines axis x1y1, projname."current.dat" using 1:4 axis x1y2
plot projname."current.dat" using 1:($2<1?$2*1e12:1/0)
#plot projname."current.dat" using 1:4

#set y2tics -100, 10
#set ytics nomirror
#plot sin(1/x) axis x1y1,100*cos(x) axis x1y2

pause 10
reread
