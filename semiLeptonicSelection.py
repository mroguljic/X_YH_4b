import ROOT
import sys
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
parser.add_option('-c', '--channel', metavar='CHANNEL', type='string', action='store',
                default   =   'mu',
                dest      =   'channel',
                help      =   'Electron (e) or muon (mu) channel')
parser.add_option('--data',action="store_true",dest="isData",default=False)
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

deepJetM = 0.3093
deepJetL = 0.0614
if(options.year=="2017"):
    deepJetM = 0.3033
    deepJetL = 0.0521 
if(options.year=="2018"):
    deepJetM = 0.2770
    deepJetL = 0.0494 

histos=[]
if(options.channel=="mu"):
    triggerList = ["HLT_IsoMu24","HLT_IsoMu27"]
    lGeneration = 2
    a.Cut("leptonSkimCut","SkimFlag>7")
elif(options.channel=="e"):
    triggerList = ["HLT_Ele27_WPTight_Gsf","HLT_Ele35_WPTight_Gsf","HLT_Ele32_WPTight_Gsf","HLT_Photon200","HLT_Photon175"]
    lGeneration = 1
    a.Cut("leptonSkimCut","SkimFlag>3 && SkimFlag<8")
else:
    print("Define lepton channel '-c mu' or '-c e'!")
    sys.exit()


nSkimmed = a.DataFrame.Count().GetValue()
print(nSkimmed)

#Event selection

if(options.isData):
    triggerString = a.GetTriggerString(triggerList)
    #a.Cut("Triggers",triggerString)  
    print("Skipping triggers, since skims don't have them!")
nTrigger = a.DataFrame.Count().GetValue() 
print(nTrigger)

a.Define("lIdx","tightLeptonIdx(nElectron,Electron_cutBased,nMuon,Muon_tightId,Muon_pfIsoId,{0})".format(lGeneration))
a.Cut("lIdxCut","lIdx>-1")#There is a tight lepton
nTightLepton = a.DataFrame.Count().GetValue()
print(nTightLepton)

a.Define("lPt","leptonPt(Electron_pt,Muon_pt,lIdx,{0})".format(lGeneration))
a.Define("lPhi","leptonPhi(Electron_phi,Muon_phi,lIdx,{0})".format(lGeneration))
a.Define("lEta","leptonEta(Electron_eta,Muon_eta,lIdx,{0})".format(lGeneration))
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
a.Define("dRmin","deltaRClosestJet(goodJetIdxs,Jet_eta,Jet_phi,lEta,lPhi)")

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
a.Cut("dRcut","dRmin<1.5")
nDR = a.DataFrame.Count().GetValue()
print(nDR)
a.Define("probeJetIdx","probeAK8JetIdx(nFatJet,FatJet_pt,FatJet_msoftdrop,FatJet_phi,FatJet_eta,FatJet_jetId,lPhi,lEta)")
a.Cut("probeJetIdxCut","probeJetIdx>-1")
nProbeJet = a.DataFrame.Count().GetValue()
print(nProbeJet)
a.Define("probeJetMass","FatJet_msoftdrop[probeJetIdx]")
a.Define("probeJetPt","FatJet_pt[probeJetIdx]")
a.Define("probeJetPNet","FatJet_ParticleNetMD_probXbb[probeJetIdx]")

