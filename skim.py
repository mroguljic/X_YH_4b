import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')

(options, args) = parser.parse_args()
start_time = time.time()
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/helperFunctions.cc") 

a = analyzer(options.input)
print(a.GetActiveNode().DataFrame.Count().GetValue())
small_rdf = a.GetActiveNode().DataFrame.Range(10000) # makes an RDF with only the first nentries considered
small_node = Node('small',small_rdf) # makes a node out of the dataframe
a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node
nTotal = a.GetActiveNode().DataFrame.Count().GetValue()
a.Define("SingleJetFlag","skimmingLeadingAK8Jet(nFatJet,FatJet_eta,FatJet_pt,FatJet_msoftdrop)")
a.Define("DiJetFlag","skimmingTwoAK8Jets(nFatJet,FatJet_eta,FatJet_pt,FatJet_msoftdrop)")
a.Define("JetLeptonFlag","skimmingIsoLepton(nJet,Jet_eta,Jet_pt,nElectron,Electron_cutBased,nMuon,Muon_looseId,Muon_pfIsoId)")
a.Define("SkimFlag","SingleJetFlag+DiJetFlag+JetLeptonFlag")
a.Cut("SkimFlagCut","SkimFlag>0")

# a.Cut("nFatJet","nFatJet>1")
# a.Cut("eta","abs(FatJet_eta[0])<2.4 && abs(FatJet_eta[1])<2.4")
# a.Cut("pT","FatJet_pt[0]>300 && FatJet_pt[1]>300")
# a.Cut("mass","FatJet_msoftdrop[0]>30 && FatJet_msoftdrop[1]>30")
opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
a.GetActiveNode().DataFrame.Snapshot("Events",options.output)
nSkim = a.GetActiveNode().DataFrame.Count().GetValue()
print(nSkim,nTotal,nSkim/nTotal)

hCutFlow = ROOT.TH1F('skimInfo',"Number of processed events",2,0.5,2.5)
hCutFlow.AddBinContent(1,nTotal)
hCutFlow.AddBinContent(2,nSkim)
hCutFlow.GetXaxis().SetBinLabel(1, "Total events")
hCutFlow.GetXaxis().SetBinLabel(2, "After skimming")
out_f = ROOT.TFile(options.output,"UPDATE")
out_f.cd()
hCutFlow.Write()
#a.GetActiveNode().DataFrame.Snapshot("Preselection", options.output,"^((?!GenModel_YMass).+).*$",opts)#Don't store GenModel_YMass branches
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
