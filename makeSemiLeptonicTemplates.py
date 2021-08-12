#To be used with trees from event selection
import ROOT as r
import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *


TIMBERPATH = os.environ["TIMBERPATH"]


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
                help      =   'jmrUp/Down, jmsUp/Down, jesUp/Down, jerUp/Down, sfUp/sfDown, trigUp/Down, IdUp/IdDown')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('-m', metavar='mode', type='string', action='store',
                default   =   "RECREATE",
                dest      =   'mode',
                help      =   'RECREATE or UPDATE outputfile')
parser.add_option('-w', '--wp', metavar='working points',nargs=2, action="store", type=float,
                default   =   (0.94,0.98),
                dest      =   'wps',
                help      =   'Loose and tight working points')

(options, args) = parser.parse_args()
#SF and JES/R have their own event trees
iFile = options.input
variation = options.variation
year = options.year
if("electron" in iFile):
    channel = "e"
elif("muon" in iFile):
    channel = "mu"
else:
    print("WARNING: no lepton in file name, setting channel to mu")
    channel = "mu"

if ("je" in variation):
    if not variation in iFile:
        iFile = iFile.replace(".root","_{0}.root".format(variation))
        print("{0} not in {1}, swapping input to {2}".format(variation,options.input,iFile))
elif ("sf" in variation):
    if not variation in iFile:
        iFile = iFile.replace(".root","_{0}.root".format(variation))
        print("{0} not in {1}, swapping input to {2}".format(variation,options.input,iFile))
else:
    if not("nom" in iFile):
        iFile = iFile.replace(".root","_nom.root")

a = analyzer(iFile)

if("data" in options.process or "Single" in options.process or "EGamma" in options.process):
    isData=True
else:
    isData=False

histos =[]

if(channel=="mu"):
    CompileCpp("TIMBER/Framework/common.cc") 
    a.Define("muonFourVec","analyzer::TLvector(lPt,lEta,0.,0.1)")#pt, eta, phi, m. Phi is irrelevant for momentum 
    a.Define("muonP","muonFourVec.P()")

if("jm" in variation):
    # if("TTbar" in options.process and "jms" in options.variation):
    # #recalculate MJY according to pt-dependent jms for bqq
    #     probeJetMassVar = "probeJetMass_recalc"
    #     CompileCpp("TIMBER/Framework/src/JMSUncShifter.cc") 
    #     CompileCpp("JMSUncShifter jmsShifter = JMSUncShifter();") 
    #     if(options.variation=="jmsUp"):
    #         a.Define("probeJetMass_recalc","jmsShifter.ptDependentJMS(probeJetMass_jmsUp,probeJetPt,1,partonCategory)")
    #     elif(options.variation=="jmsDown"):
    #         a.Define("probeJetMass_recalc","jmsShifter.ptDependentJMS(probeJetMass_jmsDown,probeJetPt,-1,partonCategory)")
    #     else:
    #         print("JMS uncertainty unkown")
    #         sys.exit()
    # else:
    #     probeJetMassVar = "probeJetMass_{0}".format(variation)
    probeJetMassVar = "probeJetMass_{0}".format(variation)

else:
    probeJetMassVar = "probeJetMass_nom"

