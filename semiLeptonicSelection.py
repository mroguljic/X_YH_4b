import ROOT
import sys
import time, os
from optparse import OptionParser
from collections import OrderedDict


from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

def getNProc(inputFile):
    nProc        = 0
    if ".root" in inputFile:
        tempFile = ROOT.TFile.Open(inputFile)
        skimInfo = tempFile.Get("skimInfo")
        nProc    = skimInfo.GetBinContent(1)
        tempFile.Close()
        return nProc
    elif ".txt" in inputFile: 
        txt_file     = open(inputFile,"r")
        for l in txt_file.readlines():
            thisfile = l.strip()
            if 'root://' not in thisfile and thisfile.startswith('/store/'): thisfile='root://cms-xrd-global.cern.ch/'+thisfile
            tempFile = ROOT.TFile.Open(thisfile)
            skimInfo = tempFile.Get("skimInfo")
            nProc    += skimInfo.GetBinContent(1)
            tempFile.Close()
    return nProc

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
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('--var', metavar='variation', type='string', action='store',
                default   =   "nom",
                dest      =   'variation',
                help      =   'nom sfUp/Down, jesUp/Down, jerUp/Down')

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

nProc = 0
if not isData:
    CompileCpp('TIMBER/Framework/src/AK4Btag_SF.cc')
    CompileCpp('AK4Btag_SF ak4SF = AK4Btag_SF({0}, "DeepJet", "reshaping");'.format(options.year[2:]))
    nProc = getNProc(options.input)

if("je" in variation):#jes,jer
    ptVar  = "Jet_pt_{0}".format(variation.replace("jes","jesTotal"))
else:
    ptVar  = "Jet_pt_nom"

if(isData):
    ptVar = "Jet_pt"

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

#Event selection

if(isData):
    triggerString = a.GetTriggerString(triggerList)
    #a.Cut("Triggers",triggerString)  
    print("Skipping triggers, since skims don't have them!")
nTrigger = a.DataFrame.Count().GetValue() 


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
nTightLepton = a.DataFrame.Count().GetValue()

a.Define("lPt","leptonPt(Electron_pt,Muon_pt,lIdx,{0})".format(lGeneration))
a.Define("lPhi","leptonPhi(Electron_phi,Muon_phi,lIdx,{0})".format(lGeneration))
a.Define("lEta","leptonEta(Electron_eta,Muon_eta,lIdx,{0})".format(lGeneration))
a.Cut("lPtCut","lPt>40")
nlPt = a.DataFrame.Count().GetValue()
a.Cut("lEtaCut","abs(lEta)<2.4")
nlEta = a.DataFrame.Count().GetValue()
a.Define("goodJetIdxs","goodAK4JetIdxs(nJet, {0}, Jet_eta, Jet_phi, Jet_jetId, lPhi, lEta)".format(ptVar))
a.Cut("goodJetIdxsCut","goodJetIdxs.size()>0")
nGoodJets = a.DataFrame.Count().GetValue()
a.Define("leadingJetPt","{0}[goodJetIdxs[0]]".format(ptVar))
a.Define("leadingJetIdx","goodJetIdxs[0]")
a.Define("dRmin","deltaRClosestJet(goodJetIdxs,Jet_eta,Jet_phi,lEta,lPhi)")

a.Cut("leadingJetPtCut","leadingJetPt>200")
nJetPt = a.DataFrame.Count().GetValue()
a.Cut("leadingJetBTagCut","btagDisc[goodJetIdxs[0]]>{0}".format(deepJetM))
nJetBTag = a.DataFrame.Count().GetValue()
a.Define("nbAk4","nbAK4(btagDisc, goodJetIdxs, {0})".format(deepJetM))
a.Cut("nbAk4Cut","nbAk4>1")
n2Ak4bJets = a.DataFrame.Count().GetValue()
a.Define("HT","HTgoodJets({0}, goodJetIdxs)".format(ptVar))
a.Cut("HTCut","HT>500")
nHT = a.DataFrame.Count().GetValue()
a.Cut("METcut","MET_pt>60")
nMET = a.DataFrame.Count().GetValue()
a.Define("ST","leadingJetPt+MET_pt+lPt")
a.Cut("STcut","ST>500")
nST = a.DataFrame.Count().GetValue()
a.Cut("dRcut","dRmin<1.5")
nDR = a.DataFrame.Count().GetValue()
a.Define("probeJetIdx","probeAK8JetIdx(nFatJet,Fat{0},FatJet_msoftdrop,FatJet_phi,FatJet_eta,FatJet_jetId,lPhi,lEta)".format(ptVar))
a.Cut("probeJetIdxCut","probeJetIdx>-1")
nProbeJet = a.DataFrame.Count().GetValue()

