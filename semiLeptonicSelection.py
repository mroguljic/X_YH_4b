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
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')

(options, args) = parser.parse_args()
start_time = time.time()


CompileCpp("TIMBER/Framework/common.cc") 
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/SemileptonicFunctions.cc") 


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

histos=[]
a.Cut("leptonSkimCut","SkimFlag>3")
nSkimmed = a.DataFrame.Count().GetValue()
print(nSkimmed)

#Event selection
triggerList = ["HLT_Ele27_WPTight_Gsf","HLT_Ele35_WPTight_Gsf","HLT_Ele32_WPTight_Gsf","HLT_IsoMu24","HLT_IsoMu27"]
triggerString = a.GetTriggerString(triggerList) 
a.Cut("Triggers",triggerString)  
nTrigger = a.DataFrame.Count().GetValue() 
print(nTrigger)

a.Define("lGeneration","leptonGeneration(SkimFlag)")
a.Cut("lGenerationCut","lGeneration>0")#skimming cut should be equivalent to this, defines if we're looking at ele or muon
a.Define("lIdx","tightLeptonIdx(nElectron,Electron_cutBased,nMuon,Muon_tightId,Muon_pfIsoId,lGeneration)")
a.Cut("lIdxCut","lIdx>-1")#There is a tight lepton
nTightLepton = a.DataFrame.Count().GetValue()
print(nTightLepton)

a.Define("lPt","leptonPt(Electron_pt,Muon_pt,lIdx,lGeneration)")
a.Define("lPhi","leptonPhi(Electron_phi,Muon_phi,lIdx,lGeneration)")
a.Define("lEta","leptonEta(Electron_eta,Muon_eta,lIdx,lGeneration)")
a.Cut("lPtCut","lPt>40")
nlPt = a.DataFrame.Count().GetValue()
print(nlPt)
a.Cut("lEtaCut","abs(lEta)<2.4")
nlEta = a.DataFrame.Count().GetValue()
print(nlEta)
a.Define("goodJetIdxs","goodAK4JetIdxs(nJet, Jet_pt, Jet_eta, Jet_phi, Jet_jetId, lPhi, lEta)")
a.Cut("goodJetIdxsCut","goodJetIdxs.size()>0")
nGoodJets = a.DataFrame.Count().GetValue()
print(nGoodJets)
a.Define("leadingJetPt","Jet_pt[goodJetIdxs[0]]")
a.Define("leadingJetIdx","goodJetIdxs[0]")

a.Cut("leadingJetPtCut","leadingJetPt>200")
nJetPt = a.DataFrame.Count().GetValue()
print(nJetPt)
a.Cut("leadingJetBTagCut","Jet_btagDeepB[goodJetIdxs[0]]>{0}".format(deepJetM))
nJetBTag = a.DataFrame.Count().GetValue()
print(nJetBTag)
a.Define("nbAk4","nbAK4(Jet_btagDeepB, goodJetIdxs, {0})".format(deepJetM))
a.Cut("nbAk4Cut","nbAk4>1")
n2Ak4bJets = a.DataFrame.Count().GetValue()
print(n2Ak4bJets)
a.Define("HT","HTgoodJets(Jet_pt, goodJetIdxs)")
a.Cut("HTCut","HT>500")
nHT = a.DataFrame.Count().GetValue()
print(nHT)
a.Cut("METcut","MET_pt>60")
nMET = a.DataFrame.Count().GetValue()
print(nMET)
a.Define("ST","leadingJetPt+MET_pt+lPt")
a.Cut("STcut","ST>500")
nST = a.DataFrame.Count().GetValue()
print(nST)

#Histograms after event selection
checkpoint  = a.GetActiveNode()#checkpoint before applying jet classifications
a.Cut("eleCut","lGeneration==1")
h_leadingJetPt = a.GetActiveNode().DataFrame.Histo1D(('{0}_eLeadingJetPt'.format(options.process),'Leading jet pt;p_{T}[GeV];Events/10 GeV;',200,0,2000),'leadingJetPt')
h_leadingJetIdx = a.GetActiveNode().DataFrame.Histo1D(('{0}_eLeadingJetIdx'.format(options.process),'Leading jet idx;Index;Jet/index;',10,0,10),'leadingJetIdx')
h_lPt = a.GetActiveNode().DataFrame.Histo1D(('{0}_ePt'.format(options.process),'Electron pt;p_{T}[GeV];Events/10 GeV;',200,0,2000),'lPt')
h_MET = a.GetActiveNode().DataFrame.Histo1D(('{0}_eMET'.format(options.process),'MET pt;p_{T}[GeV];Events/10 GeV;',100,0,1000),'MET_pt')
histos.append(h_leadingJetPt)
histos.append(h_leadingJetIdx)
histos.append(h_lPt)
histos.append(h_MET)

