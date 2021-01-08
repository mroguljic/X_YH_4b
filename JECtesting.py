import ROOT

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *
import sys


CompileCpp("TIMBER/Framework/JECShiftTesting.cc") 





a = analyzer("nano_9.root")
runNumber = a.DataFrame.Range(1).AsNumpy(["run"])#just checking the first run number to see if data or MC
if(runNumber["run"][0]>10000):
    isData=True
    print("Running on data")
else:
    isData=False
    print("Running on MC")

small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
small_node = Node('small',small_rdf) # makes a node out of the dataframe
a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

a.Define("testCol",'testJECShifter("Summer19UL18_V5_MC_Uncertainty_AK8PFPuppi.txt")') 

h = a.GetActiveNode().DataFrame.Histo1D(("testhist","",10,0,10),"testCol")

out_f = ROOT.TFile("test.root","RECREATE")
h.Write()
out_f.Close()


