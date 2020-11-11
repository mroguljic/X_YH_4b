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
parser.add_option('-p', '--process', metavar='PROCESS', type='string', action='store',
                default   =   'X1600_Y100',
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
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
# parser.add_option('-t', '--tagger', metavar='FatJet_Tagger', type='string', action='store',
#                 default   =   'FatJet_ParticleNetMD_probXbb',
#                 dest      =   'tagger',
#                 help      =   'Name of tagger for jet tagging')
# parser.add_option('--taggerShort', metavar='Short tagger suffix', type='string', action='store',
#                 default   =   'pnet',
#                 dest      =   'taggerShort',
#                 help      =   'Will be pasted at the end of histos')


(options, args) = parser.parse_args()
start_time = time.time()


CompileCpp('TIMBER/Framework/massMatching.cc') 
CompileCpp("TIMBER/Framework/common.cc") 
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/taggerOrdering.cc") 
CompileCpp("TIMBER/Framework/helperFunctions.cc") 


a = analyzer(options.input)
histos      = []
# small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
# small_node = Node('small',small_rdf) # makes a node out of the dataframe
# a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

deepJetM = 0.3093
deepJetL = 0.0614
if(options.year=="2017"):
    deepJetM = 0.3033
    deepJetL = 0.0521 
if(options.year=="2018"):
    deepJetM = 0.2770
    deepJetL = 0.0494 

if(options.isSignal):
    YMass = options.massY
    a.Cut("YMass","GenModel_YMass_{0}==1".format(YMass))

nTotal = a.GetActiveNode().DataFrame.Count().GetValue()

MetFilters = ["Flag_BadPFMuonFilter","Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_HBHENoiseIsoFilter","Flag_HBHENoiseFilter","Flag_globalSuperTightHalo2016Filter","Flag_goodVertices"]
#MetFiltersString = ' && '.join(MetFilters)
MetFiltersString = a.GetFlagString(MetFilters)

baselineTrigger="HLT_PFJet260"
triggerList = ["HLT_AK8DiPFJet280_200_TrimMass30","HLT_AK8PFJet450","HLT_PFHT650_WideJetMJJ900DEtaJJ1p5","HLT_AK8PFHT650_TrimR0p1PT0p03Mass50",
"HLT_AK8PFHT700_TrimR0p1PT0p03Mass50","HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30","HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20"]

if(options.year=="2017"):
    triggerList=["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30","HLT_AK8PFJet420_TrimMass30","HLT_AK8PFHT800_TrimMass50",
"HLT_PFJet500","HLT_AK8PFJet500","HLT_AK8PFJet330_PFAK8BTagCSV_p17"]
if(options.year=="2018"):
   triggerList=["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30","HLT_AK8PFJet420_TrimMass30","HLT_AK8PFHT800_TrimMass50",
"HLT_PFJet500","HLT_AK8PFJet500","HLT_AK8PFJet330_PFAK8BTagCSV_p17","HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2"]

triggersStringAll = a.GetTriggerString(triggerList)    
beforeTrigCheckpoint = a.GetActiveNode()
a.Cut("Triggers",triggersStringAll)
if(options.isData):
    a.Cut("MET",MetFiltersString)
nTrig = a.GetActiveNode().DataFrame.Count().GetValue()

#Jet(s) definition
jetDefinitionCuts = CutGroup("Jet definition")
jetDefinitionCuts.Add("nFatJet","nFatJet>1")
jetDefinitionCuts.Add("pT0_cut","FatJet_pt[0]>300")
jetDefinitionCuts.Add("pT1_cut","FatJet_pt[1]>200")
jetDefinitionCuts.Add("Eta0_cut","abs(FatJet_eta[0])<2.4")
jetDefinitionCuts.Add("Eta1_cut","abs(FatJet_eta[1])<2.4")
a.Apply([jetDefinitionCuts])
nJets = a.GetActiveNode().DataFrame.Count().GetValue()
evtColumns = VarGroup("Event columns")
evtColumns.Add("HT_2p4","calculateHT(nJet,Jet_eta,Jet_pt,30.0,2.4)")
evtColumns.Add("HT_5p0","calculateHT(nJet,Jet_eta,Jet_pt,30.0,5.0)")
evtColumns.Add("nAK4_2p4","nAK4(nJet,Jet_eta,Jet_pt,30.0,2.4)")
evtColumns.Add("nAK4_5p0","nAK4(nJet,Jet_eta,Jet_pt,30.0,5.0)")
evtColumns.Add("n_bAK4","n_bAK4(nJet,Jet_eta,Jet_phi,Jet_pt,Jet_btagDeepB,{0},nFatJet,FatJet_eta,FatJet_phi)".format(deepJetM))
evtColumns.Add("n_nonbAK4","n_nonbAK4(nJet,Jet_eta,Jet_phi,Jet_pt,Jet_btagDeepB,{0},nFatJet,FatJet_eta,FatJet_phi)".format(deepJetL))
evtColumns.Add("FatJet_pt0","FatJet_pt[0]")
evtColumns.Add("FatJet_pt1","FatJet_pt[1]")
evtColumns.Add("FatJet_eta0","FatJet_eta[0]")
evtColumns.Add("FatJet_eta1","FatJet_eta[1]")
a.Apply([evtColumns])

h_HT_2p4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_HT_2p4_jetSel'.format(options.process),';AK4 HT, pT>30GeV and |eta|<2.4;Events/10 GeV;',300,0,3000),"HT_2p4")
h_HT_5p0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_HT_5p0_jetSel'.format(options.process),';AK4 HT, pT>30GeV and |eta|<5.0;Events/10 GeV;',300,0,3000),"HT_5p0")
h_nAK4_2p4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nAK4_2p4_jetSel'.format(options.process),';Number of AK4, pT>30GeV and |eta|<2.4;Jets;',10,0,10),"nAK4_2p4")
h_bAK4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_n_bAK4_jetSel'.format(options.process),';Number of b-tagged AK4;Jets;',10,0,10),"n_bAK4")
h_nonbAK4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nonbAK4_jetSel'.format(options.process),';Number of non b-tagged AK4;Jets;',10,0,10),"n_nonbAK4")
h_pt0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_pt0_jetSel'.format(options.process),';Leading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt0")
h_pt1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_pt1_jetSel'.format(options.process),';Subleading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt1")
h_eta0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_eta0_jetSel'.format(options.process),';Leading AK8 jet eta;Jets/0.1;',50,-2.5,2.5),"FatJet_eta0")
h_eta1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_eta1_jetSel'.format(options.process),';Subleading AK8 jet eta;Jets/0.1;',50,-2.5,2.5),"FatJet_eta1")
histos.append(h_HT_2p4)
histos.append(h_HT_5p0)
histos.append(h_nAK4_2p4)
histos.append(h_bAK4)
histos.append(h_nonbAK4)
histos.append(h_pt0)
histos.append(h_pt1)
histos.append(h_eta0)
histos.append(h_eta1)

#need to define variables which we want in n-1 histograms
nm1Columns = VarGroup("NminusOne Columns")
nm1Columns.Add("DeltaEta","abs(FatJet_eta[0] - FatJet_eta[1])")
nm1Columns.Add("mSD0","FatJet_msoftdrop[0]")
nm1Columns.Add("mSD1","FatJet_msoftdrop[1]")
nm1Columns.Add('LeadingVector', 'analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])')
nm1Columns.Add('SubleadingVector',  'analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])')
nm1Columns.Add('mjjHY',     'analyzer::invariantMass(LeadingVector,SubleadingVector)') 

a.Apply([nm1Columns])

nm1Cuts = CutGroup('Preselection')
nm1Cuts.Add("DeltaEta_cut","DeltaEta < 1.3")
nm1Cuts.Add("mSD0_cut","mSD0 > 30")
nm1Cuts.Add("mSD1_cut","mSD1 > 30")
nm1Cuts.Add("mjjHY_cut","mjjHY > 700")

nminusOneNodes = a.Nminus1(nm1Cuts) # NOTE: Returns the nodes with N-1 selections
nminusOneHists = HistGroup('nminus1Hists') # NOTE: HistGroup used to batch operate on histograms

nMinusOneLimits = {"DeltaEta":[0.,5.0,100],"mSD0":[0.,600.,60],"mSD1":[0.,600.,60],"mjjHY":[0.,3000.,30]}#[xMin,xMax,nBins]

# Add hists to group and write out at the end
for nkey in nminusOneNodes.keys():
    #print(nkey)
    if nkey == 'full': continue
    var = nkey.replace('_cut','').replace('minus_','')
    hist = nminusOneNodes[nkey].DataFrame.Histo1D(("{0}_nm1_{1}".format(options.process,var),"nMinusOne {0}".format(var),nMinusOneLimits[var][2],nMinusOneLimits[var][0],nMinusOneLimits[var][1]),var)
    nminusOneHists.Add(var,hist)


a.SetActiveNode(nminusOneNodes["full"])
nPreselection = a.GetActiveNode().DataFrame.Count().GetValue()
h_HT_2p4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_HT_2p4_presel'.format(options.process),';AK4 HT, pT>30GeV and |eta|<2.4;Events/10 GeV;',300,0,3000),"HT_2p4")
h_HT_5p0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_HT_5p0_presel'.format(options.process),';AK4 HT, pT>30GeV and |eta|<5.0;Events/10 GeV;',300,0,3000),"HT_5p0")
h_nAK4_2p4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nAK4_2p4_presel'.format(options.process),';Number of AK4, pT>30GeV and |eta|<2.4;Jets;',15,0,15),"nAK4_2p4")
h_bAK4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_n_bAK4_presel'.format(options.process),';Number of b-tagged AK4;Jets;',10,0,10),"n_bAK4")
h_nonbAK4 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nonbAK4_presel'.format(options.process),';Number of non b-tagged AK4;Jets;',10,0,10),"n_nonbAK4")
h_pt0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_pt0_presel'.format(options.process),';Leading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt0")
h_pt1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_pt1_presel'.format(options.process),';Subleading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt1")
h_eta0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_eta0_presel'.format(options.process),';Leading AK8 jet eta;Jets/0.1;',50,-2.5,2.5),"FatJet_eta0")
h_eta1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_eta1_presel'.format(options.process),';Subleading AK8 jet eta;Jets/0.1;',50,-2.5,2.5),"FatJet_eta1")
histos.append(h_HT_2p4)
histos.append(h_HT_5p0)
histos.append(h_nAK4_2p4)
histos.append(h_bAK4)
histos.append(h_nonbAK4)
histos.append(h_pt0)
histos.append(h_pt1)
histos.append(h_eta0)
histos.append(h_eta1)
a.Define("pnet0","FatJet_ParticleNetMD_probXbb[0]")
a.Define("pnet1","FatJet_ParticleNetMD_probXbb[1]")
a.Define("pnetLow","particleNetLow(pnet0,pnet1)")
a.Define("pnetHigh","particleNetHigh(pnet0,pnet1)")
h_nm1_pnet0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnet0'.format(options.process),';Leading jet ParticleNet score;Events/0.01;',100,0,1),"pnet0")
h_nm1_pnet1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnet1'.format(options.process),';Subleading jet ParticleNet score;Events/0.01;',100,0,1),"pnet1")
h_nm1_pnetLow = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnetLow'.format(options.process),';Lower ParticleNet score;Events/0.01;',100,0,1),"pnetLow")
h_nm1_pnetHigh = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnetHigh'.format(options.process),';Higher ParticleNet score;Events/0.01;',100,0,1),"pnetHigh")
h_nPV = a.GetActiveNode().DataFrame.Histo1D(('{0}_nPV_presel'.format(options.process),';Number of primary vertices;Events;',100,0,100),"PV_npvsGood")
h_nPV_vs_mSD0 = a.GetActiveNode().DataFrame.Histo2D(('{0}_nPV_mSD0_presel'.format(options.process),';Number of primary vertices;Leading jet m_{SD};',100,0,100,60,0.,600.),"PV_npvsGood","mSD0")
h_nPV_vs_mSD1 = a.GetActiveNode().DataFrame.Histo2D(('{0}_nPV_mSD1_presel'.format(options.process),';Number of primary vertices;Subleading jet m_{SD};',100,0,100,60,0.,600.),"PV_npvsGood","mSD1")
histos.append(h_nm1_pnet1)
histos.append(h_nm1_pnet0)
histos.append(h_nm1_pnetLow)
histos.append(h_nm1_pnetHigh)
histos.append(h_nPV)
histos.append(h_nPV_vs_mSD0)
histos.append(h_nPV_vs_mSD1)

idxColumns = VarGroup("idxColumns")
idxColumns.Add("idxH","higgsMassMatchingAlt(FatJet_msoftdrop[0],FatJet_msoftdrop[1])")
idxColumns.Add("idxY","1-idxH")
idxCuts   = CutGroup("idxCuts")
idxCuts.Add("Higgs-tagged cut","idxH>=0")
a.Apply([idxColumns])
a.Apply([idxCuts])
nHiggs = a.GetActiveNode().DataFrame.Count().GetValue()
pnet_T = 0.90
pnet_L = 0.80
dak8_T = 0.90
dak8_L = 0.80

candidateColumns  = VarGroup("candidateColumns")
candidateColumns.Add('ptjH','FatJet_pt[idxH]')
candidateColumns.Add('ptjY','FatJet_pt[idxY]')
candidateColumns.Add('mjY','FatJet_msoftdrop[idxY]')
candidateColumns.Add('mjH','FatJet_msoftdrop[idxH]')
candidateColumns.Add('mjjHY_halfReduced','mjjHY - mjH + 125')
candidateColumns.Add("pnetH","FatJet_ParticleNetMD_probXbb[idxH]")
candidateColumns.Add("pnetY","FatJet_ParticleNetMD_probXbb[idxY]")
candidateColumns.Add("dak8H","FatJet_deepTagMD_ZHbbvsQCD[idxH]")
candidateColumns.Add("dak8Y","FatJet_deepTagMD_ZHbbvsQCD[idxY]")

taggerColumns = VarGroup("taggerColumns")
taggerColumns.Add("pnet_TT","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH] > {0}".format(pnet_T))
taggerColumns.Add("pnet_LL","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH] > {0} && (!pnet_TT)".format(pnet_L))
taggerColumns.Add("pnet_AT","FatJet_ParticleNetMD_probXbb[idxH] > {0} && FatJet_ParticleNetMD_probXbb[idxY]<{1}".format(pnet_L,pnet_L))#Anti-tag region

taggerColumns.Add("dak8_TT","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0}".format(dak8_T))
taggerColumns.Add("dak8_LL","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0} && (!dak8_TT)".format(dak8_L))
taggerColumns.Add("dak8_AT","FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxY]<{1}".format(dak8_L,dak8_L))
a.Apply([candidateColumns,taggerColumns])

a.Cut("pt H cut","ptjH>300")
a.Cut("pt Y cut","ptjY>200")
nBoosted = a.GetActiveNode().DataFrame.Count().GetValue()

h_pnet_pT_H = a.GetActiveNode().DataFrame.Histo2D(('{0}_pnet_pT_H'.format(options.process),'ParticleNet vs pT Y;ParticleNet_H score ;pT_H [GeV];',100,0,1,300,0,3000),'pnetH','ptjH')
h_pnet_pT_Y = a.GetActiveNode().DataFrame.Histo2D(('{0}_pnet_pT_Y'.format(options.process),'ParticleNet vs pT Y;ParticleNet_Y score ;pT_Y [GeV];',100,0,1,300,0,3000),'pnetY','ptjY')
h_dak8_pT_H = a.GetActiveNode().DataFrame.Histo2D(('{0}_dak8_pT_H'.format(options.process),'DeepAK8 vs pT Y;DeepAK8_H score ;pT_H [GeV];',100,0,1,300,0,3000),'dak8H','ptjH')
h_dak8_pT_Y = a.GetActiveNode().DataFrame.Histo2D(('{0}_dak8_pT_Y'.format(options.process),'DeepAK8 vs pT Y;DeepAK8_Y score ;pT_Y [GeV];',100,0,1,300,0,3000),'dak8Y','ptjY')

histos.append(h_pnet_pT_Y)
histos.append(h_pnet_pT_H)
histos.append(h_dak8_pT_Y)
histos.append(h_dak8_pT_H)

if not options.isData:
    a.Define("idx_GenJetH","genJetToRecoMatching(nGenJetAK8,FatJet_phi[idxH],FatJet_eta[idxH],GenJetAK8_phi,GenJetAK8_eta)")
    a.Define("idx_GenJetY","genJetToRecoMatching(nGenJetAK8,FatJet_phi[idxY],FatJet_eta[idxY],GenJetAK8_phi,GenJetAK8_eta)")
    a.Define("GenJetH_mass","GenJetAK8_mass[idxH]")
    a.Define("GenJetY_mass","GenJetAK8_mass[idxY]")
    h_idx_reco_vs_gen = a.GetActiveNode().DataFrame.Histo2D(('{0}_reco_vs_gen'.format(options.process),'Reco Idx vs Gen Idx;Reco jet index; Get jet index',3,-1,2,10,-1,9),'idxH','idx_GenJetH')
    histos.append(h_idx_reco_vs_gen)

h_ptjY = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH'.format(options.process),'FatJetY pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
h_mjY = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY'.format(options.process),'FatJetY mSD;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH'.format(options.process),'FatJetH mSD;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_idxY = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxY'.format(options.process),'idxY',5,-1,4),'idxY')
h_idxH = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxH'.format(options.process),'idxH',5,-1,4),'idxH')
histos.append(h_ptjY)
histos.append(h_ptjH)
histos.append(h_mjY)
histos.append(h_mjH)
histos.append(h_idxY)
histos.append(h_idxH)

#node before we start applying tagger cuts
checkpoint  = a.GetActiveNode()
#-----Trigger study part------
#Separated from the rest of the cut tree
a.SetActiveNode(beforeTrigCheckpoint)
a.Cut("Baseline",baselineTrigger)
if(options.isData):
    a.Cut("MET For Trigger",MetFiltersString)
#need to change names to create nodes with different names than already existing
jetDefinitionCuts.name = "Jet Definition For Trigger"
nm1Columns.name = "NminusOne Columns For Trigger"
nm1Cuts.name = "Preselection For Trigger"
candidateColumns.name = "candidateColumns For Trigger"
idxColumns.name = "idxColumns For Trigger"
idxCuts.name = "idxCuts For Trigger"
a.Apply([jetDefinitionCuts,nm1Columns,nm1Cuts,idxColumns,idxCuts,candidateColumns])
a.Cut("pt H cut For Trigger","ptjH>300")
a.Cut("pt Y cut For Trigger","ptjY>200")


triggersStringAll = a.GetTriggerString(triggerList)  
triggersStringNoBtag = a.GetTriggerString(triggerList[:-1])
h_noTriggers = a.GetActiveNode().DataFrame.Histo2D(('{0}_noTriggers'.format(options.process),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,750,3250,30,30,330),'mjjHY','mjY')
a.Cut("triggers_all",triggersStringAll)
h_triggersAll = a.GetActiveNode().DataFrame.Histo2D(('{0}_triggersAll'.format(options.process),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,750,3250,30,30,330),'mjjHY','mjY')
trigCheckpoint  = a.GetActiveNode()#node with all triggers included
a.Cut("triggers_noBtag",triggersStringNoBtag)
h_triggersNoBtag = a.GetActiveNode().DataFrame.Histo2D(('{0}_triggersNoBtag'.format(options.process),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,750,3250,30,30,330),'mjjHY','mjY')

histos.append(h_noTriggers)
histos.append(h_triggersAll)
histos.append(h_triggersNoBtag)

#return to event selection
a.SetActiveNode(checkpoint)



#-----------------pnet------------------#
a.SetActiveNode(checkpoint)
a.Cut("pnet_TT","pnet_TT==1")
n_pnet_TT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_TT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_pnet_TT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_mjjHY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_pnet_TT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY',)
h_mjjHYRed_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_reduced_pnet_TT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY_halfReduced',)
h_mjY_mjH_mjjHY_pnet_TT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_pnet_TT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_TT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_TT'.format(options.process),'FatJetH pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_TT)
histos.append(h_ptjH_pnet_TT)
histos.append(h_mjjHY_pnet_TT)
histos.append(h_mjjHYRed_pnet_TT)
histos.append(h_mjY_pnet_TT)
histos.append(h_mjH_pnet_TT)
histos.append(h_mjY_mjH_mjjHY_pnet_TT)


