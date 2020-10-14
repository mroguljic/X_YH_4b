import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools import CMS_lumi
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


CompileCpp('/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/rand01.cc') 
CompileCpp('/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/massMatching.cc') 
CompileCpp("/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/common.cc") 
CompileCpp("/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/deltaRMatching.cc") 


a = analyzer(options.input)
histos      = []
#small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
#small_node = Node('small',small_rdf) # makes a node out of the dataframe
#a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

if(options.isSignal):
    YMass = options.massY
    a.Cut("YMass","GenModel_YMass_{0}==1".format(YMass))

totalEvents = a.GetActiveNode().DataFrame.Count().GetValue()

a.Cut("nFatJet","nFatJet>1")
n_FatJetCut = a.GetActiveNode().DataFrame.Count().GetValue()
a.Cut("Jets eta","abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4")
n_EtaCut = a.GetActiveNode().DataFrame.Count().GetValue()
#a.Define("idxH","getRand01()")
a.Define("idxH","higgsMassMatching(FatJet_msoftdrop[0],FatJet_msoftdrop[1])")
a.Define("idxY","1-idxH")
a.Define("idx_GenJetH","genJetToRecoMatching(nGenJetAK8,FatJet_phi[idxH],FatJet_eta[idxH],GenJetAK8_phi,GenJetAK8_eta)")
a.Define("idx_GenJetY","genJetToRecoMatching(nGenJetAK8,FatJet_phi[idxY],FatJet_eta[idxY],GenJetAK8_phi,GenJetAK8_eta)")
a.Define('ptjH','FatJet_pt[idxH]')
a.Define('ptjY','FatJet_pt[idxY]')
a.Define('mjY','FatJet_msoftdrop[idxY]')
a.Define('mjH','FatJet_msoftdrop[idxH]')
a.Define("DeltaEta","abs(FatJet_eta[0] - FatJet_eta[1])")
a.Define("pnetH","FatJet_ParticleNetMD_probXbb[idxH]")
a.Define("pnetY","FatJet_ParticleNetMD_probXbb[idxY]")
a.Define("GenJetH_mass","GenJetAK8_mass[idxH]")
a.Define("GenJetY_mass","GenJetAK8_mass[idxY]")

h_ptjY_total = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_tot'.format(options.process),'FatJetY pt',300,0,3000),'ptjY')
h_ptjH_total = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_tot'.format(options.process),'FatJetH pt',300,0,3000),'ptjH')
h_mjY_total = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_tot'.format(options.process),'FatJetY mSD',100,0,1000),'mjY')
h_mjH_total = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_tot'.format(options.process),'FatJetH mSD',100,0,1000),'mjH')
h_idx_reco_vs_gen = a.GetActiveNode().DataFrame.Histo2D(('{0}_reco_vs_gen'.format(options.process),'Reco Idx vs Gen Idx',3,-1,2,10,-1,9),'idxH','idx_GenJetH')
h_idxY = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxY'.format(options.process),'idxY',5,-1,4),'idxY')
h_idxH = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxH'.format(options.process),'idxH',5,-1,4),'idxH')
histos.append(h_ptjY_total)
histos.append(h_ptjH_total)
histos.append(h_mjY_total)
histos.append(h_mjH_total)
histos.append(h_idxY)
histos.append(h_idxH)
histos.append(h_idx_reco_vs_gen)

cutsForNminusOne = CutGroup('nMinusOne')
cutsForNminusOne.Add("DeltaEta_cut","DeltaEta < 1.3")
cutsForNminusOne.Add("ptjH_cut","ptjH > 300")
cutsForNminusOne.Add("ptjY_cut","ptjY > 300")
cutsForNminusOne.Add("mjH_cut","mjH > 90 && mjH<140")
cutsForNminusOne.Add("mjY_cut","mjY>60")
cutsForNminusOne.Add("pnetH_cut","pnetH>0.8")
cutsForNminusOne.Add("pnetY_cut","pnetY>0.8")
nminusOneNodes = a.Nminus1(a.GetActiveNode(),cutsForNminusOne) # NOTE: Returns the nodes with N-1 selections
nminusOneHists = HistGroup('nminus1Hists') # NOTE: HistGroup used to batch operate on histograms

nMinusOneLimits = {"DeltaEta":[0.,5.0],"ptjH":[0.,2000.],"ptjY":[0.,2000.],"mjH":[0.,1000.],"mjY":[0.,1000.],"pnetH":[0.,1.],"pnetY":[0.,1.]}

# Add hists to group and write out at the end
for nkey in nminusOneNodes.keys():
    if nkey == 'full': continue
    var = nkey.replace('_cut','').replace('minus_','')
    hist = nminusOneNodes[nkey].DataFrame.Histo1D(("{0}_nm1_{1}".format(options.process,var),"nMinusOne {0}".format(var),100,nMinusOneLimits[var][0],nMinusOneLimits[var][1]),var)
    #hist.SetName("{0}_nm1_{1}".format(options.process,hist.GetName()))
    nminusOneHists.Add(var,hist)

