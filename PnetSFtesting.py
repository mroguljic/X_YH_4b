import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

CompileCpp('TIMBER/Framework/src/btagSFHandler.cc')
#CompileCpp('btagSFHandler btagHandler = btagSFHandler({0.8,0.95},{0.71,0.53},2016,0);')
CompileCpp('btagSFHandler btagHandler = btagSFHandler({0.8,0.95},{0.48,0.31},2016,0);')

a = analyzer("nano_9.root")

#small_rdf = a.GetActiveNode().DataFrame.Range(100)
#small_node = Node('small',small_rdf)
#a.SetActiveNode(small_node)
a.Cut("nFatJet","nFatJet>1")

a.Define("Pnet0",'FatJet_ParticleNetMD_probXbb[0]')
a.Define("pt0",'FatJet_pt[0]')
a.Define("Pnet1",'FatJet_ParticleNetMD_probXbb[1]')
a.Define("taggerCats0","btagHandler.createTaggingCategories(Pnet0)")
a.Define("updatedCats0","btagHandler.updateTaggingCategories(taggerCats0,pt0)")

h1 = a.GetActiveNode().DataFrame.Histo1D(("taggerCats0","",10,0,10),"taggerCats0")
h2 = a.GetActiveNode().DataFrame.Histo1D(("updatedCats0","",10,0,10),"updatedCats0")
out_f = ROOT.TFile("test.root","RECREATE")
h1.Write()
h2.Write()
out_f.Close() 