#Go back to before tagger cuts were made
a.SetActiveNode(checkpoint)
a.Cut("pnet_LL","pnet_LL==1")
n_pnet_LL = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_LL'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_pnet_LL'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_mjjHY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_pnet_LL'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY',)
h_mjjHYRed_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_reduced_pnet_LL'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY_halfReduced',)
h_mjY_mjH_mjjHY_pnet_LL = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_pnet_LL'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_LL'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_LL'.format(options.process),'FatJetH pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_LL)
histos.append(h_ptjH_pnet_LL)
histos.append(h_mjjHY_pnet_LL)
histos.append(h_mjjHYRed_pnet_LL)
histos.append(h_mjY_pnet_LL)
histos.append(h_mjH_pnet_LL)
histos.append(h_mjY_mjH_mjjHY_pnet_LL)

a.SetActiveNode(checkpoint)
a.Cut("pnet_AT","pnet_AT==1")
n_pnet_AT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_AT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_pnet_AT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_mjjHY_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_pnet_AT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY',)
h_mjjHYRed_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_reduced_pnet_AT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY_halfReduced',)
h_mjY_mjH_mjjHY_pnet_AT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_pnet_AT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_AT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_AT'.format(options.process),'FatJetH pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_AT)
histos.append(h_ptjH_pnet_AT)
histos.append(h_mjjHY_pnet_AT)
histos.append(h_mjjHYRed_pnet_AT)
histos.append(h_mjY_pnet_AT)
histos.append(h_mjH_pnet_AT)
histos.append(h_mjY_mjH_mjjHY_pnet_AT)

