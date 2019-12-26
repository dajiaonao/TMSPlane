#set xrange [0:20]
#set yrange [0:400]
##set size ratio -1
#if (GPVAL_DATA_X_MAX > 100) set xrange[GPVAL_DATA_X_MAX-100:GPVAL_DATA_X_MAX]; 
set xdata time
#set timefmt x "%Y-%m-%d_%H:%M:%S"
set timefmt "%Y-%m-%d_%H:%M:%S"
if (!exists("projname")) projname='project_42/'
#if (!exists("projname")) projname='./'
#print projname
set ylabel "I [pA]"
set xlabel "Time"
#set terminal postscript eps enhanced colour dashed lw 1 "Helvetica" 14 
#set output projname.'test.eps'
#plot projname."current.dat" using 1:2 with lines
plot projname."current.dat" using 1:($2<1?$2*1e12:1/0) with lines
pause 10
reread
