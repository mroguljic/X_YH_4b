#To be used with trees from event selection
import ROOT as r
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
                default   =   'ttbarSemi',
                dest      =   'process',
                help      =   'Process in the given file')
parser.add_option('-v','--var', metavar='variation', type='string', action='store',
                default   =   "nom",
                dest      =   'variation',
                help      =   'jmrUp/Down, jmsUp/Down, jesUp/Down, jerUp/Down, sfUp/sfDown, trigUp/Down, isoUp/Down, IdUp/IdDown')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('-m', metavar='mode', type='string', action='store',
                default   =   "RECREATE",
                dest      =   'mode',
                help      =   'RECREATE or UPDATE outputfile')

(options, args) = parser.parse_args()
#SF and JES/R have their own event trees
iFile = options.input
variation = options.variation
year = options.year
if ("je" in variation and not variation in iFile):
        iFile = iFile.replace(".root","_{0}.root".format(variation))
        print("{0} not in {1}, swapping input to {2}".format(variation,options.input,iFile))
elif ("sf" in variation and not variation in iFile):
        iFile = iFile.replace(".root","_{0}.root".format(variation))
        print("{0} not in {1}, swapping input to {2}".format(variation,options.input,iFile))
else:
    if not("nom" in iFile):
        iFile = iFile.replace(".root","_nom.root")

a = analyzer(iFile)

if("data" in options.process or "SingleMuon" in options.process):
    isData=True
else:
    isData=False

histos =[]


if("jm" in variation):
    probeJetMassVar = "probeJetMass_{0}".format(variation)
else:
    probeJetMassVar = "probeJetMass_nom"

if(year=="2016"):
    #SFs are split into B-F and G-H era with respective lumis 19.961 and 16.217
    IdFile1   = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2016_preVFP_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ID.root"   
    IdName1   = "NUM_MediumID_DEN_TrackerMuons_abseta_pt"
    IdFile2   = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2016_postVFP_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2016_UL_ID.root"   
    IdName2   = "NUM_MediumID_DEN_TrackerMuons_abseta_pt"
    IsoFile1  = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2016_postVFP_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2016_UL_ISO.root"
    IsoName1  = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt"
    IsoFile2  = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2016_preVFP_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2016_UL_HIPM_ISO.root"
    IsoName2  = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt"
    TrigFile1 = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesAndSF_RunBtoF.root"
    TrigName1 = "IsoMu24_OR_IsoTkMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
    TrigFile2 = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesAndSF_Period4.root"
    TrigName2 = "IsoMu24_OR_IsoTkMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
    lumiBCDEF = 19.961
    lumiGH    = 16.227
elif(year=="2017"):
    IdFile    = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2017_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root"
    IdName    = "NUM_MediumID_DEN_TrackerMuons_abseta_pt"
    IsoFile   = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2017_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root"
    IsoName   = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt"
    TrigFile  = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root"
    TrigName  = "IsoMu27_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
elif(year=="2018"):
    IdFile    = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2018_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root"
    IdName    = "NUM_MediumID_DEN_TrackerMuons_abseta_pt"    
    IsoFile   = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2018_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root"
    IsoName   = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt"
    TrigFile1 = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_2018_trigger_EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root"
    TrigName1 = "IsoMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
    TrigFile2 = "TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_2018_trigger_EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root"
    TrigName2 = "IsoMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
    lumiBefore= 8.950
    lumiAfter = 50.789

if not isData:
    if(year=="2016"):
        IdCorr      = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile1),'"{0}"'.format(IdName1),'"{0}"'.format(IdFile2),'"{0}"'.format(IdName2),'{0}'.format(lumiBCDEF/(lumiBCDEF+lumiGH)),'{0}'.format(lumiGH/(lumiBCDEF+lumiGH))],corrtype='weight',mainFunc="evalComb")
        IsoCorr     = Correction('IsoSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IsoFile1),'"{0}"'.format(IsoName1),'"{0}"'.format(IsoFile2),'"{0}"'.format(IsoName2),'{0}'.format(lumiBCDEF/(lumiBCDEF+lumiGH)),'{0}'.format(lumiGH/(lumiBCDEF+lumiGH))],corrtype='weight',mainFunc="evalComb")
        TriggerCorr = Correction('TriggerEff',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(TrigFile1),'"{0}"'.format(TrigName1),'"{0}"'.format(TrigFile2),'"{0}"'.format(TrigName2),'{0}'.format(lumiBCDEF/(lumiBCDEF+lumiGH)),'{0}'.format(lumiGH/(lumiBCDEF+lumiGH))],corrtype='weight',mainFunc="evalComb")
    elif(year=="2017"):
        IdCorr      = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile),'"{0}"'.format(IdName)],corrtype='weight')
        IsoCorr     = Correction('IsoSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IsoFile),'"{0}"'.format(IsoName)],corrtype='weight')
        TriggerCorr = Correction('TriggerEff',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(TrigFile),'"{0}"'.format(TrigName)],corrtype='weight')
    elif(year=="2018"):
        IdCorr      = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile),'"{0}"'.format(IdName)],corrtype='weight')
        IsoCorr     = Correction('IsoSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IsoFile),'"{0}"'.format(IsoName)],corrtype='weight')
        TriggerCorr = Correction('TriggerEff',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(TrigFile1),'"{0}"'.format(TrigName1),'"{0}"'.format(TrigFile2),'"{0}"'.format(TrigName2),'{0}'.format(lumiBefore/(lumiBefore+lumiAfter)),'{0}'.format(lumiAfter/(lumiBefore+lumiAfter))],corrtype='weight',mainFunc="evalComb")
    
    STcorr = Correction('STcorr',"TIMBER/Framework/src/ST_weight.cc",constructor=[ '-0.0002532','1.1789'],corrtype='weight')
    a.AddCorrection(STcorr,evalArgs={'ST':'ST'})
    a.AddCorrection(IdCorr,evalArgs={'pt':'lPt','eta':'lEta'})
    a.AddCorrection(IsoCorr,evalArgs={'pt':'lPt','eta':'lEta'})
    a.AddCorrection(TriggerCorr,evalArgs={'pt':'lPt','eta':'lEta'})
    a.MakeWeightCols('noSTCorr',dropList=["STcorr"])

