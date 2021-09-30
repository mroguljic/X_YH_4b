import ROOT

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *
import sys


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
                default   =   'X1600_Y100',
                dest      =   'process',
                help      =   'Process in the given MC file')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('--var', metavar='variation', type='string', action='store',
                default   =   "nom",
                dest      =   'variation',
                help      =   'jmrUp/Down, jmsUp/Down, jesUp/Down, jerUp/Down')

(options, args) = parser.parse_args()
start_time = time.time()
year = options.year

CompileCpp('TIMBER/Framework/massMatching.cc')
CompileCpp("TIMBER/Framework/common.cc") 
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/taggerOrdering.cc") 
CompileCpp("TIMBER/Framework/helperFunctions.cc") 
CompileCpp("TIMBER/Framework/TTstitching.cc") 
CompileCpp("TIMBER/Framework/SemileptonicFunctions.cc") 
CompileCpp("TIMBER/Framework/src/JMSUncShifter.cc") 
CompileCpp("JMSUncShifter jmsShifter = JMSUncShifter();") 
CompileCpp("TIMBER/Framework/src/JMRUncSmearer.cc") 
CompileCpp("JMRUncSmearer jmrSmearer = JMRUncSmearer();") 


varName = options.variation
if(varName=="nom"):
    ptVar  = "FatJet_pt_nom"
elif("jm" in varName):#jmr,jms
    ptVar  = "FatJet_pt_nom"
elif("je" in varName):#jes,jer
    ptVar  = "FatJet_pt_{0}".format(varName.replace("jes","jesTotal"))
else:
    print("Not recognizing shape uncertainty {0}, exiting".format(varName))        
    sys.exit()

a = analyzer(options.input)

# nToRun = 10000
# small_rdf = a.GetActiveNode().DataFrame.Range(nToRun) # makes an RDF with only the first nentries considered
# small_node = Node('small',small_rdf) # makes a node out of the dataframe
# a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node


runNumber = a.DataFrame.Range(1).AsNumpy(["run"])#just checking the first run number to see if data or MC
if(runNumber["run"][0]>10000):
    isData=True
    print("Running on data")
else:
    isData=False
    print("Running on MC")
histos      = []

if isData:
    a.Define("genWeight","1")

nProc = a.genEventSumw


if("TTbar" in options.process):
    a.Define("topIdx","getPartIdx(nGenPart,GenPart_pdgId,GenPart_statusFlags,6)")
    a.Define("antitopIdx","getPartIdx(nGenPart,GenPart_pdgId,GenPart_statusFlags,-6)")
    a.Cut("twoTops","topIdx>-1 && antitopIdx>-1") #perhaps unnecessary
    a.Define("topVector","analyzer::TLvector(GenPart_pt[topIdx],GenPart_eta[topIdx],GenPart_phi[topIdx],GenPart_mass[topIdx])")
    a.Define("antitopVector","analyzer::TLvector(GenPart_pt[antitopIdx],GenPart_eta[antitopIdx],GenPart_phi[antitopIdx],GenPart_mass[antitopIdx])")
    a.Define("MTT",'analyzer::invariantMass(topVector,antitopVector)')
    a.Define("topPt",'GenPart_pt[topIdx]')
    a.Define("antitopPt",'GenPart_pt[antitopIdx]')
    if(year=="2016"):
        a.Define("ttHTFlag","highHTFlag(nGenPart,GenPart_pdgId,GenPart_pt,GenPart_phi,GenPart_eta,GenPart_mass,nGenJetAK8,GenJetAK8_pt,GenJetAK8_phi,GenJetAK8_eta,GenJetAK8_mass)")
        if("HT" in options.process):
            a.Cut("ttHTCut","ttHTFlag==1")
        else:
           a.Cut("ttHTCut","ttHTFlag==0")
    else:
        if(options.process=="TTbar" or options.process=="TTbarSemi"):
            hMTTincl  = a.DataFrame.Histo1D(('{0}_MTT_skim_incl'.format(options.process),';M_{TT} [GeV];;',30,0,3000.),"MTT","genWeight")
            histos.append(hMTTincl)
            a.Cut("MTTcut","MTT<700")
        hMTT  = a.DataFrame.Histo1D(('{0}_MTT_skim'.format(options.process),';M_{TT} [GeV];;',30,0,3000.),"MTT","genWeight")
        histos.append(hMTT)