#-----------------dak8------------------#
a.SetActiveNode(checkpoint)
a.Cut("dak8_TT","dak8_TT==1")
n_dak8_TT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_TT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_dak8_TT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_mjjHY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_dak8_TT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY',)
h_mjjHYRed_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_reduced_dak8_TT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY_halfReduced',)
h_mjY_mjH_mjjHY_dak8_TT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_dak8_TT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_TT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_TT'.format(options.process),'FatJetH pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_TT)
histos.append(h_ptjH_dak8_TT)
histos.append(h_mjjHYRed_dak8_TT)
histos.append(h_mjjHY_dak8_TT)
histos.append(h_mjY_dak8_TT)
histos.append(h_mjH_dak8_TT)
histos.append(h_mjY_mjH_mjjHY_dak8_TT)


#Go back to before tagger cuts were made
a.SetActiveNode(checkpoint)
a.Cut("dak8_LL","dak8_LL==1")
n_dak8_LL = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_LL'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_dak8_LL'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_mjjHY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_dak8_LL'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY',)
h_mjjHYRed_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_reduced_dak8_LL'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY_halfReduced',)
h_mjY_mjH_mjjHY_dak8_LL = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_dak8_LL'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_LL'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_LL'.format(options.process),'FatJetH pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_LL)
histos.append(h_ptjH_dak8_LL)
histos.append(h_mjjHYRed_dak8_LL)
histos.append(h_mjjHY_dak8_LL)
histos.append(h_mjY_dak8_LL)
histos.append(h_mjH_dak8_LL)
histos.append(h_mjY_mjH_mjjHY_dak8_LL)

