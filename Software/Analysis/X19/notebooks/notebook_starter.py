import os
tmsDir = os.getenv('HOME')+'/work/repos/TMSPlane'
import sys
sys.path.append(tmsDir+'/Software/Control/src')

from notebook_test import test, get_spectrum
from rootHelper import getRDF
import matplotlib.pyplot as plt
import numpy as np
from ROOT import gPad, gDirectory, gStyle, TCanvas, TGraph
gStyle.SetPalette(55)

dir1 = tmsDir+'/Software/Control/src/data/fpgaLin/'

plt.rc('figure', figsize=(15, 6))

from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))

import ROOT
ROOT.enableJSVis()

c = TCanvas()
