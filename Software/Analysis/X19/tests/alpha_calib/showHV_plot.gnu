#set terminal png size 400,300; set output 'xyz.png';
#plot 'HV1000_current_0.dat' using 3:2\
#, 'HV1000_current_1.dat' using 3:2\
#, 'HV1000_current_2.dat' using 3:2\
#,'HV1000_current_3.dat' using 3:2
#
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
show grid
set yrange [-2e-11:1e-11]
list1 = system('ls -1B *.dat')
#plot for [file1 in list1] file1 using 3:($2*50000000) t file1
plot for [file1 in list1] file1 using 3:2 t file1
#plot for [i=0:10] 'HV1000_current_'.i.'.dat' using 3:2 title 'Data '.i

pause 10
reread
