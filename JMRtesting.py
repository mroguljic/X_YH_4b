import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *

CompileCpp('TIMBER/Framework/src/JMRUncSmearer.cc')
CompileCpp('TIMBER/Framework/include/common.h')
CompileCpp('JMRUncSmearer jmrSmearer = JMRUncSmearer();')

a = analyzer("nano_9.root")

# small_rdf = a.GetActiveNode().DataFrame.Range(10000)
# small_node = Node('small',small_rdf)
# a.SetActiveNode(small_node)
a.Cut("nFatJet","nFatJet>1")

a.Define('lead_vector','hardware::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])')
a.Define("mSDOriginal","FatJet_msoftdrop[0]")
#(float mass, float pt,float sigma,rvec_f GenJetAK8_pt, int FatJet_genJetAK8Idx)
a.Define("mSDsmearDown","jmrSmearer.smearMsd(mSDOriginal,FatJet_pt[0],1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[0],0)")
a.Define("mSDsmearNom","jmrSmearer.smearMsd(mSDOriginal,FatJet_pt[0],1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[0],1)")
a.Define("mSDsmearUp","jmrSmearer.smearMsd(mSDOriginal,FatJet_pt[0],1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[0],2)")

h1 = a.GetActiveNode().DataFrame.Histo1D(("mSDOriginal","",30,0,300),"mSDOriginal")
h2 = a.GetActiveNode().DataFrame.Histo1D(("mSDsmearDown","",30,0,300),"mSDsmearDown")
h3 = a.GetActiveNode().DataFrame.Histo1D(("mSDsmearNom","",30,0,300),"mSDsmearNom")
h4 = a.GetActiveNode().DataFrame.Histo1D(("mSDsmearUp","",30,0,300),"mSDsmearUp")

out_f = ROOT.TFile("test.root","RECREATE")
h1.Write()
h2.Write()
h3.Write()
h4.Write()
out_f.Close()
