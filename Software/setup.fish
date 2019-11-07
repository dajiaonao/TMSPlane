#!/bin/fish

set -gx TMS_HOME_DIR (pwd)
set -gx TMS_DATA_DIR '${TMS_HOME_DIR}/Control/src/data/fpgaLin/'
set -gx PYTHONPATH $PYTHONPATH:${TMS_HOME_DIR}/python
