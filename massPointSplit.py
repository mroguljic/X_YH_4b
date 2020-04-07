import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from JHUanalyzer.Analyzer.analyzer import analyzer, Group, VarGroup, CutGroup
from JHUanalyzer.Tools.Common import openJSON,CutflowHist
from JHUanalyzer.Analyzer.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

parser = OptionParser()

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'config.json',
                dest      =   'config',
                help      =   'Configuration file in json format that is interpreted as a python dictionary')
#------------------------------------------------
#---------Script for debugging purposes----------
#------------------------------------------------
(options, args) = parser.parse_args()
customc.Import('./JHUanalyzer/Framework/AnalysisModules/deltaRMatching.cc')
start_time = time.time()
# Initialize
a = analyzer(options.input)
YmassPoints = ["125"]

#----------Adding interesting variables----------
mPointCut       = CutGroup("mPointCut")
mPointCut.Add("GenModel_YMass_125","GenModel_YMass_125==1")
newcolumns      = VarGroup("newcolumns")
newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
newcolumns.Add("GenY_pt" ,"getGen_Y_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
newcolumns.Add("GenH_pt" ,"getGen_H_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
preselection    = a.Apply([mPointCut,newcolumns])
#------------------------------------------------

#---------Applying DR matching------------------
cutH        = CutGroup("cutH")
cutY        = CutGroup("cutY")
cutH.Add("matchedH","matchedH > -1")
cutY.Add("matchedY","matchedY > -1")
matchedH    = preselection.Apply([cutH])
matchedY    = preselection.Apply([cutY])


#-------------Boosted cuts for H-----------------
boostedHCuts = CutGroup('boostedHCuts')
boostedHCuts.Add("FatJet_pt","FatJet_pt[matchedH]>300")
boostedHCuts.Add("FatJet_eta","FatJet_eta[matchedH]>-2.5 && FatJet_eta[matchedH]<2.5")

boostedHColumns = VarGroup("boostedHColumns")
boostedHColumns.Add("matchedHFatJet_pt","FatJet_pt[matchedH]")

boostedMatchedH = matchedH.Apply([boostedHCuts,boostedHColumns])
boostedMatchedH.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'boostedMatchedH.root',treename='boostedMatchedH',lazy=False)
#------------------------------------------------

#-------------Boosted cuts for Y-----------------
boostedYCuts = CutGroup('boostedYCuts')
boostedYCuts.Add("FatJet_pt","FatJet_pt[matchedY]>300")
boostedYCuts.Add("FatJet_eta","FatJet_eta[matchedY]>-2.5 && FatJet_eta[matchedY]<2.5")

boostedYColumns = VarGroup("boostedYColumns")
boostedYColumns.Add("matchedYFatJet_pt","FatJet_pt[matchedY]")

boostedMatchedY = matchedY.Apply([boostedYCuts,boostedYColumns])
boostedMatchedY.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'boostedMatchedY.root',treename='boostedMatchedY',lazy=False)

#------------------------------------------------

#-----------Histograms for each wp---------------
taggerH = "FatJet_btagHbb[matchedH]"
taggerY = "FatJet_btagHbb[matchedY]"
wps = [0.5]#,0.7,0.9]
for wp in wps:

    outputName    = "Y125_output.root"
    out_f         = ROOT.TFile(outputName,"RECREATE") 
    taggerHPass    = CutGroup("taggerHPass")
    taggerHFail    = CutGroup("taggerHPass")
    taggerHPass.Add(taggerH,"{0}>{1}".format(taggerH,wp))
    taggerHFail.Add(taggerH,"{0}<{1}".format(taggerH,wp))
    taggerYPass    = CutGroup("taggerYPass")
    taggerYFail    = CutGroup("taggerYPass")
    taggerYPass.Add(taggerY,"{0}>{1}".format(taggerY,wp))
    taggerYFail.Add(taggerY,"{0}<{1}".format(taggerY,wp))

    HpassedTagger = boostedMatchedH.Apply([taggerHPass])
    HfailedTagger = boostedMatchedH.Apply([taggerHFail])
    YpassedTagger = boostedMatchedY.Apply([taggerYPass])
    YfailedTagger = boostedMatchedY.Apply([taggerYFail])
    HpassedTagger.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'HpassedTagger.root',treename='HpassedTagger',lazy=False)
    HfailedTagger.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'HfailedTagger.root',treename='HfailedTagger',lazy=False)
    YpassedTagger.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'YpassedTagger.root',treename='YpassedTagger',lazy=False)
    YfailedTagger.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'YfailedTagger.root',treename='YfailedTagger',lazy=False)

    out_f.mkdir("H")
    tDir = out_f.GetDirectory("H")
    tDir.cd()
    
    hPass = HpassedTagger.DataFrame.Histo1D(("HpassedTagger_pt","HpassedTagger_pt",100,0,2000),"GenH_pt")
    hFail = HfailedTagger.DataFrame.Histo1D(("HfailedTagger_pt","HfailedTagger_pt",100,0,2000),"GenH_pt")
    hEff  = ROOT.TEfficiency(hPass.GetValue(),hPass.GetValue()+hFail.GetValue())
    hEff.SetName("eff_H")
    hPass.Write()
    hFail.Write()
    hEff.Write()

    out_f.mkdir("Y")
    tDir = out_f.GetDirectory("Y")
    tDir.cd()
    
    hPass = YpassedTagger.DataFrame.Histo1D(("YpassedTagger_pt","YpassedTagger_pt",100,0,2000),"GenY_pt")
    hFail = YfailedTagger.DataFrame.Histo1D(("YfailedTagger_pt","YfailedTagger_pt",100,0,2000),"GenY_pt")
    hEff  = ROOT.TEfficiency(hPass.GetValue(),hPass.GetValue()+hFail.GetValue())
    hEff.SetName("eff_Y")
    hPass.Write()
    hFail.Write()
    hEff.Write()

    out_f.Close()
#------------------------------------------------

print("Total time: "+str((time.time()-start_time)/60.) + ' min')