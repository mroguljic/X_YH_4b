import ROOT
import sys
import time, os
from optparse import OptionParser
from collections import OrderedDict


from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *


TIMBERPATH = os.environ["TIMBERPATH"]


def getNweighted(analyzer,isData):
    if not isData:
        nWeighted = a.DataFrame.Sum("genWeight").GetValue()
    else:
        nWeighted = a.DataFrame.Count().GetValue()
    return nWeighted

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
                default   =   'ttbarSemi',
                dest      =   'process',
                help      =   'Process in the given MC file')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('--var', metavar='variation', type='string', action='store',
                default   =   "nom",
                dest      =   'variation',
                help      =   'nom sfUp/Down, jesUp/Down, jerUp/Down')
# parser.add_option('-c', '--channel', metavar='CHANNEL', type='string', action='store', #only running mu channel for now
#                 default   =   'mu',
#                 dest      =   'channel',
#                 help      =   'Electron (e) or muon (mu) channel')

(options, args) = parser.parse_args()
start_time = time.time()
variation = options.variation

CompileCpp("TIMBER/Framework/common.cc") 
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/SemileptonicFunctions.cc") 
CompileCpp("TIMBER/Framework/src/JMSUncShifter.cc") 
CompileCpp("JMSUncShifter jmsShifter = JMSUncShifter();") 
CompileCpp("TIMBER/Framework/src/JMRUncSmearer.cc") 
CompileCpp("JMRUncSmearer jmrSmearer = JMRUncSmearer();") 

a = analyzer(options.input)
runNumber = a.DataFrame.Range(1).AsNumpy(["run"])#just checking the first run number to see if data or MC
if(runNumber["run"][0]>10000):
    isData=True
    print("Running on data")
else:
    isData=False
    print("Running on MC")

if(isData and variation!="nom"):
    print("Not running systematics on data")
    sys.exit()

if isData:
    a.Define("genWeight","1")

nProc = a.genEventSumw

if not isData:
    CompileCpp('TIMBER/Framework/src/AK4Btag_SF.cc')
    print('AK4Btag_SF ak4SF = AK4Btag_SF({0}, "DeepJet", "reshaping");'.format(options.year[2:]))
    CompileCpp('AK4Btag_SF ak4SF = AK4Btag_SF({0}, "DeepJet", "reshaping");'.format(options.year[2:]))

if("je" in variation):#jes,jer
    ptVar  = "Jet_pt_{0}".format(variation.replace("jes","jesTotal"))
    METVar = "MET_T1_pt_{0}".format(variation.replace("jes","jesTotal"))
else:
    ptVar  = "Jet_pt_nom"
    METVar = "MET_T1_pt"

if(isData):
    ptVar  = "Jet_pt"
    METVar = "MET_pt"

histos      = []

if(options.year=="2016"):
    deepJetM = 0.3093
    deepJetL = 0.0614
if(options.year=="2017"):
    deepJetM = 0.3040 
    deepJetL = 0.0532 
if(options.year=="2018"):
    deepJetM = 0.2783 
    deepJetL = 0.0490 

histos=[]
if(options.year=="2016"):
    triggerList = ["HLT_IsoMu24","HLT_IsoTkMu24"]
elif(options.year=="2017"):
    triggerList = ["HLT_IsoMu27"]
else:
    triggerList = ["HLT_IsoMu24"]
lGeneration = 2

#if(options.channel=="mu"):
# elif(options.channel=="e"):
#     triggerList = ["HLT_Ele27_WPTight_Gsf","HLT_Ele35_WPTight_Gsf","HLT_Ele32_WPTight_Gsf","HLT_Photon200","HLT_Photon175"]
#     lGeneration = 1
#     a.Cut("leptonSkimCut","SkimFlag>3 && SkimFlag<8")
# else:
#     print("Define lepton channel '-c mu' or '-c e'!")
#     sys.exit()

nSkimmed = getNweighted(a,isData)


if(isData):
    triggerString = a.GetTriggerString(triggerList)
    a.Cut("Triggers",triggerString)  

nTrigger = getNweighted(a,isData)

if(variation == "sfDown"):
    sfVar = 1
elif(variation=="sfUp"):
    sfVar = 2
else:
    sfVar = 0 

if(isData):
    a.Define("btagDisc",'Jet_btagDeepB') 
else:
    a.Define("btagDisc",'ak4SF.evalCollection(nJet,{0}, Jet_eta, Jet_hadronFlavour,Jet_btagDeepB,{1})'.format(ptVar,sfVar)) 

a.Define("lIdx","tightLeptonIdx(nElectron,Electron_cutBased,nMuon,Muon_tightId,Muon_pfIsoId,{0})".format(lGeneration))
a.Cut("lIdxCut","lIdx>-1")#There is a tight lepton

nTightLepton = getNweighted(a,isData)

a.Define("lPt","leptonPt(Electron_pt,Muon_pt,lIdx,{0})".format(lGeneration))
a.Define("lPhi","leptonPhi(Electron_phi,Muon_phi,lIdx,{0})".format(lGeneration))
a.Define("lEta","leptonEta(Electron_eta,Muon_eta,lIdx,{0})".format(lGeneration))
a.Cut("lPtCut","lPt>40")

nlPt = getNweighted(a,isData)

a.Cut("lEtaCut","abs(lEta)<2.4")
a.Cut("METcut","{0}>60".format(METVar))

nMET = getNweighted(a,isData)


