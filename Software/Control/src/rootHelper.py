#!/usr/bin/env python
from ROOT import TChain

tree_name = 'tree1'
def getChain(files, treename=tree_name, dir1=''):
    ch = TChain(treename)
    ch.Add(dir1+files)
    return ch

import ROOT
import glob
keepObj = []
def getRDF(pattern, treename=tree_name, title=''):
    ch1 = ROOT.TChain(treename,title)
    for f in glob.glob(pattern): ch1.Add(f)

    keepObj.append(ch1) # to keep this object in the memory
    return ROOT.RDataFrame(ch1), ch1