hSTBefore = a.DataFrame.Histo1D(('{0}_STbefore_I'.format(options.process),';ST [GeV];Events/100;',20,0,2000),"ST","weight_noSTCorr__nominal")
histos.append(hSTBefore)
a.MakeWeightCols()

weightString = "weight__nominal"
if(variation=="isoUp"):
    weightString = "IsoSF__up"
elif(variation=="isoDown"):
    weightString = "IsoSF__down"
elif(variation=="IdUp"):
    weightString = "Id__up"
elif(variation=="IdDown"):
    weightString = "Id__down"
elif(variation=="trigUp"):
    weightString = "TriggerEff__up"
elif(variation=="trigDown"):
    weightString = "TriggerEff__down"


pnetHi = 0.95
pnetLo = 0.80
pnetCuts = ["probeJetPNet>{0}".format(pnetHi),"probeJetPNet>{0} && probeJetPNet<{1}".format(pnetLo,pnetHi),"probeJetPNet>-0.001"]
pnetTags = ["T","L","I"]

beforePnet = a.GetActiveNode()
for i in range(len(pnetCuts)):
    a.SetActiveNode(beforePnet)
    a.Cut("{0}_cut".format(pnetTags[i]),pnetCuts[i])

    hMET = a.DataFrame.Histo1D(('{0}_MET_{1}'.format(options.process,pnetTags[i]),';MET [GeV];Events/100 GeV;',20,0,2000),"MET_pt")
    hHT = a.DataFrame.Histo1D(('{0}_HT_{1}'.format(options.process,pnetTags[i]),';HT [GeV];Events/100;',20,0,2000),"HT")
    hST = a.DataFrame.Histo1D(('{0}_ST_{1}'.format(options.process,pnetTags[i]),';ST [GeV];Events/100;',20,0,2000),"ST")
    hPt = a.DataFrame.Histo1D(('{0}_lepton_pT_{1}'.format(options.process,pnetTags[i]),';pT [GeV];Events/100;',20,0,2000),"lPt")

    histos.append(hMET)
    histos.append(hHT)
    histos.append(hST)
    histos.append(hPt)

    if not isData:
        checkpoint = a.GetActiveNode()
        hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        histos.append(hMassInclusive)

        a.Cut("bqq_{0}".format(pnetTags[i]),"partonCategory==3")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_bqq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutbqq_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_bqq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutbqq_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_bqq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        a.SetActiveNode(checkpoint)

        a.Cut("bq_{0}".format(pnetTags[i]),"partonCategory==2")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_bq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutbq_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_bq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutbq_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_bq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        a.SetActiveNode(checkpoint)

        a.Cut("qq_{0}".format(pnetTags[i]),"partonCategory==1")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_qq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutqq_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_qq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutqq_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_qq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)

        a.SetActiveNode(checkpoint)
        a.Cut("unmatched_{0}".format(pnetTags[i]),"partonCategory==0")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_unmatched_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutunm_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_unmatched_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutunm_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_unmatched_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        histos.append(hMassInclusive)
    else:
        hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCut_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCut_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),probeJetMassVar,weightString)
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)


in_f = ROOT.TFile(iFile)
#Grab cutflow histogram
for key in in_f.GetListOfKeys():
    h = key.ReadObj()
    hName = h.GetName()
    if(hName=="Events"):
        continue
    if("cutflow" in hName.lower()):
        h.SetDirectory(0)
        histos.append(h)


out_f = ROOT.TFile(options.output,options.mode)
out_f.cd()
for h in histos:
    h.SetName(h.GetName()+"_"+options.variation)
    h.Write()
out_f.Close()