nSkimmed = getNweighted(a,isData)

MetFilters = ["Flag_BadPFMuonFilter","Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_HBHENoiseIsoFilter","Flag_HBHENoiseFilter","Flag_globalSuperTightHalo2016Filter","Flag_goodVertices"]
if(isData):
    MetFilters.append("Flag_eeBadScFilter")
if(year!="2016"):
    MetFilters.append("Flag_ecalBadCalibFilter")
    MetFilters.append("Flag_eeBadScFilter")
MetFiltersString = a.GetFlagString(MetFilters)

if(year=="2016"):
    if("JetHT2016B" in options.process):
        #2016B does not have the AK8PFJet450 in all files and this causes problems so it's removed from the list
        triggerList = ["HLT_AK8DiPFJet280_200_TrimMass30","HLT_PFHT650_WideJetMJJ900DEtaJJ1p5","HLT_AK8PFHT650_TrimR0p1PT0p03Mass50",
        "HLT_AK8PFHT700_TrimR0p1PT0p03Mass50","HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30","HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20"]
    else:
        triggerList = ["HLT_AK8DiPFJet280_200_TrimMass30","HLT_PFHT650_WideJetMJJ900DEtaJJ1p5","HLT_AK8PFHT650_TrimR0p1PT0p03Mass50",
        "HLT_AK8PFHT700_TrimR0p1PT0p03Mass50","HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30","HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20","HLT_AK8PFJet450"]
elif(year=="2017"):
    triggerList=["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30","HLT_AK8PFJet420_TrimMass30","HLT_AK8PFHT800_TrimMass50",
"HLT_PFJet500","HLT_PFJet320","HLT_AK8PFJet500","HLT_AK8PFJet320"]
elif(year=="2018"):
   triggerList=["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30","HLT_AK8PFJet420_TrimMass30","HLT_AK8PFHT800_TrimMass50",
"HLT_PFJet500","HLT_AK8PFJet500"]

a.Cut("MET",MetFiltersString)
beforeTrigCheckpoint = a.GetActiveNode()
if(isData):
    triggersStringAll = a.GetTriggerString(triggerList)    
    a.Cut("Triggers",triggersStringAll)
    #Only applying trigger to data, will apply trigger turn-on to MC
nTrig = getNweighted(a,isData)


#Jet(s) definition
a.Cut("nFatJet","nFatJet>1")
a.Cut("ID","FatJet_jetId[0]>1 && FatJet_jetId[1]>1")#bit 1 is loose, bit 2 is tight, bit3 is tightlepVeto, we select tight
nJetID = getNweighted(a,isData)
if(year=="2016"):
    a.Cut("Eta","abs(FatJet_eta[0])<2.4 && abs(FatJet_eta[1])<2.4")
else:
    a.Cut("Eta","abs(FatJet_eta[0])<2.5 && abs(FatJet_eta[1])<2.5")
nEta = getNweighted(a,isData)


if(varName=="jmsUp"):
    msdShift = 2
elif(varName=="jmsDown"):
    msdShift = 1
else:
    msdShift = 0

if(varName=="jmrUp"):
    msdSmear = 2
elif(varName=="jmrDown"):
    msdSmear = 0
else:
    msdSmear = 0

evtColumns = VarGroup("Event columns")
if isData:
    evtColumns.Add("correctedMSD",'RVec<float> {FatJet_msoftdrop[0],FatJet_msoftdrop[1]}')
else:
    smearString1 = "scaledMSD[0],1.1,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[0],{0}".format(msdSmear)
    smearString2 = "scaledMSD[1],1.1,nGenJetAK8,GenJetAK8_mass,FatJet_genJetAK8Idx[1],{0}".format(msdSmear)
    evtColumns.Add("scaledMSD",'RVec<float> {jmsShifter.shiftMsd(FatJet_msoftdrop[0],"%s",%i),jmsShifter.shiftMsd(FatJet_msoftdrop[1],"%s",%i)}' %(year, msdShift, year,msdShift))
    evtColumns.Add("correctedMSD",'RVec<float> {jmrSmearer.smearMsd(%s),jmrSmearer.smearMsd(%s)}'%(smearString1,smearString2))