a.SetActiveNode(checkpoint)
a.Cut("muCut","lGeneration==2")
h_leadingJetPt = a.GetActiveNode().DataFrame.Histo1D(('{0}_mLeadingJetPt'.format(options.process),'Leading jet pt;p_{T}[GeV];Events/10 GeV;',200,0,2000),'leadingJetPt')
h_leadingJetIdx = a.GetActiveNode().DataFrame.Histo1D(('{0}_mLeadingJetIdx'.format(options.process),'Leading jet idx;Index;Jet/index;',10,0,10),'leadingJetIdx')
h_lPt = a.GetActiveNode().DataFrame.Histo1D(('{0}_mPt'.format(options.process),'Muon pt;p_{T}[GeV];Events/10 GeV;',200,0,2000),'lPt')
h_MET = a.GetActiveNode().DataFrame.Histo1D(('{0}_mMET'.format(options.process),'MET pt;p_{T}[GeV];Events/10 GeV;',100,0,1000),'MET_pt')
histos.append(h_leadingJetPt)
histos.append(h_leadingJetIdx)
histos.append(h_lPt)
histos.append(h_MET)

#Tag and probe
a.SetActiveNode(checkpoint)
a.Define("probeJetIdx","probeAK8JetIdx(nFatJet,FatJet_pt,FatJet_msoftdrop,FatJet_phi,FatJet_eta,FatJet_jetId,lPhi,lEta)")
a.Cut("probeJetIdxCut","probeJetIdx>-1")
print(a.GetActiveNode().DataFrame.Count().GetValue())
a.Define("nBH","FatJet_nBHadrons[probeJetIdx]")
a.Define("nCH","FatJet_nCHadrons[probeJetIdx]")

#Classification with n hadrons
a.Define("n2plusB","nBH>1")
a.Define("n1B1plusC","nBH==1 && nCH>0")
a.Define("n1B0C","nBH==1 && nCH==0")
a.Define("n0B1plusC","nBH==0 && nCH>0")
a.Define("n0B0C","nBH==0 && nCH==0")
a.Define("nBnCElse","!(n2plusB || n1B1plusC || n1B0C || n0B1plusC || n0B0C)")
checkpoint  = a.GetActiveNode()#checkpoint before applying jet classifications

a.Cut("n2plusBCut","n2plusB")
print(a.GetActiveNode().DataFrame.Count().GetValue())

a.SetActiveNode(checkpoint)
a.Cut("n1B1plusCCut","n1B1plusC")
print(a.GetActiveNode().DataFrame.Count().GetValue())

a.SetActiveNode(checkpoint)
a.Cut("n1B0CCut","n1B0C")
print(a.GetActiveNode().DataFrame.Count().GetValue())

a.SetActiveNode(checkpoint)
a.Cut("n0B0CCut","n0B0C")
print(a.GetActiveNode().DataFrame.Count().GetValue())

a.SetActiveNode(checkpoint)
a.Cut("nBnCElseCut","nBnCElse")
print(a.GetActiveNode().DataFrame.Count().GetValue())

#Classification with partons
a.SetActiveNode(checkpoint)
a.Define("partonCategory","classifyProbeJet(probeJetIdx, FatJet_phi, FatJet_eta, nGenPart, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
print(a.GetActiveNode().DataFrame.Count().GetValue())
h_leadingJetPt = a.GetActiveNode().DataFrame.Histo1D(('{0}_partonCategory'.format(options.process),'Jet content category;Category;;',4,0,4),'partonCategory')
histos.append(h_leadingJetPt)

cutFlowVars = [nSkimmed,nTrigger,nTightLepton,nlPt,nGoodJets,nJetPt,nJetBTag,n2Ak4bJets,nHT,nMET,nST]
cutFlowLabels = ["Skimmed","Trigger","Tight lepton","Lepton pT > 40 GeV","Good jet exists","Leading Ak4 pT > 200 GeV","Leading jet b-tag","Two b jets","HT>500","MET>60","ST>500"]
nCutFlowVars = len(cutFlowVars)
hCutFlow = ROOT.TH1F('{0}_cutflow'.format(options.process),"Number of events after each cut",nCutFlowVars,0.5,nCutFlowVars+0.5)
for i,var in enumerate(cutFlowVars):
	hCutFlow.AddBinContent(i+1,var)
	hCutFlow.GetXaxis().SetBinLabel(i+1, cutFlowLabels[i])


histos.append(hCutFlow)
#a.PrintNodeTree('node_tree.png',verbose=True) #not supported at the moment
out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
