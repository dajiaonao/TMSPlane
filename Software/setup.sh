#!/bin/bash
# echo $0 $1
# echo $BASH_SOURCE
# export TMS_HOME_DIR=`pwd`
dirx=`realpath $BASH_SOURCE`
export TMS_HOME_DIR=`dirname $dirx`
export TMS_DATA_DIR='${TMS_HOME_DIR}/Control/src/data/fpgaLin/'
export PYTHONPATH=$PYTHONPATH:$TMS_HOME_DIR/python