if(channel=="mu" and not isData):
#Setup muon-related SFs
    a.Define("absEta","abs(lEta)")
    if(year=="2016"):
        #SFs are split into B-F and G-H era with respective lumis 19.961 and 16.217
        IdFile    = TIMBERPATH+"TIMBER/data/OfficialSFs/2016_ReReco_muon_TightIsoTightID_SF.root"   
        IdName    = "TightID_TightRelISO_SF_eta_pt"
        TrigFile1 = TIMBERPATH+"TIMBER/data/OfficialSFs/EfficienciesAndSF_RunBtoF.root"
        TrigName1 = "IsoMu24_OR_IsoTkMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
        TrigFile2 = TIMBERPATH+"TIMBER/data/OfficialSFs/EfficienciesAndSF_Period4.root"
        TrigName2 = "IsoMu24_OR_IsoTkMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA"
        lumiBCDEF = 19.961
        lumiGH    = 16.227
    elif(year=="2017"):
        IdFile    = TIMBERPATH+"TIMBER/data/OfficialSFs/2017_UL_muon_TightIsoTightID_SF.root"
        IdName    = "TightID_TightRelISO_SF_eta_pt"
        TrigFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/EfficienciesStudies_UL2017_Trigger_rootfiles_Efficiencies_muon_generalTracks_Z_Run2017_UL_SingleMuonTriggers.root"
        TrigName  = "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt_efficiencyData"
        RecoFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/MuonRecoEfficiencies/UL_17_18_Muon_RecoSF.root"
        RecoName  = "reco_sf_17"
    elif(year=="2018"):
        IdFile    = TIMBERPATH+"TIMBER/data/OfficialSFs/2018_UL_muon_TightIsoTightID_SF.root"
        IdName    = "TightID_TightRelISO_SF_eta_pt"    
        TrigFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/EfficienciesStudies_UL2018_Trigger_rootfiles_Efficiencies_muon_generalTracks_Z_Run2018_UL_SingleMuonTriggers.root"
        TrigName  = "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt_efficiencyData"
        RecoFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/MuonRecoEfficiencies/UL_17_18_Muon_RecoSF.root"
        RecoName  = "reco_sf_18"
        #lumiBefore= 8.950
        #lumiAfter = 50.789

    puCorr = Correction('puReweighting',"TIMBER/Framework/src/puWeight.cc",constructor=['"../TIMBER/TIMBER/data/pileup/PUweights_{0}.root"'.format(year)],corrtype='weight')
    if(year=="2016"):
        IdCorr      = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile),'"{0}"'.format(IdName)],corrtype='weight')
        TriggerCorr = Correction('TriggerEff',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(TrigFile1),'"{0}"'.format(TrigName1),'"{0}"'.format(TrigFile2),'"{0}"'.format(TrigName2),'{0}'.format(lumiBCDEF/(lumiBCDEF+lumiGH)),'{0}'.format(lumiGH/(lumiBCDEF+lumiGH))],corrtype='weight',mainFunc="evalComb")
    elif(year=="2017"):
        IdCorr      = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile),'"{0}"'.format(IdName)],corrtype='weight')
        TriggerCorr = Correction('TriggerEff',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(TrigFile),'"{0}"'.format(TrigName)],corrtype='weight')
        RecoCorr    = Correction('RecoSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(RecoFile),'"{0}"'.format(RecoName)],corrtype='weight')
    elif(year=="2018"):
        IdCorr      = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile),'"{0}"'.format(IdName)],corrtype='weight')
        TriggerCorr = Correction('TriggerEff',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(TrigFile),'"{0}"'.format(TrigName)],corrtype='weight')
        RecoCorr    = Correction('RecoSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(RecoFile),'"{0}"'.format(RecoName)],corrtype='weight')

    a.AddCorrection(puCorr, evalArgs={'puTrue':'Pileup_nTrueInt'})
    a.AddCorrection(TriggerCorr,evalArgs={'pt':'lPt','eta':'absEta'})
    if(year=="2016"):
        a.AddCorrection(IdCorr,evalArgs={'pt':'lPt','eta':'lEta'})
    else:
        a.AddCorrection(IdCorr,evalArgs={'pt':'lPt','eta':'absEta'})
        a.AddCorrection(RecoCorr,evalArgs={'pt':'muonP','eta':'absEta'})

if(channel=="e" and not isData):
    TrigFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/SingleElectronEfficiencies.root"
    TrigName  = "ele_eff_{0}".format(year)
    IdName    = "EGamma_SF2D"
    RecoName  = "EGamma_SF2D"#sf histo has same name as ID
    if(year=="2016"):
        IdFile    = TIMBERPATH+"TIMBER/data/OfficialSFs/2016LegacyReReco_ElectronTight_Fall17V2.root"   
        RecoFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/EleRecoEfficiencies/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root"   
    elif(year=="2017"):
        IdFile    = TIMBERPATH+"TIMBER/data/OfficialSFs/egammaEffi.txt_EGM2D_Tight_UL17.root"   
        RecoFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/EleRecoEfficiencies/egammaEffi_ptAbove20.txt_EGM2D_UL2017.root"   
    elif(year=="2018"):
        #https://twiki.cern.ch/twiki/bin/view/CMS/EgammaUL2016To2018
        IdFile    = TIMBERPATH+"TIMBER/data/OfficialSFs/egammaEffi.txt_Ele_Tight_EGM2D.root"   
        RecoFile  = TIMBERPATH+"TIMBER/data/OfficialSFs/EleRecoEfficiencies/egammaEffi_ptAbove20.txt_EGM2D_UL2018.root"   

    #ID and ISO are both in cut-based WP so only one SF
    IdCorr        = Correction('IdSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(IdFile),'"{0}"'.format(IdName)],corrtype='weight')
    RecoCorr      = Correction('RecoSF',"TIMBER/Framework/src/TH2_SF.cc",constructor=['"{0}"'.format(RecoFile),'"{0}"'.format(RecoName)],corrtype='weight')
    puCorr        = Correction('puReweighting',"TIMBER/Framework/src/puWeight.cc",constructor=['"../TIMBER/TIMBER/data/pileup/PUweights_{0}.root"'.format(year)],corrtype='weight')
    TriggerCorr   = Correction('TriggerEff',"TIMBER/Framework/src/SingleETriggerEfficiency.cc",constructor=['"{0}"'.format(TrigFile),'"{0}"'.format(TrigName)],corrtype='weight')
    #Add trigger

    a.AddCorrection(IdCorr,evalArgs={'pt':'lPt','eta':'lEta'})
    a.AddCorrection(RecoCorr,evalArgs={'pt':'lPt','eta':'lEta'})
    a.AddCorrection(puCorr, evalArgs={'puTrue':'Pileup_nTrueInt'})
    a.AddCorrection(TriggerCorr,evalArgs={'pt':'lPt','eta':'lEta'})

if("TTbar" in options.process):
    ptrwtCorr = Correction('topPtReweighting',"TIMBER/Framework/src/TopPt_reweighting.cc",corrtype='weight')
    a.AddCorrection(ptrwtCorr, evalArgs={'genTPt':'topPt','genTbarPt':'antitopPt'})

a.MakeWeightCols()

weightString = "weight__nominal"
if(variation=="IdUp"):
    weightString = "weight__IdSF_up"
elif(variation=="IdDown"):
    weightString = "weight__IdSF_down"
elif(variation=="trigUp"):
    weightString = "weight__TriggerEff_up"
elif(variation=="trigDown"):
    weightString = "weight__TriggerEff_down"
elif(variation=="ptRwtUp"):
    weightString = "weight__topPtReweighting_up"
elif(variation=="ptRwtDown"):
    weightString = "weight__topPtReweighting_down"
elif(variation=="puRwtUp"):
    weightString = "weight__puReweighting_up"
elif(variation=="puRwtDown"):
    weightString = "weight__puReweighting_down"

print("Using weight string ", weightString)

if isData:
    a.Define("genWeight","1")

if(year=="2018"):
    #a.Define("evtWeight","genWeight*HEMweight*{0}".format(weightString)) #uncomment when trees with HEM weights are calculated
    a.Define("evtWeight","genWeight*{0}".format(weightString))
else:
    a.Define("evtWeight","genWeight*{0}".format(weightString))

pnetHi = options.wps[1]
pnetLo = options.wps[0]
pnetCuts = ["probeJetPNet>{0}".format(pnetHi),"probeJetPNet>{0} && probeJetPNet<{1}".format(pnetLo,pnetHi),"probeJetPNet>-0.001","probeJetPNet>-0.001 && probeJetPNet<{0}".format(pnetLo)]
pnetTags = ["T","L","I","AT"]


if(year=="2018" or year=="2017"):
    a.Cut("probjeJetPtCut","probeJetPt>450")


beforePnet = a.GetActiveNode()
for i in range(len(pnetCuts)):
    a.SetActiveNode(beforePnet)
    a.Cut("{0}_cut".format(pnetTags[i]),pnetCuts[i])

    hMET    = a.DataFrame.Histo1D(('{0}_MET_{1}'.format(options.process,pnetTags[i]),';MET [GeV];Events/100 GeV;',20,0,2000),"METpt","evtWeight")
    hMETphi = a.DataFrame.Histo1D(('{0}_METphi_{1}'.format(options.process,pnetTags[i]),';MET phi;Events/0.1;',80,-4.,4.),"METphi","evtWeight")
    hHT     = a.DataFrame.Histo1D(('{0}_HT_{1}'.format(options.process,pnetTags[i]),';HT [GeV];Events/100;',20,0,2000),"HT","evtWeight")
    hST     = a.DataFrame.Histo1D(('{0}_ST_{1}'.format(options.process,pnetTags[i]),';ST [GeV];Events/100;',30,0,3000),"ST","evtWeight")
    hPt     = a.DataFrame.Histo1D(('{0}_lepton_pT_{1}'.format(options.process,pnetTags[i]),';pT [GeV];Events/100;',20,0,2000),"lPt","evtWeight")

    histos.append(hMET)
    histos.append(hMETphi)
    histos.append(hHT)
    histos.append(hST)
    histos.append(hPt)

    
    if not isData:
        checkpoint = a.GetActiveNode()
        hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        histos.append(hMassInclusive)

        a.Cut("bqq_{0}".format(pnetTags[i]),"partonCategory==3")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_bqq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutbqq_{0}".format(pnetTags[i]),"probeJetPt<600 && probeJetPt>300").DataFrame.Histo1D(('{0}_bqq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutbqq_{0}".format(pnetTags[i]),"probeJetPt>600").DataFrame.Histo1D(('{0}_bqq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        a.SetActiveNode(checkpoint)

        a.Cut("bq_{0}".format(pnetTags[i]),"partonCategory==2")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_bq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutbq_{0}".format(pnetTags[i]),"probeJetPt<600 && probeJetPt>300").DataFrame.Histo1D(('{0}_bq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutbq_{0}".format(pnetTags[i]),"probeJetPt>600").DataFrame.Histo1D(('{0}_bq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        a.SetActiveNode(checkpoint)

        a.Cut("qq_{0}".format(pnetTags[i]),"partonCategory==1")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_qq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutqq_{0}".format(pnetTags[i]),"probeJetPt<600 && probeJetPt>300").DataFrame.Histo1D(('{0}_qq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutqq_{0}".format(pnetTags[i]),"probeJetPt>600").DataFrame.Histo1D(('{0}_qq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)

        a.SetActiveNode(checkpoint)
        a.Cut("unmatched_{0}".format(pnetTags[i]),"partonCategory==0")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_unmatched_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutunm_{0}".format(pnetTags[i]),"probeJetPt<600 && probeJetPt>300").DataFrame.Histo1D(('{0}_unmatched_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutunm_{0}".format(pnetTags[i]),"probeJetPt>600").DataFrame.Histo1D(('{0}_unmatched_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
    else:
        hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCut_{0}".format(pnetTags[i]),"probeJetPt<600 && probeJetPt>300").DataFrame.Histo1D(('{0}_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCut_{0}".format(pnetTags[i]),"probeJetPt>600").DataFrame.Histo1D(('{0}_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',14,60,200),probeJetMassVar,"evtWeight")
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
    h.SetDirectory(0)
    histos.append(h)

out_f = ROOT.TFile(options.output,options.mode)
out_f.cd()
for h in histos:
    if not isData:
        h.SetName(h.GetName()+"_"+variation)
    h.Write()
out_f.Close()

