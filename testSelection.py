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


(options, args) = parser.parse_args()
customc.Import('./JHUanalyzer/Framework/AnalysisModules/deltaRMatching.cc')
start_time = time.time()
# Initialize
a = analyzer(options.input)
#a.Define("myMatchedJets","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")


preselection1   = CutGroup('preselection1')
newcolumns      = VarGroup("newcolumns")
preselection1.Add("nFatJets","nFatJet > 1")
newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
preselection    = a.Apply([preselection1,newcolumns])


cutH        = CutGroup("cutH")
cutY        = CutGroup("cutY")
cutH.Add("matchedH","matchedH > -1")
cutY.Add("matchedY","matchedY > -1")
matchedH    = preselection.Apply([cutH])
matchedY    = preselection.Apply([cutY])
#matchedH.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY",'matchedH.root',treename='preselection',lazy=False)

#matchedY.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY",'matchedY.root',treename='preselection',lazy=False)

boostedHCuts = CutGroup('boostedHCuts')
boostedHCuts.Add("FatJet_pt","FatJet_pt[matchedH]>300")
boostedHCuts.Add("FatJet_eta","FatJet_eta[matchedH]>-2.5 && FatJet_eta[matchedH]<2.5")

boostedHColumns = VarGroup("boostedHColumns")
boostedHColumns.Add("matchedHFatJet_pt","FatJet_pt[matchedH]")
#boostedHColumns.Add("matchedHFatJet_pt","matchedH > -1 ? FatJet_pt[matchedY] : 0") don't need this since we already cut matchedH=-1

boostedMatchedH = matchedH.Apply([boostedHCuts,boostedHColumns])
boostedMatchedH.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt,matchedYFatJet_pt",'boostedMatchedH.root',treename='preselection',lazy=True)

YmassPoints = ["90","100","125","150","200","250","300","400","500","600","700"]#"800","900","1000","1200","1400","1600","1800"] pt cut kills higher mass points
boostedMatchedYs=[]
for massPoint in YmassPoints:
    ptCutOff = 2*float(massPoint)/0.8
    ptCutOff = 50 * round(ptCutOff/50.) #round to nearest multiple of 50
    print("Mass {0} - pt cutoff {1}".format(massPoint,ptCutOff))
    tempYCuts = CutGroup("boostedYCuts_{0}".format(massPoint))
    tempYCuts.Add("GenModel_YMass_{0}".format(massPoint),"GenModel_YMass_{0}==1".format(massPoint))
    tempYCuts.Add("FatJet_pt","FatJet_pt[matchedY]>{0}".format(ptCutOff))
    tempYCuts.Add("FatJet_eta","FatJet_eta[matchedY]>-2.5 && FatJet_eta[matchedY]<2.5")
    tempYColumns = VarGroup("boostedYColumn_{0}".format(massPoint))
    tempYColumns.Add("matchedYFatJet_pt","FatJet_pt[matchedY]")
    boostedMatchedYs.append(matchedY.Apply([tempYCuts,tempYColumns]))


tagger = "FatJet_btagHbb[matchedH]"
wps = [0.5,0.7,0.9]
for wp in wps:

    outputName    = "outputWP_{0}.root".format(wp)
    #out_f = ROOT.TFile(options.output,"RECREATE") 
    out_f         = ROOT.TFile(outputName,"RECREATE") 
    taggerPass    = CutGroup("taggerPass")
    taggerFail    = CutGroup("taggerPass")
    taggerPass.Add(tagger,"{0}>{1}".format(tagger,wp))
    taggerFail.Add(tagger,"{0}<{1}".format(tagger,wp))
    HpassedTagger = boostedMatchedH.Apply([taggerPass])
    HfailedTagger = boostedMatchedH.Apply([taggerFail])

    for i,boostedMatchedY in enumerate(boostedMatchedYs):
        dirName = "YMass_{0}".format(YmassPoints[i])
        out_f.mkdir(dirName)
        tDir = out_f.GetDirectory(dirName)
        tDir.cd()
        YpassedTagger = boostedMatchedY.Apply([taggerPass])
        YfailedTagger = boostedMatchedY.Apply([taggerFail])
        hists=[]
        hists.append(YpassedTagger.DataFrame.Histo1D(("YpassedTagger_pt","YpassedTagger_pt",100,0,2000),"matchedYFatJet_pt"))
        hists.append(YfailedTagger.DataFrame.Histo1D(("YfailedTagger_pt","YfailedTagger_pt",100,0,2000),"matchedYFatJet_pt"))
#    hists.append(HpassedTagger.DataFrame.Histo1D(("HpassedTagger_pt","HpassedTagger_pt",100,0,2000),"matchedHFatJet_pt"))
#    hists.append(HfailedTagger.DataFrame.Histo1D(("HfailedTagger_pt","HfailedTagger_pt",100,0,2000),"matchedHFatJet_pt"))    
        for h in hists:
            h.Write()

    out_f.mkdir("H")
    tDir = out_f.GetDirectory("H")
    tDir.cd()
    
    hPass = HpassedTagger.DataFrame.Histo1D(("HpassedTagger_pt","HpassedTagger_pt",100,0,2000),"matchedHFatJet_pt")
    hFail = HfailedTagger.DataFrame.Histo1D(("HfailedTagger_pt","HfailedTagger_pt",100,0,2000),"matchedHFatJet_pt")

    hPass.Write()
    hFail.Write()
    # hists = [boostedMatchedH.DataFrame.Histo1D(("matchedHFatJet_pt","matchedHFatJet_pt",100,0,2000),"matchedHFatJet_pt")]
    # for i,massPoint in enumerate(YmassPoints):
    #     histName  = "matchedHFatJet_pt_Y{0}".format(massPoint)
    #     histTitle = "matchedHFatJet_pt_Y{0}".format(massPoint)
    #     hists.append(boostedMatchedYs[i].DataFrame.Histo1D((histName,histTitle,100,0,2000),"matchedYFatJet_pt"))


    out_f.Close()

print("Total time: "+str((time.time()-start_time)/60.) + ' min')