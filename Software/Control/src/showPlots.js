function showPlots(pID, headTag, order=0){
	head = headTag+"_"+pID.toString()+'_'
	document.write("<p>Plots for "+pID.toString()+" with pattern: "+head+"[1-90].png"+"</p>");

	for(var i=1; i<11; i++){
	  v = 2.0+(i-1)*0.1
	  vs = v.toString()
	  if (vs.length == 1) vs += ".0"
	  document.write("<p>"+vs);
	  for(var j=0; j<9; j++){
	    k = i+j*10
	    if (order==1) k = (i-1)*9+j+1
	    var x= head+k.toString()+".png"
	    document.write('<a href="'+ x +'"><img src="'+x+'" height="90" /></a>')
	  }
	  document.write("</p>");
	}
}