evtColumns.Add("FatJet_pt0","{0}[0]".format(ptVar))
evtColumns.Add("FatJet_pt1","{0}[1]".format(ptVar))
evtColumns.Add("FatJet_eta0","FatJet_eta[0]")
evtColumns.Add("FatJet_eta1","FatJet_eta[1]")
evtColumns.Add("FatJet_phi0","FatJet_phi[0]")
evtColumns.Add("FatJet_phi1","FatJet_phi[1]")
evtColumns.Add("mSD0","correctedMSD[0]")
evtColumns.Add("mSD1","correctedMSD[1]")

a.Apply([evtColumns])

a.Cut("mSD0Cut","mSD0>60")
a.Cut("mSD1Cut","mSD1>60")


nmSD = getNweighted(a,isData)


if(year=="2016"):
    a.Cut("pT","FatJet_pt0>350 && FatJet_pt1>350")
else:
    a.Cut("pT","FatJet_pt0>450 && FatJet_pt1>450")

npT = getNweighted(a,isData)


a.Define("nEle","nElectrons(nElectron,Electron_cutBased,0,Electron_pt,20,Electron_eta)")
#0:fail,1:veto,2:loose,3:medium,4:tight
#condition is, cutBased>cut
a.Define("nMu","nMuons(nMuon,Muon_looseId,Muon_pfIsoId,0,Muon_pt,20,Muon_eta)")
#1=PFIsoVeryLoose, 2=PFIsoLoose, 3=PFIsoMedium, 4=PFIsoTight, 5=PFIsoVeryTight, 6=PFIsoVeryVeryTight
#condition is, pfIsoId>cut
a.Cut("LeptonVeto","nMu==0 && nEle==0")
nLeptonVeto = getNweighted(a,isData)

# h_pt0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_pt0_jetSel'.format(options.process),';Leading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt0","genWeight")
# h_pt1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_pt1_jetSel'.format(options.process),';Subleading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt1","genWeight")
# h_eta0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_eta0_jetSel'.format(options.process),';Leading AK8 jet eta;Jets/0.1;',100,-2.5,2.5),"FatJet_eta0","genWeight")
# h_eta1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_eta1_jetSel'.format(options.process),';Subleading AK8 jet eta;Jets/0.1;',100,-2.5,2.5),"FatJet_eta1","genWeight")
# h_phi0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_phi0_jetSel'.format(options.process),';Leading AK8 jet eta;Jets/0.1;',160,-4,4),"FatJet_phi0","genWeight")
# h_phi1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_phi1_jetSel'.format(options.process),';Subleading AK8 jet eta;Jets/0.1;',160,-4,4),"FatJet_phi1","genWeight")
# histos.append(h_pt0)
# histos.append(h_pt1)
# histos.append(h_eta0)
# histos.append(h_eta1)



#need to define variables which we want in n-1 histograms
dijetColumns = VarGroup("dijet Columns")
dijetColumns.Add("DeltaEta","abs(FatJet_eta[0] - FatJet_eta[1])")
dijetColumns.Add('LeadingVector', 'analyzer::TLvector(FatJet_pt0,FatJet_eta[0],FatJet_phi[0],mSD0)')
dijetColumns.Add('SubleadingVector',  'analyzer::TLvector(FatJet_pt1,FatJet_eta[1],FatJet_phi[1],mSD1)')
dijetColumns.Add('MJJ',     'analyzer::invariantMass(LeadingVector,SubleadingVector)') 

a.Apply([dijetColumns])

nm1Cuts = CutGroup('Preselection')
nm1Cuts.Add("DeltaEta_cut","DeltaEta < 1.3")
nm1Cuts.Add("MJJ_cut","MJJ > 700")

nminusOneNodes = a.Nminus1(nm1Cuts) # NOTE: Returns the nodes with N-1 selections
nminusOneHists = HistGroup('nminus1Hists') # NOTE: HistGroup used to batch operate on histograms

