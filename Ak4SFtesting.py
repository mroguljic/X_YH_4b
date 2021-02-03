import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

print("Compiling")
CompileCpp('TIMBER/Framework/src/AK4Btag_SF.cc')
print("Instantiating")
CompileCpp('AK4Btag_SF ak4SF = AK4Btag_SF(16, "DeepJet", "reshaping"); \n RVec<float>sf = ak4SF.eval(50.5,1.2,0,0.5);')

a = analyzer("nano_9.root")

small_rdf = a.GetActiveNode().DataFrame.Range(100)
small_node = Node('small',small_rdf)
a.SetActiveNode(small_node)

a.Cut("nJet","nJet>1")
a.Define("reshapedDiscs",'ak4SF.evalCollection(nJet,Jet_pt, Jet_eta, Jet_hadronFlavour, Jet_btagDeepB,"central")') 
a.Define("reshapedDics",'Jet_btagDeepB') 
h = a.GetActiveNode().DataFrame.Histo1D(("testhist","",100,0,1),"test")

out_f = ROOT.TFile("test.root","RECREATE")
h.Write()
out_f.Close()