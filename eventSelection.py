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
CompileCpp('/afs/cern.ch/work/m/mrogulji/X_YH_4b/HAMMER/Framework/rand01.cc') 


a = analyzer(options.input)
histos      = []
#small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
# small_node = Node('small',small_rdf) # makes a node out of the dataframe
# a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

if(options.isSignal):
    a.Cut("YMass","GenModel_YMass_125==1")

totalEvents = a.GetActiveNode().DataFrame.Count().GetValue()

a.Cut("nFatJet","nFatJet>1")
a.Define("idxY","getRand01()")
a.Define("idxH","1-idxY")
a.Define('ptjH','FatJet_pt[idxH]')
a.Define('ptjY','FatJet_pt[idxY]')
a.Define('mjY','FatJet_msoftdrop[idxY]')
a.Define('mjH','FatJet_msoftdrop[idxH]')

h_ptjY_total = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_tot'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_total = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_tot'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
h_test1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxY'.format(options.process),'idxY',5,-1,4),'idxY')
h_test2 = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxH'.format(options.process),'idxH',5,-1,4),'idxH')
histos.append(h_ptjY_total)
histos.append(h_ptjH_total)
histos.append(h_test1)
histos.append(h_test2)

selectionCuts    = CutGroup("selection")
selectionCuts.Add("Jets eta","abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4")
selectionCuts.Add("Jets delta eta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
selectionCuts.Add("Jets Pt","FatJet_pt[0] > 300 && FatJet_pt[1] > 300")
#selectionCuts.Add("mjH","mjH>110 && mjH<140")
selectionCuts.Add("mjY","mjY>110 && mjY<140")

newcolumns  = VarGroup("newcolumns")
newcolumns.Add('H_vector',       'analyzer::TLvector(FatJet_pt[idxH],FatJet_eta[idxH],FatJet_phi[idxH],FatJet_msoftdrop[idxH])')
newcolumns.Add('Y_vector',    'analyzer::TLvector(FatJet_pt[idxY],FatJet_eta[idxY],FatJet_phi[idxY],FatJet_msoftdrop[idxY])')
newcolumns.Add('mjjHY',     'analyzer::invariantMass(H_vector,Y_vector)') 

newcolumns.Add("pnet_TT","FatJet_ParticleNetMD_probXbb[idxY] > 0.93 && FatJet_ParticleNetMD_probXbb[idxH] > 0.93")
newcolumns.Add("pnet_LL","FatJet_ParticleNetMD_probXbb[idxY] > 0.85 && FatJet_ParticleNetMD_probXbb[idxH] > 0.85 && (!pnet_TT)")
newcolumns.Add("pnet_ATT","FatJet_ParticleNetMD_probXbb[idxY] > 0.93 && FatJet_ParticleNetMD_probXbb[idxH]<0.85")#Anti-tag (H) Tight (Y)
newcolumns.Add("pnet_ALL","FatJet_ParticleNetMD_probXbb[idxY] > 0.85 && FatJet_ParticleNetMD_probXbb[idxH]<0.85 && (!pnet_ATT)")#Anti-tag (H) Loose (Y)

newcolumns.Add("dak8_TT","FatJet_deepTagMD_ZHbbvsQCD[idxY] > 0.97 && FatJet_deepTagMD_ZHbbvsQCD[idxH] > 0.97")
newcolumns.Add("dak8_LL","FatJet_deepTagMD_ZHbbvsQCD[idxY] > 0.80 && FatJet_deepTagMD_ZHbbvsQCD[idxH] > 0.80 && (!dak8_TT)")
newcolumns.Add("dak8_ATT","FatJet_deepTagMD_ZHbbvsQCD[idxY] > 0.97 && FatJet_deepTagMD_ZHbbvsQCD[idxH]<0.80")
newcolumns.Add("dak8_ALL","FatJet_deepTagMD_ZHbbvsQCD[idxY] > 0.80 && FatJet_deepTagMD_ZHbbvsQCD[idxH]<0.80 && (!dak8_ATT)")


a.Apply([selectionCuts,newcolumns])
checkpoint  = a.GetActiveNode()
nAfterSelection = a.GetActiveNode().DataFrame.Count().GetValue()
h_ptjY_selection = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_sel'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_selection = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_sel'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_selection)
histos.append(h_ptjH_selection)

#-----------------pnet------------------#
a.Cut("pnet_TT","pnet_TT==1")
n_pnet_TT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_TT'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_pnet_TT = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_pnet_TT'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_TT'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_TT'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_TT)
histos.append(h_ptjH_pnet_TT)
histos.append(h_mjY_pnet_TT)
histos.append(h_mjH_mjjHY_pnet_TT)


