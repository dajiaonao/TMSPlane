#!/bin/bash

viewer(){
	while : 
	do
		ps -ef |grep L5902:localhost:5902 |grep ssh >/dev/null
		echo $?
		if [ $? -eq 1 ]; then
			sleep 1
			print "Waiting..."
			continue
		fi
		sleep 5
		vncviewer localhost:5902
		break
	done
}

viewer &
ssh -A -L5902:localhost:5902 dlzhang@fpgalin.dhcp.lbl.gov
