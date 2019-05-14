set xdata time
set timefmt x "%s"
plot "test.dat" using 1:3 with lines
pause 10
reread
