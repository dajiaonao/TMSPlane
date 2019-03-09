import sys
#sys.path.append('/data/repos/TMSPlane2/Software/X11/scripts')
sys.path.append('/home/dlzhang/work/repos/TMSPlane/Software/Control/src')

from notebook_test import test, get_spectrum
from rootHelper import getRDF
import matplotlib.pyplot as plt
import numpy as np
from ROOT import gPad, gDirectory, gStyle, TCanvas, TGraph
gStyle.SetPalette(55)

dir1 = '/home/dlzhang/work/repos/TMSPlane/Software/Control/src/data/fpgaLin/'

plt.rc('figure', figsize=(15, 6))

from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))

import ROOT
ROOT.enableJSVis()

c = TCanvas()
