binwidth=0.01
bin(x,width)=width*floor(x/width)
#plot 'test.dat' using (bin($2,binwidth)):(1.0) smooth freq with boxes
plot 'test.dat' using (bin($2,0.001)):(1.0) smooth freq with boxes

pause 10
reread