nMinusOneLimits = {"DeltaEta":[0.,5.0,100],"MJJ":[0.,3000.,30]}#[xMin,xMax,nBins]
beforeNM1checkpoint = a.GetActiveNode()
# Add hists to group and write out at the end
for nkey in nminusOneNodes.keys():
    #print(nkey)
    if nkey == 'full': continue
    var = nkey.replace('_cut','').replace('minus_','')
    hist = nminusOneNodes[nkey].DataFrame.Histo1D(("{0}_nm1_{1}".format(options.process,var),"nMinusOne {0}".format(var),nMinusOneLimits[var][2],nMinusOneLimits[var][0],nMinusOneLimits[var][1]),var,"genWeight")
    nminusOneHists.Add(var,hist)

#Not applying delta eta, it will be applied later
a.SetActiveNode(beforeNM1checkpoint)
a.Cut("MJJ_cut","MJJ>700")
nMJJ = getNweighted(a,isData)


if(year=="2016"):
    #Pnet_v0
    a.Define("pnet0","FatJet_ParticleNetMD_probXbb[0]/(FatJet_ParticleNetMD_probXbb[0]+FatJet_ParticleNetMD_probQCDb[0]+FatJet_ParticleNetMD_probQCDbb[0]+FatJet_ParticleNetMD_probQCDc[0]+FatJet_ParticleNetMD_probQCDcc[0]+FatJet_ParticleNetMD_probQCDothers[0])")
    a.Define("pnet1","FatJet_ParticleNetMD_probXbb[1]/(FatJet_ParticleNetMD_probXbb[1]+FatJet_ParticleNetMD_probQCDb[1]+FatJet_ParticleNetMD_probQCDbb[1]+FatJet_ParticleNetMD_probQCDc[1]+FatJet_ParticleNetMD_probQCDcc[1]+FatJet_ParticleNetMD_probQCDothers[1])")
else:
    #Pnet_v1
    a.Define("pnet0","FatJet_particleNetMD_Xbb[0]/(FatJet_particleNetMD_Xbb[0]+FatJet_particleNetMD_QCD[0])")
    a.Define("pnet1","FatJet_particleNetMD_Xbb[1]/(FatJet_particleNetMD_Xbb[1]+FatJet_particleNetMD_QCD[1])")

a.Define("pnetLow","particleNetLow(pnet0,pnet1)")
a.Define("pnetHigh","particleNetHigh(pnet0,pnet1)")
h_nm1_pnet0     = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnet0'.format(options.process),';Leading jet ParticleNet score;Events/0.01;',1000,0,1),"pnet0","genWeight")
h_nm1_pnet1     = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnet1'.format(options.process),';Subleading jet ParticleNet score;Events/0.01;',1000,0,1),"pnet1","genWeight")
h_nm1_pnetLow   = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnetLow'.format(options.process),';Lower ParticleNet score;Events/0.01;',1000,0,1),"pnetLow","genWeight")
h_nm1_pnetHigh  = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnetHigh'.format(options.process),';Higher ParticleNet score;Events/0.01;',1000,0,1),"pnetHigh","genWeight")
h_nm1_pt0       = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pt0'.format(options.process),';Leading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt0","genWeight")
h_nm1_pt1       = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pt1'.format(options.process),';Subleading AK8 jet pT;Jets/10 GeV;',300,0,3000),"FatJet_pt1","genWeight")
h_nm1_eta0      = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_eta0'.format(options.process),';Leading AK8 jet eta;Jets/0.05;',100,-2.5,2.5),"FatJet_eta0","genWeight")
h_nm1_eta1      = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_eta1'.format(options.process),';Subleading AK8 jet eta;Jets/0.05;',100,-2.5,2.5),"FatJet_eta1","genWeight")
h_nm1_phi0      = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_phi0'.format(options.process),';Leading AK8 jet phi;Jets/0.05;',160,-4,4),"FatJet_phi0","genWeight")
h_nm1_phi1      = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_phi1'.format(options.process),';Subleading AK8 jet phi;Jets/0.05;',160,-4,4),"FatJet_phi1","genWeight")


