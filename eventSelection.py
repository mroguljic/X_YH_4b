import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from HAMMER.Tools import CMS_lumi
from HAMMER.Tools.Common import *
from HAMMER.Analyzer import *

parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-p', '--process', metavar='PROCESS', type='string', action='store',
                default   =   'Xbb',
                dest      =   'process',
                help      =   'Process in the given MC file')
parser.add_option('-s', '--sig', action="store_true",dest="isSignal",default=False)
parser.add_option('-b', '--bkg', action="store_false",dest="isSignal",default=False)
parser.add_option('--data',action="store_true",dest="isData",default=False)
parser.add_option('-m', '--massY', metavar='GenY mass (if MC signal)', type=int, action='store',
                default   =   200,
                dest      =   'massY',
                help      =   'Mass of the Y')
parser.add_option('-d', '--outdir', metavar='ODIR', type='string', action='store',
                default   =   '.',
                dest      =   'outdir',
                help      =   'Output directory.')
parser.add_option('-t', '--tagger', metavar='FatJet_Tagger', type='string', action='store',
                default   =   'FatJet_ParticleNetMD_probXbb',
                dest      =   'tagger',
                help      =   'Name of tagger for jet tagging')
parser.add_option('--taggerShort', metavar='Short tagger suffix', type='string', action='store',
                default   =   'pnet',
                dest      =   'taggerShort',
                help      =   'Will be pasted at the end of histos')


(options, args) = parser.parse_args()
start_time = time.time()

commonc = CommonCscripts()
CompileCpp(commonc.vector)
CompileCpp(commonc.invariantMass)


a = analyzer(options.input)

#small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
# small_node = Node('small',small_rdf) # makes a node out of the dataframe
# a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

if(options.isSignal):
    a.Cut("YMass","GenModel_YMass_125==1")

h_allEvents = a.GetActiveNode().DataFrame.Histo1D(('{0}_nFatJet'.format(options.process),'nFatJet',20,0,20),'nFatJet')
totalEvents = a.GetActiveNode().DataFrame.Count().GetValue()

selectionCuts    = CutGroup("selection")
selectionCuts.Add("nFatJet","nFatJet>1")
selectionCuts.Add("Jets eta","abs(FatJet_eta[0]) < 2.5 && abs(FatJet_eta[1]) < 2.5")
selectionCuts.Add("Jets delta eta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
selectionCuts.Add("Jets Pt","FatJet_pt[0] > 300 && FatJet_pt[1] > 200")


newcolumns  = VarGroup("newcolumns")
newcolumns.Add('mj0','FatJet_msoftdrop[0]')
newcolumns.Add('mj1','FatJet_msoftdrop[1]')
newcolumns.Add('lead_vector',       'analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])')
newcolumns.Add('sublead_vector',    'analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])')
newcolumns.Add('invariantMass',     'analyzer::invariantMass(lead_vector,sublead_vector)') 
newcolumns.Add("TT","FatJet_ParticleNetMD_probXbb[0] > 0.93 && FatJet_ParticleNetMD_probXbb[1] > 0.93")
newcolumns.Add("LL","FatJet_ParticleNetMD_probXbb[0] > 0.85 && FatJet_ParticleNetMD_probXbb[1] > 0.85 && (!TT)")


a.Apply([selectionCuts,newcolumns])
checkpoint  = a.GetActiveNode()
nAfterSelection = a.GetActiveNode().DataFrame.Count().GetValue()


a.Cut("TT","TT==1")
nAfterTT = a.GetActiveNode().DataFrame.Count().GetValue()


h_invMass_tt = a.GetActiveNode().DataFrame.Histo1D(('{0}_invMass_TT'.format(options.process),'Invariant Mass',100,0,3000),'invariantMass')
h_mj0_tt = a.GetActiveNode().DataFrame.Histo1D(('{0}_mj0_TT'.format(options.process),'FatJet0 softdrop mass',100,0,1000),'mj0')
h_mj1_tt = a.GetActiveNode().DataFrame.Histo1D(('{0}_mj1_TT'.format(options.process),'FatJet1 softdrop mass',100,0,1000),'mj1')


#Go back to before TT cut was made
a.SetActiveNode(checkpoint)
a.Cut("LL","LL==1")
nAfterLL = a.GetActiveNode().DataFrame.Count().GetValue()

h_invMass_ll = a.GetActiveNode().DataFrame.Histo1D(('{0}_invMass_LL'.format(options.process),'Invariant Mass',100,0,3000),'invariantMass')
h_mj0_ll = a.GetActiveNode().DataFrame.Histo1D(('{0}_mj0_LL'.format(options.process),'FatJet0 softdrop mass',100,0,1000),'mj0')
h_mj1_ll = a.GetActiveNode().DataFrame.Histo1D(('{0}_mj1_LL'.format(options.process),'FatJet1 softdrop mass',100,0,1000),'mj1')

hCutFlow = ROOT.TH1F("hCutFlow","Number of events after each cut",4,0.,4.)
hCutFlow.AddBinContent(1,totalEvents)
hCutFlow.AddBinContent(2,nAfterSelection)
hCutFlow.AddBinContent(3,nAfterTT)
hCutFlow.AddBinContent(4,nAfterLL)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
h_allEvents.Write()
h_invMass_tt.Write()
h_mj0_tt.Write()
h_mj1_tt.Write()
h_invMass_ll.Write()
h_mj0_ll.Write()
h_mj1_ll.Write()
hCutFlow.Write()
out_f.Close()

a.PrintNodeTree('node_tree')
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