a.SetActiveNode(checkpoint)
a.Cut("dak8_AT","dak8_AT==1")
n_pnet_AT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_AT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events/10 GeV;',57,30,600),'mjY')
h_mjH_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_dak8_AT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events/10 GeV;',57,30,600),'mjH')
h_mjjHY_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_dak8_AT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY',)
h_mjjHYRed_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjjHY_reduced_dak8_AT'.format(options.process),'Dijet invariant mass [GeV];Events/10 GeV;',330,700,4000),'mjjHY_halfReduced',)
h_mjY_mjH_mjjHY_dak8_AT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_dak8_AT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_AT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY')
h_ptjH_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_AT'.format(options.process),'FatJetH pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_AT)
histos.append(h_ptjH_dak8_AT)
histos.append(h_mjjHYRed_dak8_AT)
histos.append(h_mjjHY_dak8_AT)
histos.append(h_mjY_dak8_AT)
histos.append(h_mjH_dak8_AT)
histos.append(h_mjY_mjH_mjjHY_dak8_AT)

if not options.isData:
    a.SetActiveNode(checkpoint)
    a.Cut("genJetIdx","idx_GenJetH>=0 && idx_GenJetY>=0")
    h_genJetMassH = a.GetActiveNode().DataFrame.Histo1D(('{0}_genJetM_H'.format(options.process),'GenJetH softdrop mass;Gen jet H mSD [GeV];Events/10 GeV;',57,30,600),'GenJetH_mass')
    h_genJetMassY = a.GetActiveNode().DataFrame.Histo1D(('{0}_genJetM_Y'.format(options.process),'GenJetY softdrop mass;Gen jet Y mSD [GeV];Events/10 GeV;',57,30,600),'GenJetY_mass')
    h_recoJetMassY = a.GetActiveNode().DataFrame.Histo1D(('{0}_recoJetM_Y'.format(options.process),'RecoJetY softdrop mass;Reco jet H mSD [GeV];Events/10 GeV;',57,30,600),'mjY')
    h_recoJetMassH = a.GetActiveNode().DataFrame.Histo1D(('{0}_recoJetM_H'.format(options.process),'RecoJetH softdrop massReco jet Y mSD [GeV];Events/10 GeV;',57,30,600),'mjH')
    histos.append(h_genJetMassY)
    histos.append(h_genJetMassH)
    histos.append(h_recoJetMassY)
    histos.append(h_recoJetMassH)