histos.append(h_nm1_pnet1)
histos.append(h_nm1_pnet0)
histos.append(h_nm1_pnetLow)
histos.append(h_nm1_pnetHigh)
histos.append(h_nm1_pt0)
histos.append(h_nm1_pt1)
histos.append(h_nm1_eta0)
histos.append(h_nm1_eta1)
histos.append(h_nm1_phi0)
histos.append(h_nm1_phi1)

idxColumns = VarGroup("idxColumns")
idxColumns.Add("idxH","higgsMassMatching(mSD0,mSD1)")#randomize ambiguous cases
#idxColumns.Add("idxH","higgsMassMatchingAlternative(mSD0,mSD1)")#choose one closer to
idxColumns.Add("idxY","1-idxH")
idxCuts   = CutGroup("idxCuts")
idxCuts.Add("Higgs-tagged cut","idxH>=0")
a.Apply([idxColumns])
a.Apply([idxCuts])
nHiggs = getNweighted(a,isData)

candidateColumns  = VarGroup("candidateColumns")
candidateColumns.Add('ptjH','{0}[idxH]'.format(ptVar))
candidateColumns.Add('ptjY','{0}[idxY]'.format(ptVar))

candidateColumns.Add('MJY','correctedMSD[idxY]')
candidateColumns.Add('MJH','correctedMSD[idxH]')
candidateColumns.Add('MJJ_halfReduced','MJJ - MJH + 125')

if(year=="2016"):
    #Pnet_v0
    candidateColumns.Add("pnetH","FatJet_ParticleNetMD_probXbb[idxH]/(FatJet_ParticleNetMD_probXbb[idxH]+FatJet_ParticleNetMD_probQCDb[idxH]+FatJet_ParticleNetMD_probQCDbb[idxH]+FatJet_ParticleNetMD_probQCDc[idxH]+FatJet_ParticleNetMD_probQCDcc[idxH]+FatJet_ParticleNetMD_probQCDothers[idxH])")
    candidateColumns.Add("pnetY","FatJet_ParticleNetMD_probXbb[idxY]/(FatJet_ParticleNetMD_probXbb[idxY]+FatJet_ParticleNetMD_probQCDb[idxY]+FatJet_ParticleNetMD_probQCDbb[idxY]+FatJet_ParticleNetMD_probQCDc[idxY]+FatJet_ParticleNetMD_probQCDcc[idxY]+FatJet_ParticleNetMD_probQCDothers[idxY])")
else:
    #Pnet_v1
    candidateColumns.Add("pnetH","FatJet_particleNetMD_Xbb[idxH]/(FatJet_particleNetMD_Xbb[idxH]+FatJet_particleNetMD_QCD[idxH])")
    candidateColumns.Add("pnetY","FatJet_particleNetMD_Xbb[idxY]/(FatJet_particleNetMD_Xbb[idxY]+FatJet_particleNetMD_QCD[idxY])")


a.Apply([candidateColumns])

h_pnet_pT_H = a.GetActiveNode().DataFrame.Histo2D(('{0}_pnet_pT_H'.format(options.process),'ParticleNet vs pT Y;ParticleNet_H score ;pT_H [GeV];',100,0,1,300,0,3000),'pnetH','ptjH',"genWeight")
h_pnet_pT_Y = a.GetActiveNode().DataFrame.Histo2D(('{0}_pnet_pT_Y'.format(options.process),'ParticleNet vs pT Y;ParticleNet_Y score ;pT_Y [GeV];',100,0,1,300,0,3000),'pnetY','ptjY',"genWeight")
histos.append(h_pnet_pT_Y)
histos.append(h_pnet_pT_H)

