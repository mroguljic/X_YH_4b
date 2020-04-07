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
YmassPoints = ["90","100","125","150","200","250","300","400","500","600","700"]#"800","900","1000","1200","1400","1600","1800"] pt cut kills higher mass points

#----------Adding interesting variables----------
newcolumns      = VarGroup("newcolumns")
newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
newcolumns.Add("GenY_pt" ,"getGen_Y_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
newcolumns.Add("GenH_pt" ,"getGen_H_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
preselection    = a.Apply([newcolumns])
#------------------------------------------------

#---------Applying DR matching------------------
cutH        = CutGroup("cutH")
cutY        = CutGroup("cutY")
cutH.Add("matchedH","matchedH > -1")
cutY.Add("matchedY","matchedY > -1")
matchedH    = preselection.Apply([cutH])
matchedY    = preselection.Apply([cutY])

#matchedH.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|FatJet_btagHbb",'matchedH.root',treename='matchedH',lazy=False)
#matchedY.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|FatJet_btagHbb",'matchedY.root',treename='matchedY',lazy=False)
#------------------------------------------------

#-----Cross check if DR matched as expected------

# matchedY_YMassPoints = []
# tot_YMassPoints      = []
# drMatchinghistos     = []
# for massPoint in YmassPoints:
#     tempYCuts = CutGroup("tempCut_{0}".format(massPoint))
#     tempYCuts.Add("GenModel_YMass_{0}".format(massPoint),"GenModel_YMass_{0}==1".format(massPoint))
#     matchedY_YMassPoints.append(matchedY.Apply([tempYCuts]))
#     tot_YMassPoints.append(preselection.Apply([tempYCuts]))


# for i in range(len(YmassPoints)):
#     hMatched = matchedY_YMassPoints[i].DataFrame.Histo1D(("Y_DRmatched_{0}".format(YmassPoints[i]),"Y_DRmatched".format(YmassPoints[i]),100,0,2000),"GenY_pt")    
#     hTot     = tot_YMassPoints[i].DataFrame.Histo1D(("Y_tot_{0}".format(YmassPoints[i]),"Y_tot_{0}".format(YmassPoints[i]),100,0,2000),"GenY_pt")
#     hEff     = ROOT.TEfficiency(hMatched.GetValue(),hTot.GetValue()) 
#     hEff.SetName("YmatchingEfff_{0}".format(YmassPoints[i]))
#     drMatchinghistos.append(hMatched)
#     drMatchinghistos.append(hTot)
#     drMatchinghistos.append(hEff)

# hMatched = matchedH.DataFrame.Histo1D(("H_DRmatched","H_DRmatched",100,0,2000),"GenH_pt")
# hTot     = preselection.DataFrame.Histo1D(("H_tot","H_tot",100,0,2000),"GenH_pt")
# hEff     = ROOT.TEfficiency(hMatched.GetValue(),hTot.GetValue()) 
# hEff.SetName("HmatchingEfff")
# out_f    = ROOT.TFile("drMatching_control.root","RECREATE") 

# hMatched.Write()
# hTot.Write()
# hEff.Write()

# for histo in drMatchinghistos:
#     histo.Write()

# out_f.Close()
#------------------------------------------------


#-------------Boosted cuts for H-----------------
boostedHCuts = CutGroup('boostedHCuts')
boostedHCuts.Add("FatJet_pt","FatJet_pt[matchedH]>300")
boostedHCuts.Add("FatJet_eta","FatJet_eta[matchedH]>-2.5 && FatJet_eta[matchedH]<2.5")

boostedHColumns = VarGroup("boostedHColumns")
boostedHColumns.Add("matchedHFatJet_pt","FatJet_pt[matchedH]")

boostedMatchedH = matchedH.Apply([boostedHCuts,boostedHColumns])
#boostedMatchedH.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'boostedMatchedH.root',treename='boostedMatchedH',lazy=False)
#------------------------------------------------

#-------------Boosted cuts for Y-----------------

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
    #boostedMatchedYs[-1].Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'boostedMatchedY_{0}.root'.format(massPoint),treename='boostedMatchedY_{0}'.format(massPoint),lazy=False)
#------------------------------------------------

#-----------Histograms for each wp---------------
taggerH = "FatJet_btagHbb[matchedH]"
taggerY = "FatJet_btagHbb[matchedY]"
wps = [0.5,0.7,0.9]
for wp in wps:

    outputName    = "outputWP_{0}.root".format(wp)
    #out_f = ROOT.TFile(options.output,"RECREATE") 
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

    for i,boostedMatchedY in enumerate(boostedMatchedYs):
        dirName = "YMass_{0}".format(YmassPoints[i])
        out_f.mkdir(dirName)
        tDir = out_f.GetDirectory(dirName)
        tDir.cd()
        YpassedTagger = boostedMatchedY.Apply([taggerYPass])
        YfailedTagger = boostedMatchedY.Apply([taggerYFail])
        hists=[]
        #hPass = YpassedTagger.DataFrame.Histo1D(("YpassedTagger_pt","YpassedTagger_pt",100,0,2000),"matchedYFatJet_pt") if we want jet pt instead of gen pt
        hPass = YpassedTagger.DataFrame.Histo1D(("YpassedTagger_pt","YpassedTagger_pt",100,0,2000),"GenY_pt")
        hFail = YfailedTagger.DataFrame.Histo1D(("YfailedTagger_pt","YfailedTagger_pt",100,0,2000),"GenY_pt")
        hEff  = ROOT.TEfficiency(hPass.GetValue(),hPass.GetValue()+hFail.GetValue())
        hEff.SetName("eff_YMasss_{0}".format(YmassPoints[i]))
        hists.append(hPass)
        hists.append(hFail)
        hists.append(hEff) #not a hist though, tefficiency
  
        for h in hists:
            h.Write()

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


    out_f.Close()
#------------------------------------------------

print("Total time: "+str((time.time()-start_time)/60.) + ' min')