a.Define("goodJetIdxs","goodAK4JetIdxs(nJet, {0}, Jet_eta, Jet_phi, Jet_jetId, lPhi, lEta)".format(ptVar))#pt>30,|eta|<2.4, dR(lepton,jet)>0.4
a.Cut("goodJetIdxsCut","goodJetIdxs.size()>0")

a.Define("leptonSideAK4Idx","leptonSideJetIdx(goodJetIdxs,Jet_eta,Jet_phi,btagDisc,{0},{1},lEta,lPhi)".format(deepJetM,ptVar))
a.Cut("leptonSideAK4Cut","leptonSideAK4Idx>-1")
a.Define("bJetPt","{0}[leptonSideAK4Idx]".format(ptVar))

nBJetLeptonSide = getNweighted(a,isData)


a.Define("HT","HTgoodJets({0}, goodJetIdxs)".format(ptVar))
a.Cut("HTCut","HT>500")

nHT = getNweighted(a,isData)

a.Define("probeJetIdx","probeAK8JetIdx(nFatJet,Fat{0},FatJet_msoftdrop,FatJet_phi,FatJet_eta,FatJet_jetId,lPhi,lEta)".format(ptVar))
a.Cut("probeJetIdxCut","probeJetIdx>-1")
a.Define("probeJetPt","Fat{0}[probeJetIdx]".format(ptVar))
if(options.year=="2017" or options.year=="2018"):
    a.Cut("probeJetPtCut","probeJetPt>450")#350 is used in probeJetIdx

nProbeJet = getNweighted(a,isData)

a.Define("ST","bJetPt+{0}+lPt+probeJetPt".format(METVar))
a.Cut("STcut","ST>500")

nST = getNweighted(a,isData)


#Define branches to store in output
if(isData):
    a.Define("probeJetMass_nom",'FatJet_msoftdrop[probeJetIdx]')
    a.Define("probeJetPNet","FatJet_particleNetMD_Xbb[probeJetIdx]/(FatJet_particleNetMD_Xbb[probeJetIdx]+FatJet_particleNetMD_QCD[probeJetIdx])")
else:
    a.Define("scaledProbeJetNom",'jmsShifter.shiftMsd(FatJet_msoftdrop[probeJetIdx],"{0}",0)'.format(options.year))
    a.Define("scaledProbeJetUp",'jmsShifter.shiftMsd(FatJet_msoftdrop[probeJetIdx],"{0}",2)'.format(options.year))
    a.Define("scaledProbeJetDown",'jmsShifter.shiftMsd(FatJet_msoftdrop[probeJetIdx],"{0}",1)'.format(options.year))
    smearStringNom = "scaledProbeJetNom,1.0,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],1"
    smearStringJMSUp = "scaledProbeJetUp,1.0,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],1"
    smearStringJMSDown = "scaledProbeJetDown,1.0,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],1"
    smearStringJMRUp = "scaledProbeJetNom,1.1,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],2"
    smearStringJMRDown = "scaledProbeJetNom,1.1,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],0"

    a.Define("probeJetMass_nom",'jmrSmearer.smearMsd({0})'.format((smearStringNom)))
    a.Define("probeJetMass_jmsUp",'jmrSmearer.smearMsd({0})'.format((smearStringJMSUp)))
    a.Define("probeJetMass_jmsDown",'jmrSmearer.smearMsd({0})'.format((smearStringJMSDown)))
    a.Define("probeJetMass_jmrDown",'jmrSmearer.smearMsd({0})'.format((smearStringJMRDown)))
    a.Define("probeJetMass_jmrUp",'jmrSmearer.smearMsd({0})'.format((smearStringJMRUp)))

    a.Define("probeJetPNet","FatJet_particleNetMD_Xbb[probeJetIdx]/(FatJet_particleNetMD_Xbb[probeJetIdx]+FatJet_particleNetMD_QCD[probeJetIdx])")
    a.Define("partonCategory","classifyProbeJet(probeJetIdx, FatJet_phi, FatJet_eta, nGenPart, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")


if(options.variation=="nom"):
    cutFlowVars = [nProc,nSkimmed,nTrigger,nTightLepton,nlPt,nMET,nBJetLeptonSide,nHT,nProbeJet,nST]
    cutFlowLabels = ["nProc","Skimmed","Trigger","Tight lepton","Lepton pT > 40 GeV","MET>60","Lepton-side b-tagged AK4","HT>500","ProbeJet found","ST>500"]
    nCutFlowVars = len(cutFlowVars)
    hCutFlow = ROOT.TH1F('{0}_cutflow'.format(options.process),"Number of events after each cut",nCutFlowVars,0.5,nCutFlowVars+0.5)
    for i,var in enumerate(cutFlowVars):
    	hCutFlow.AddBinContent(i+1,var)
    	hCutFlow.GetXaxis().SetBinLabel(i+1, cutFlowLabels[i])
    histos.append(hCutFlow)

outputFile = options.output.replace(".root","_{0}.root".format(variation))

if(isData):
    snapshotColumns = ["lPt","lEta","MET_pt","HT","ST","probeJetMass_nom","probeJetPt","probeJetPNet"]
else:
    snapshotColumns = ["lPt","lEta","MET_pt","HT","ST","probeJetMass_nom","probeJetMass_jmsDown","probeJetMass_jmsUp","probeJetMass_jmrDown","probeJetMass_jmrUp","probeJetPt","probeJetPNet","partonCategory","genWeight"]
opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
a.GetActiveNode().DataFrame.Snapshot("Events",outputFile,snapshotColumns,opts)

out_f = ROOT.TFile(outputFile,"UPDATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