h_ptjY = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY'.format(options.process),'FatJetY pt;pT_Y [GeV];Events/10 GeV;',300,0,3000),'ptjY',"genWeight")
h_ptjH = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH'.format(options.process),'FatJetY pt;pT_H [GeV];Events/10 GeV;',300,0,3000),'ptjH',"genWeight")
h_MJY = a.GetActiveNode().DataFrame.Histo1D(('{0}_MJY'.format(options.process),'FatJetY mSD;mSD_Y [GeV];Events/10 GeV;',60,30,630),'MJY',"genWeight")
h_MJH = a.GetActiveNode().DataFrame.Histo1D(('{0}_MJH'.format(options.process),'FatJetH mSD;mSD_H [GeV];Events/10 GeV;',60,30,630),'MJH',"genWeight")
h_idxY = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxY'.format(options.process),'idxY',5,-1,4),'idxY',"genWeight")
h_idxH = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxH'.format(options.process),'idxH',5,-1,4),'idxH',"genWeight")
histos.append(h_ptjY)
histos.append(h_ptjH)
histos.append(h_MJY)
histos.append(h_MJH)
histos.append(h_idxY)
histos.append(h_idxH)

checkpoint  = a.GetActiveNode()
#-----Trigger study part------
#Separated from the rest of the cut tree
# if(isData):
if(varName=="nom"):
    baselineTrigger="HLT_PFJet260"
    a.SetActiveNode(beforeTrigCheckpoint)
    a.Cut("Baseline",baselineTrigger)
    if(isData):
        a.Cut("MET For Trigger",MetFiltersString)
    #need to change names to create nodes with different names than already existing
    a.Cut("nFatJet_ForTrigger","nFatJet>1")
    a.Cut("Eta_ForTrigger","abs(FatJet_eta[0])<2.4 && abs(FatJet_eta[1])<2.4")
    evtColumns.name = "Event Columns For Trigger"
    a.Apply([evtColumns])
    if(year=="2016"):
        a.Cut("pT_ForTrigger","FatJet_pt0>350 && FatJet_pt1>350")
    else:
        a.Cut("pT_ForTrigger","FatJet_pt0>450 && FatJet_pt1>450")
    nJets = getNweighted(a,isData)

    dijetColumns.name = "NminusOne Columns For Trigger"
    candidateColumns.name = "candidateColumns For Trigger"
    idxColumns.name = "idxColumns For Trigger"
    idxCuts.name = "idxCuts For Trigger"
    a.Apply([dijetColumns,idxColumns,idxCuts,candidateColumns])
    a.Cut("MJJ_cut_trigger","MJJ>700")
    a.Cut("MJY_cut_trigger","MJY>60")
    triggersStringAll = a.GetTriggerString(triggerList)  

    DEtaStrings = ["DeltaEta>0","DeltaEta<1.3","DeltaEta>1.5"]
    DEtaRegions = ["incl","SR","SB"]
    detaCheckpoint  = a.GetActiveNode()
    for i, tag in enumerate(DEtaRegions):
        a.SetActiveNode(detaCheckpoint)
        a.Cut("deta_{0}".format(tag),DEtaStrings[i])

        h_noTriggers = a.GetActiveNode().DataFrame.Histo2D(('{0}_noTriggers_{1}'.format(options.process,tag),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,700,3200,26,60,320),'MJJ','MJY',"genWeight")
        h_pT0noTriggers = a.GetActiveNode().DataFrame.Histo1D(('{0}_pT0noTriggers_{1}'.format(options.process,tag),';Leading jet pT [GeV]; Events/10 GeV;',180,200,2000),"FatJet_pt0","genWeight")
        h_pT1noTriggers = a.GetActiveNode().DataFrame.Histo1D(('{0}_pT1noTriggers_{1}'.format(options.process,tag),';Subleading jet pT [GeV]; Events/10 GeV;',180,200,2000),"FatJet_pt1","genWeight")
        a.Cut("triggers_{0}".format(tag),triggersStringAll)
        h_triggersAll = a.GetActiveNode().DataFrame.Histo2D(('{0}_triggersAll_{1}'.format(options.process,tag),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,700,3200,26,60,320),'MJJ','MJY',"genWeight")
        h_pT0triggersAll = a.GetActiveNode().DataFrame.Histo1D(('{0}_pT0triggersAll_{1}'.format(options.process,tag),';Leading jet pT [GeV]; Events/10 GeV;',180,200,2000),"FatJet_pt0","genWeight")
        h_pT1triggersAll = a.GetActiveNode().DataFrame.Histo1D(('{0}_pT1triggersAll_{1}'.format(options.process,tag),';Subleading jet pT [GeV]; Events/10 GeV;',180,200,2000),"FatJet_pt1","genWeight")

        histos.append(h_noTriggers)
        histos.append(h_pT0noTriggers)
        histos.append(h_pT1noTriggers)
        histos.append(h_triggersAll)
        histos.append(h_pT0triggersAll)
        histos.append(h_pT1triggersAll)

    #return to event selection
    a.SetActiveNode(checkpoint)
