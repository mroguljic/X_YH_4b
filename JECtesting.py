import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *


CompileCpp("TIMBER/Framework/JESShiftTesting.cc") 


a = analyzer("nano_9.root")

small_rdf = a.GetActiveNode().DataFrame.Range(100)
small_node = Node('small',small_rdf)
a.SetActiveNode(small_node)

a.Define("JESUnc",'testJESShifter("Summer19UL18_V5_MC_Uncertainty_AK8PFPuppi.txt")') 

h = a.GetActiveNode().DataFrame.Histo1D(("testhist","",10,0,10),"JESUnc")

out_f = ROOT.TFile("test.root","RECREATE")
h.Write()
out_f.Close()