#Go back to before tagger cuts were made
a.SetActiveNode(checkpoint)
a.Cut("pnet_LL","pnet_LL==1")
n_pnet_LL = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_LL'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_pnet_LL = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_pnet_LL'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_LL'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_LL'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_LL)
histos.append(h_ptjH_pnet_LL)
histos.append(h_mjY_pnet_LL)
histos.append(h_mjH_mjjHY_pnet_LL)

a.SetActiveNode(checkpoint)
a.Cut("pnet_ATT","pnet_ATT==1")
h_mjY_pnet_ATT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_ATT'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_pnet_ATT = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_pnet_ATT'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_pnet_ATT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_ATT'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_pnet_ATT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_ATT'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_ATT)
histos.append(h_ptjH_pnet_ATT)
histos.append(h_mjY_pnet_ATT)
histos.append(h_mjH_mjjHY_pnet_ATT)

a.SetActiveNode(checkpoint)
a.Cut("pnet_ALL","pnet_ALL==1")
h_mjY_pnet_ALL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_ALL'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_pnet_ALL = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_pnet_ALL'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_pnet_ALL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_ALL'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_pnet_ALL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_ALL'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_ALL)
histos.append(h_ptjH_pnet_ALL)
histos.append(h_mjY_pnet_ALL)
histos.append(h_mjH_mjjHY_pnet_ALL)


hCutFlow_pnet = ROOT.TH1F("hCutFlow_pnet","Number of events after each cut",4,0.,4.)
hCutFlow_pnet.AddBinContent(1,totalEvents)
hCutFlow_pnet.AddBinContent(2,nAfterSelection)
hCutFlow_pnet.AddBinContent(3,n_pnet_TT)
hCutFlow_pnet.AddBinContent(4,n_pnet_LL)
histos.append(hCutFlow_pnet)

#-----------------dak8------------------#
a.SetActiveNode(checkpoint)
a.Cut("dak8_TT","dak8_TT==1")
n_dak8_TT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_TT'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_dak8_TT = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_dak8_TT'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_TT'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_TT'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_TT)
histos.append(h_ptjH_dak8_TT)
histos.append(h_mjY_dak8_TT)
histos.append(h_mjH_mjjHY_dak8_TT)


#Go back to before tagger cuts were made
a.SetActiveNode(checkpoint)
a.Cut("dak8_LL","dak8_LL==1")
n_dak8_LL = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_LL'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_dak8_LL = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_dak8_LL'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_LL'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_LL'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_LL)
histos.append(h_ptjH_dak8_LL)
histos.append(h_mjY_dak8_LL)
histos.append(h_mjH_mjjHY_dak8_LL)

a.SetActiveNode(checkpoint)
a.Cut("dak8_ATT","dak8_ATT==1")
h_mjY_dak8_ATT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_ATT'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_dak8_ATT = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_dak8_ATT'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_dak8_ATT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_ATT'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_dak8_ATT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_ATT'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_ATT)
histos.append(h_ptjH_dak8_ATT)
histos.append(h_mjY_dak8_ATT)
histos.append(h_mjH_mjjHY_dak8_ATT)

a.SetActiveNode(checkpoint)
a.Cut("dak8_ALL","dak8_ALL==1")
h_mjY_dak8_ALL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_ALL'.format(options.process),'FatJetY softdrop mass',100,0,1000),'mjY')
h_mjH_mjjHY_dak8_ALL = a.GetActiveNode().DataFrame.Histo2D(('{0}_mjH_mjjHY_dak8_ALL'.format(options.process),'mjjHY vs mjH',100,0,1000,300,0,3000),'mjH','mjjHY')
h_ptjY_dak8_ALL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_ALL'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_dak8_ALL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_ALL'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_ALL)
histos.append(h_ptjH_dak8_ALL)
histos.append(h_mjY_dak8_ALL)
histos.append(h_mjH_mjjHY_dak8_ALL)


hCutFlow_dak8 = ROOT.TH1F("hCutFlow_dak8","Number of events after each cut",4,0.,4.)
hCutFlow_dak8.AddBinContent(1,totalEvents)
hCutFlow_dak8.AddBinContent(2,nAfterSelection)
hCutFlow_dak8.AddBinContent(3,n_dak8_TT)
hCutFlow_dak8.AddBinContent(4,n_dak8_LL)
histos.append(hCutFlow_dak8)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()

a.PrintNodeTree('node_tree',verbose=True)
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