if(isData):
    a.Define("probeJetMass_nom",'FatJet_msoftdrop[probeJetIdx]')
else:
    a.Define("scaledProbeJetNom",'jmsShifter.shiftMsd(FatJet_msoftdrop[probeJetIdx],"{0}",0)'.format(options.year))
    a.Define("scaledProbeJetUp",'jmsShifter.shiftMsd(FatJet_msoftdrop[probeJetIdx],"{0}",2)'.format(options.year))
    a.Define("scaledProbeJetDown",'jmsShifter.shiftMsd(FatJet_msoftdrop[probeJetIdx],"{0}",1)'.format(options.year))
    smearStringNom = "scaledProbeJetNom,0.,1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],1"
    smearStringJMSUp = "scaledProbeJetUp,0.,1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],1"
    smearStringJMSDown = "scaledProbeJetDown,0.,1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],1"
    smearStringJMRUp = "scaledProbeJetNom,0.,1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],2"
    smearStringJMRDown = "scaledProbeJetNom,0.,1.1,GenJetAK8_mass,FatJet_genJetAK8Idx[probeJetIdx],0"

    a.Define("probeJetMass_nom",'jmrSmearer.smearMsd({0})'.format((smearStringNom)))
    a.Define("probeJetMass_jmsUp",'jmrSmearer.smearMsd({0})'.format((smearStringJMSUp)))
    a.Define("probeJetMass_jmsDown",'jmrSmearer.smearMsd({0})'.format((smearStringJMSDown)))
    a.Define("probeJetMass_jmrDown",'jmrSmearer.smearMsd({0})'.format((smearStringJMRDown)))
    a.Define("probeJetMass_jmrUp",'jmrSmearer.smearMsd({0})'.format((smearStringJMRUp)))

    a.Define("probeJetPt","Fat{0}[probeJetIdx]".format(ptVar))
    a.Define("probeJetPNet","FatJet_ParticleNetMD_probXbb[probeJetIdx]")
    a.Define("partonCategory","classifyProbeJet(probeJetIdx, FatJet_phi, FatJet_eta, nGenPart, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")


if(options.variation=="nom"):
    cutFlowVars = [nProc,nSkimmed,nTrigger,nTightLepton,nlPt,nJetPt,nJetBTag,n2Ak4bJets,nHT,nMET,nST,nDR,nProbeJet]
    cutFlowLabels = ["nProc","Skimmed","Trigger","Tight lepton","Lepton pT > 40 GeV","Leading Ak4 pT > 200 GeV","Leading jet b-tag","Two medium b jets","HT>500","MET>60","ST>500","dR(l, closest jet)<1.5","ProbeJet found"]
    nCutFlowVars = len(cutFlowVars)
    hCutFlow = ROOT.TH1F('{0}_cutflow'.format(options.process),"Number of events after each cut",nCutFlowVars,0.5,nCutFlowVars+0.5)
    for i,var in enumerate(cutFlowVars):
    	hCutFlow.AddBinContent(i+1,var)
    	hCutFlow.GetXaxis().SetBinLabel(i+1, cutFlowLabels[i])
    histos.append(hCutFlow)

if(isData):
    snapshotColumns = ["lPt","lEta","MET_pt","HT","ST","probeJetMass_nom","probeJetPt","probeJetPNet"]
else:
    snapshotColumns = ["lPt","lEta","MET_pt","HT","ST","probeJetMass_nom","probeJetMass_jmsDown","probeJetMass_jmsUp","probeJetMass_jmrDown","probeJetMass_jmrUp","probeJetPt","probeJetPNet","partonCategory"]
opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
a.GetActiveNode().DataFrame.Snapshot("Events",options.output,snapshotColumns,opts)

out_f = ROOT.TFile(options.output,"UPDATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