a.Cut("Jets delta eta","DeltaEta < 1.3")
n_DeltaEtaCut = a.GetActiveNode().DataFrame.Count().GetValue()
a.Cut("Jets Pt","FatJet_pt[0] > 300 && FatJet_pt[1] > 300")
n_PtCut = a.GetActiveNode().DataFrame.Count().GetValue()
a.Cut("H jet mass","mjH > 90 && mjH<140")
n_mjHCut = a.GetActiveNode().DataFrame.Count().GetValue()
a.Cut("Y jet mass","mjY>60")
n_mjYCut = a.GetActiveNode().DataFrame.Count().GetValue()

pnet_T = 0.90
pnet_L = 0.80
dak8_T = 0.90
dak8_L = 0.80

newcolumns  = VarGroup("newcolumns")
newcolumns.Add('H_vector',       'analyzer::TLvector(FatJet_pt[idxH],FatJet_eta[idxH],FatJet_phi[idxH],FatJet_msoftdrop[idxH])')
newcolumns.Add('Y_vector',    'analyzer::TLvector(FatJet_pt[idxY],FatJet_eta[idxY],FatJet_phi[idxY],FatJet_msoftdrop[idxY])')
newcolumns.Add('mjjHY',     'analyzer::invariantMass(H_vector,Y_vector)') 

newcolumns.Add("pnet_TT","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH] > {0}".format(pnet_T))
newcolumns.Add("pnet_LL","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH] > {0} && (!pnet_TT)".format(pnet_L))
newcolumns.Add("pnet_ATT","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH]<{1}".format(pnet_T,pnet_L))#Anti-tag (H) Tight (Y)
newcolumns.Add("pnet_ALL","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH]<{0} && (!pnet_ATT)".format(pnet_L))#Anti-tag (H) Loose (Y)

newcolumns.Add("dak8_TT","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0}".format(dak8_T))
newcolumns.Add("dak8_LL","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0} && (!dak8_TT)".format(dak8_L))
newcolumns.Add("dak8_ATT","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH]<{1}".format(dak8_T,dak8_L))
newcolumns.Add("dak8_ALL","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH]<{0} && (!dak8_ATT)".format(dak8_L))


a.Apply([newcolumns])
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

a.SetActiveNode(checkpoint)
a.Cut("genJetIdx","idx_GenJetH>=0 && idx_GenJetY>=0")
h_genJetMassH = a.GetActiveNode().DataFrame.Histo1D(('{0}_genJetM_H'.format(options.process),'GenJetH softdrop mass',100,0,1000),'GenJetH_mass')
h_genJetMassY = a.GetActiveNode().DataFrame.Histo1D(('{0}_genJetM_Y'.format(options.process),'GenJetY softdrop mass',100,0,1000),'GenJetY_mass')
h_recoJetMassY = a.GetActiveNode().DataFrame.Histo1D(('{0}_recoJetM_Y'.format(options.process),'RecoJetY softdrop mass',100,0,1000),'mjY')
h_recoJetMassH = a.GetActiveNode().DataFrame.Histo1D(('{0}_recoJetM_H'.format(options.process),'RecoJetH softdrop mass',100,0,1000),'mjH')
histos.append(h_genJetMassY)
histos.append(h_genJetMassH)
histos.append(h_recoJetMassY)
histos.append(h_recoJetMassH)

hCutFlow = ROOT.TH1F("hCutFlow","Number of events after each cut",11,0.5,11.5)
hCutFlow.AddBinContent(1,totalEvents)
hCutFlow.AddBinContent(2,n_FatJetCut)
hCutFlow.AddBinContent(3,n_EtaCut)
hCutFlow.AddBinContent(4,n_DeltaEtaCut)
hCutFlow.AddBinContent(5,n_PtCut)
hCutFlow.AddBinContent(6,n_mjHCut)
hCutFlow.AddBinContent(7,n_mjYCut)
hCutFlow.AddBinContent(8,n_dak8_TT)
hCutFlow.AddBinContent(9,n_dak8_LL)
hCutFlow.AddBinContent(10,n_pnet_TT)
hCutFlow.AddBinContent(11,n_pnet_LL)

hCutFlow.GetXaxis().SetBinLabel(1, "no cuts")
hCutFlow.GetXaxis().SetBinLabel(2, "nFatJet>1")
hCutFlow.GetXaxis().SetBinLabel(3, "|eta|<2.4")
hCutFlow.GetXaxis().SetBinLabel(4, "Delta eta < 1.3")
hCutFlow.GetXaxis().SetBinLabel(5, "FatJet pT 1,2 > 300")
hCutFlow.GetXaxis().SetBinLabel(6, "110<mjH<140")
hCutFlow.GetXaxis().SetBinLabel(7, "mjY>60")
hCutFlow.GetXaxis().SetBinLabel(8, "pnet TT")
hCutFlow.GetXaxis().SetBinLabel(9, "pnet LL")
hCutFlow.GetXaxis().SetBinLabel(10, "dak8 TT")
hCutFlow.GetXaxis().SetBinLabel(11, "dak8 LL")

histos.append(hCutFlow)


out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
nminusOneHists.Do('Write')
out_f.Close()

a.PrintNodeTree('node_tree',verbose=True)
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