if not options.isData:
    #Jet content classification
    print(a.GetActiveNode().DataFrame.Count().GetValue())
    a.Define("nBH","FatJet_nBHadrons[probeJetIdx]")
    a.Define("nCH","FatJet_nCHadrons[probeJetIdx]")
    #Classification with n hadrons
    a.Define("n2plusB","nBH>1")
    a.Define("n1B1plusC","nBH==1 && nCH>0")
    a.Define("n1B0C","nBH==1 && nCH==0")
    a.Define("n0B1plusC","nBH==0 && nCH>0")
    a.Define("n0B0C","nBH==0 && nCH==0")
    a.Define("partonCategory","classifyProbeJet(probeJetIdx, FatJet_phi, FatJet_eta, nGenPart, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")

    checkpoint  = a.GetActiveNode()#checkpoint before applying jet classifications
    confMatrixHistos = []
    a.Cut("n2plusBCut","n2plusB")
    n2plusB = a.GetActiveNode().DataFrame.Count().GetValue()
    print(n2plusB)
    confMatrixHistos.append(a.GetActiveNode().DataFrame.Histo1D(('{0}_2BHConf'.format(options.process),'',4,0,4),'partonCategory'))

    a.SetActiveNode(checkpoint)
    a.Cut("n1B1plusCCut","n1B1plusC")
    n1B1plusC = a.GetActiveNode().DataFrame.Count().GetValue()
    print(n1B1plusC)
    confMatrixHistos.append(a.GetActiveNode().DataFrame.Histo1D(('{0}_1B1pCHConf'.format(options.process),'',4,0,4),'partonCategory'))

    a.SetActiveNode(checkpoint)
    a.Cut("n1B0CCut","n1B0C")
    n1B0C = a.GetActiveNode().DataFrame.Count().GetValue()
    print(n1B0C)
    confMatrixHistos.append(a.GetActiveNode().DataFrame.Histo1D(('{0}_1B1pCHConf'.format(options.process),'',4,0,4),'partonCategory'))

    a.SetActiveNode(checkpoint)
    a.Cut("n0B1plusCCut","n0B1plusC")
    n0B1plusC = a.GetActiveNode().DataFrame.Count().GetValue()
    print(n0B1plusC)
    confMatrixHistos.append(a.GetActiveNode().DataFrame.Histo1D(('{0}_0B1pCHConf'.format(options.process),'',4,0,4),'partonCategory'))

    a.SetActiveNode(checkpoint)
    a.Cut("n0B0CCut","n0B0C")
    n0B0C = a.GetActiveNode().DataFrame.Count().GetValue()
    print(n0B0C)
    confMatrixHistos.append(a.GetActiveNode().DataFrame.Histo1D(('{0}_0B0CHConf'.format(options.process),'',4,0,4),'partonCategory'))


    hadronCats  = ["2b+","1b1+c","1b0c","0b1+c","0b0c"]
    partonCats  = ["unmatched","qq","bq","bqq"]
    hadronCatsN = [n2plusB,n1B1plusC,n1B0C,n0B1plusC,n0B0C]
    nHadronCats = len(hadronCats)

    h2_confusionMatrix = ROOT.TH2F("{0}_confusionMatrix".format(options.process),"",5,0,5,4,0,4)
    for i,h in enumerate(confMatrixHistos):
        for j in range(0,4):
            h2_confusionMatrix.SetBinContent(i+1,j+1,h.GetBinContent(j+1))#+1 to avoid underflow bins

    for i,cat in enumerate(hadronCats):
        h2_confusionMatrix.GetXaxis().SetBinLabel(i+1, hadronCats[i])
    for i,cat in enumerate(partonCats):
        h2_confusionMatrix.GetYaxis().SetBinLabel(i+1, partonCats[i])

    histos.append(h2_confusionMatrix)

    h_hadronCat = ROOT.TH1F('{0}_hadronCategory'.format(options.process),';Jet category;;',nHadronCats,0.5,nHadronCats+0.5)
    for i,N in enumerate(hadronCatsN):
        h_hadronCat.AddBinContent(i+1,N)
        h_hadronCat.GetXaxis().SetBinLabel(i+1, hadronCats[i])
    histos.append(h_hadronCat)


    #Classification with partons
    a.SetActiveNode(checkpoint)
    checkpoint  = a.GetActiveNode()#checkpoint before applying jet classifications
    print(a.GetActiveNode().DataFrame.Count().GetValue())
    h_partonCat = a.GetActiveNode().DataFrame.Histo1D(('{0}_partonCategory'.format(options.process),';Jet category;;',4,0,4),'partonCategory')
    for i,cat in enumerate(partonCats):
        h_partonCat.GetXaxis().SetBinLabel(i+1, partonCats[i])
    histos.append(h_partonCat)

    a.Cut("qqCut","partonCategory==1")
    h_mSDqq = a.GetActiveNode().DataFrame.Histo1D(('{0}_mSDqq'.format(options.process),';Softdrop mass;;',60,0,300),'probeJetMass')
    histos.append(h_mSDqq)

    a.SetActiveNode(checkpoint)
    a.Cut("bqCut","partonCategory==2")
    h_mSDbq = a.GetActiveNode().DataFrame.Histo1D(('{0}_mSDbq'.format(options.process),';Softdrop mass;;',60,0,300),'probeJetMass')
    histos.append(h_mSDbq)

    a.SetActiveNode(checkpoint)
    a.Cut("bqqCut","partonCategory==3")
    h_mSDbqq = a.GetActiveNode().DataFrame.Histo1D(('{0}_mSDbqq'.format(options.process),';Softdrop mass;;',60,0,300),'probeJetMass')
    histos.append(h_mSDbqq)

    a.SetActiveNode(checkpoint)
    a.Cut("otherCut","partonCategory==0")
    h_mSDother = a.GetActiveNode().DataFrame.Histo1D(('{0}_mSDunmatched'.format(options.process),';Softdrop mass;;',60,0,300),'probeJetMass')
    histos.append(h_mSDother)
    a.SetActiveNode(checkpoint)

cutFlowVars = [0,nSkimmed,nTrigger,nTightLepton,nlPt,nJetPt,nJetBTag,n2Ak4bJets,nHT,nMET,nST,nDR,nProbeJet]
cutFlowLabels = ["nProc","Skimmed","Trigger","Tight lepton","Lepton pT > 40 GeV","Leading Ak4 pT > 200 GeV","Leading jet b-tag","Two medium b jets","HT>500","MET>60","ST>500","dR(l, closest jet)<1.5","ProbeJet found"]
nCutFlowVars = len(cutFlowVars)
hCutFlow = ROOT.TH1F('{0}_cutflow'.format(options.process),"Number of events after each cut",nCutFlowVars,0.5,nCutFlowVars+0.5)
for i,var in enumerate(cutFlowVars):
	hCutFlow.AddBinContent(i+1,var)
	hCutFlow.GetXaxis().SetBinLabel(i+1, cutFlowLabels[i])
histos.append(hCutFlow)

if(options.isData):
    snapshotColumns = ["lPt","MET_pt","HT","ST","probeJetMass","probeJetPt","probeJetPNet"]
else:
    snapshotColumns = ["lPt","MET_pt","HT","ST","probeJetMass","probeJetPt","probeJetPNet","partonCategory"]
opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
print(snapshotColumns)
a.GetActiveNode().DataFrame.Snapshot("Events",options.output,snapshotColumns,opts)

out_f = ROOT.TFile(options.output,"UPDATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