a.SetActiveNode(checkpoint)
a.Cut("dak8H_cut","dak8H>{0}".format(dak8_L))
h_dak8_mjj_mjY = a.GetActiveNode().DataFrame.Histo3D(('{0}_dak8_mjj_mjY'.format(options.process),'DeepAK8_Y vs mjj vs mj_Y - DeepAK8_H > {0};DeepAK8_Y score ;Dijet invariant mass [GeV]; mSD_Y [GeV]'.format(dak8_L),100,0,1,300,0,3000,100,0,1000),'dak8Y','mjjHY','mjY')
histos.append(h_dak8_mjj_mjY)

a.SetActiveNode(checkpoint)
a.Cut("pnetH_cut","pnetH>{0}".format(pnet_L))
h_pnet_mjj_mjY = a.GetActiveNode().DataFrame.Histo3D(('{0}_pnet_mjj_mjY'.format(options.process),'ParticleNet_Y vs mjj vs mj_Y - ParticleNet_H > {0};ParticlNet_Y score ;Dijet invariant mass [GeV]; mSD_Y [GeV]'.format(pnet_L),100,0,1,300,0,3000,100,0,1000),'pnetY','mjjHY','mjY')
histos.append(h_pnet_mjj_mjY)



hCutFlow = ROOT.TH1F('{0}_cutflow'.format(options.process),"Number of events after each cut",10,0.5,10.5)
hCutFlow.AddBinContent(1,nTotal)
hCutFlow.AddBinContent(2,nTrig)
hCutFlow.AddBinContent(3,nJets)
hCutFlow.AddBinContent(4,nPreselection)
hCutFlow.AddBinContent(5,nHiggs)
hCutFlow.AddBinContent(6,nBoosted)
hCutFlow.AddBinContent(7,n_pnet_TT)
hCutFlow.AddBinContent(8,n_pnet_LL)
hCutFlow.AddBinContent(9,n_dak8_TT)
hCutFlow.AddBinContent(10,n_dak8_LL)
if options.isData:
    hCutFlow.SetBinContent(7,0)
    hCutFlow.SetBinContent(8,0)
    hCutFlow.SetBinContent(9,0)
    hCutFlow.SetBinContent(10,0)


hCutFlow.GetXaxis().SetBinLabel(1, "No cuts")
hCutFlow.GetXaxis().SetBinLabel(2, "Triggers")
hCutFlow.GetXaxis().SetBinLabel(3, "Jets definition")
hCutFlow.GetXaxis().SetBinLabel(4, "Preselection")
hCutFlow.GetXaxis().SetBinLabel(5, "100<H m_{SD}<140")
hCutFlow.GetXaxis().SetBinLabel(6, "H,Y pT")
hCutFlow.GetXaxis().SetBinLabel(7, "pnet TT")
hCutFlow.GetXaxis().SetBinLabel(8, "pnet LL")
hCutFlow.GetXaxis().SetBinLabel(9, "dak8 TT")
hCutFlow.GetXaxis().SetBinLabel(10, "dak8 LL")

histos.append(hCutFlow)


out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
nminusOneHists.Do('Write')
out_f.Close()

#a.PrintNodeTree('node_tree',verbose=True) #not supported at the moment
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