#-----Trigger study part end------

#Categorize TT jets
if("TTbar" in options.process):
    a.Define("jetCatH","classifyProbeJet(idxH, FatJet_phi, FatJet_eta, nGenPart, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
    a.Define("jetCatY","classifyProbeJet(idxY, FatJet_phi, FatJet_eta, nGenPart, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")


snapshotColumns = ["pnetH","pnetY","MJJ","MJY","MJH","DeltaEta","PV_npvsGood"]

#HEM drop
if(isData):
    if(year=="2018" and not "2018A" in options.process):
        a.Define("Jet0_HEM","FatJet_phi[0]>-1.57 && FatJet_phi[0]<-0.8 && FatJet_eta[0]<-1.3")
        a.Define("Jet1_HEM","FatJet_phi[1]>-1.57 && FatJet_phi[1]<-0.8 && FatJet_eta[1]<-1.3")
        a.Define("HEMflag","run>319076 && (Jet0_HEM || Jet1_HEM)")
        a.Cut("HEMcut","HEMflag<1")
else:
    if(year=="2018"):
        a.Define("Jet0_HEM","FatJet_phi[0]>-1.57 && FatJet_phi[0]<-0.8 && FatJet_eta[0]<-1.3")
        a.Define("Jet1_HEM","FatJet_phi[1]>-1.57 && FatJet_phi[1]<-0.8 && FatJet_eta[1]<-1.3")
        a.Define("HEMflag","Jet0_HEM || Jet1_HEM")
        a.Define("HEMweight","HEMweightMC(HEMflag)")        
        snapshotColumns.append("HEMweight")

outputFile = options.output.replace(".root","_{0}.root".format(varName))

if not isData:
    snapshotColumns = ["pnetH","pnetY","MJJ","MJY","MJH","DeltaEta","PV_npvsGood","nFatJet","FatJet_hadronFlavour","ptjH","ptjY","genWeight","Pileup_nTrueInt"]
    if("TTbar" in options.process):
        snapshotColumns.append("MTT")
        snapshotColumns.append("topPt")
        snapshotColumns.append("antitopPt")
        snapshotColumns.append("jetCatH")
        snapshotColumns.append("jetCatY")
opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
opts.fLazy = False
a.GetActiveNode().DataFrame.Snapshot("Events",outputFile,snapshotColumns,opts)

cutFlowVars = [nProc,nSkimmed,nTrig,nJetID,nEta,nmSD,npT,nLeptonVeto,nMJJ,nHiggs]
cutFlowLabels = ["Processed","Skimmed","Trigger","JetID","Eta","mSD","pT","Lepton Veto","MJJ","Higgs mass","DeltaEta","TT","LL","L_AL","AL_T","AL_L","AL_AL"]#tagging bins will be filled out in template making
nCutFlowlabels = len(cutFlowLabels)
hCutFlow = ROOT.TH1F('{0}_cutflow'.format(options.process),"Number of events after each cut",nCutFlowlabels,0.5,nCutFlowlabels+0.5)
for i,label in enumerate(cutFlowLabels):
    hCutFlow.GetXaxis().SetBinLabel(i+1, label)

for i,var in enumerate(cutFlowVars):
    hCutFlow.AddBinContent(i+1,var)

histos.append(hCutFlow)


out_f = ROOT.TFile(outputFile,"UPDATE")
out_f.cd()
for h in histos:
    h.Write()
nminusOneHists.Do('Write')
out_f.Close()

#a.PrintNodeTree('node_tree.dot',verbose=True)
print("Total time: "+str((time.time()-start_time)/60.) + ' min')