import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from JHUanalyzer.Analyzer.analyzer import analyzer, Group, VarGroup, CutGroup, SetCFunc
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

#----------Post-trigger cuts---------------------
jetsCuts = CutGroup("jetsCuts")
jetsCuts.Add("nFatJet","nFatJet>1")
jetsCuts.Add("Leading jets Pt","FatJet_pt[0] > 300 && FatJet_pt[1] > 300")
jetsCuts.Add("Leading jets eta","abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4")
#jetsCuts.Add("Leading jets delta eta","abs(FatJet_eta[1]-FatJet_eta[0])<1.4")
newcolumns = VarGroup("newcolumns")
newcolumns.Add("deltaEta","FatJet_eta[0]-FatJet_eta[1]")
preselection1 = a.Apply([jetsCuts,newcolumns])
preselection1.Snapshot("nFatJet|GenModel_YMass_*|FatJet_pt|FatJet_eta|deltaEta",'deltaEta.root',treename='test',lazy=False)

# pvCuts = CutGroup("pvCuts")
# pvCuts.Add("PV nDof","PV_ndof>4")
# pvCuts.Add("PV z displacement","abs(PV_z)<4")
# pvCuts.Add("PV transverse displacement","(PV_x*PV_x + PV_y*PV_y)<4") #transverse displacement r<2

# massCuts = CutGroup("massCuts")
# massCuts.Add("GenModel_YMass_200","GenModel_YMass_200==1")
# massCuts.Add("msoftdrop_0","100 < FatJet_msoftdrop[0] && FatJet_msoftdrop[0] < 500")
# massCuts.Add("msoftdrop_1","100 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 500")

# #pvCutsSelection = jetCutsSelection.Apply([pvCuts])
# #pvCutsSelection.Snapshot("PV_*|nFatJet|FatJet_pt|FatJet_eta",'test.root',treename='test',lazy=False)#PV* columns must be first or nPV included!

# SetCFunc(commonc.vector) # common library
# SetCFunc(commonc.invariantMass) # common library

# newcolumns = VarGroup("newcolumns2")
# newcolumns.Add("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
# newcolumns.Add("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
# newcolumns.Add("mhh","analyzer::invariantMass(lead_vect,sublead_vect)")
# newcolumns.Add("mreduced","mhh - (FatJet_msoftdrop[0]-125.0) - (FatJet_msoftdrop[1]-125.0)")
# newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
# newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
# newcolumns.Add("GenY_pt" ,"getGen_Y_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
# newcolumns.Add("GenH_pt" ,"getGen_H_pt(nGenPart,GenPart_pdgId,GenPart_pt)")

# preselection2 = preselection1.Apply([pvCuts,massCuts,newcolumns])
# preselection2.Snapshot("nFatJet|FatJet*|lead_vect|sublead_vect|mhh|mreduced|matchedH|matchedY",'test.root',treename='test',lazy=True)


# #----------Adding interesting variables----------
# newcolumns      = VarGroup("newcolumns")
# newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
# newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
# newcolumns.Add("GenY_pt" ,"getGen_Y_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
# newcolumns.Add("GenH_pt" ,"getGen_H_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
# preselection    = a.Apply([newcolumns])
# #------------------------------------------------

# #---------Applying DR matching------------------
# cutH        = CutGroup("cutH")
# cutY        = CutGroup("cutY")
# cutH.Add("matchedH","matchedH > -1")
# cutY.Add("matchedY","matchedY > -1")
# matchedH    = preselection.Apply([cutH])
# matchedY    = preselection.Apply([cutY])


# #-------------Boosted cuts for H-----------------
# boostedHCuts = CutGroup('boostedHCuts')
# boostedHCuts.Add("FatJet_pt","FatJet_pt[matchedH]>300")
# boostedHCuts.Add("FatJet_eta","FatJet_eta[matchedH]>-2.5 && FatJet_eta[matchedH]<2.5")
# #boostedHCuts.Add("FatJet_eta","FatJet_eta[matchedH]>-1.5 && FatJet_eta[matchedH]<1.5")

# boostedHColumns = VarGroup("boostedHColumns")
# boostedHColumns.Add("matchedHFatJet_pt","FatJet_pt[matchedH]")

# boostedMatchedH = matchedH.Apply([boostedHCuts,boostedHColumns])
# boostedMatchedH.Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'boostedMatchedH.root',treename='boostedMatchedH',lazy=False)
# #------------------------------------------------

# #-------------Boosted cuts for Y-----------------

# boostedMatchedYs=[]
# for massPoint in YmassPoints:
#     ptCutOff = 2*float(massPoint)/0.8
#     ptCutOff = 50 * round(ptCutOff/50.) #round to nearest multiple of 50
#     print("Mass {0} - pt cutoff {1}".format(massPoint,ptCutOff))
#     tempYCuts = CutGroup("boostedYCuts_{0}".format(massPoint))
#     tempYCuts.Add("GenModel_YMass_{0}".format(massPoint),"GenModel_YMass_{0}==1".format(massPoint))
#     tempYCuts.Add("FatJet_pt","FatJet_pt[matchedY]>{0}".format(ptCutOff))
#     tempYCuts.Add("FatJet_eta","FatJet_eta[matchedY]>-2.5 && FatJet_eta[matchedY]<2.5")
# #    tempYCuts.Add("FatJet_eta","FatJet_eta[matchedY]>-1.5 && FatJet_eta[matchedY]<1.5")
#     tempYColumns = VarGroup("boostedYColumn_{0}".format(massPoint))
#     tempYColumns.Add("matchedYFatJet_pt","FatJet_pt[matchedY]")
#     boostedMatchedYs.append(matchedY.Apply([tempYCuts,tempYColumns]))
#     #boostedMatchedYs[-1].Snapshot("nFatJet|nGenPart|FatJet*|Gen*|matchedH|matchedY|matchedHFatJet_pt|matchedYFatJet_pt",'boostedMatchedY_{0}.root'.format(massPoint),treename='boostedMatchedY_{0}'.format(massPoint),lazy=False)
# #------------------------------------------------

# #-----------Histograms for each wp---------------
# taggerH = "FatJet_btagHbb[matchedH]"
# taggerY = "FatJet_btagHbb[matchedY]"
# wps = [0.5,0.7,0.9]
# for wp in wps:

#     outputName    = "outputWP_{0}.root".format(wp)
#     #out_f = ROOT.TFile(options.output,"RECREATE") 
#     out_f         = ROOT.TFile(outputName,"RECREATE") 
#     taggerHPass    = CutGroup("taggerHPass")
#     taggerHFail    = CutGroup("taggerHFail")
#     taggerHPass.Add(taggerH,"{0}>{1}".format(taggerH,wp))
#     taggerHFail.Add(taggerH,"{0}<{1}".format(taggerH,wp))
#     taggerYPass    = CutGroup("taggerYPass")
#     taggerYFail    = CutGroup("taggerYFail")
#     taggerYPass.Add(taggerY,"{0}>{1}".format(taggerY,wp))
#     taggerYFail.Add(taggerY,"{0}<{1}".format(taggerY,wp))
#     HpassedTagger = boostedMatchedH.Apply([taggerHPass])
#     HfailedTagger = boostedMatchedH.Apply([taggerHFail])

#     for i,boostedMatchedY in enumerate(boostedMatchedYs):
#         dirName = "YMass_{0}".format(YmassPoints[i])
#         out_f.mkdir(dirName)
#         tDir = out_f.GetDirectory(dirName)
#         tDir.cd()
#         YpassedTagger = boostedMatchedY.Apply([taggerYPass])
#         YfailedTagger = boostedMatchedY.Apply([taggerYFail])
#         hists=[]
#         #hPass = YpassedTagger.DataFrame.Histo1D(("YpassedTagger_pt","YpassedTagger_pt",100,0,2000),"matchedYFatJet_pt") if we want jet pt instead of gen pt
#         hPass = YpassedTagger.DataFrame.Histo1D(("YpassedTagger_pt","YpassedTagger_pt",100,0,2000),"GenY_pt")
#         hFail = YfailedTagger.DataFrame.Histo1D(("YfailedTagger_pt","YfailedTagger_pt",100,0,2000),"GenY_pt")
#         hEff  = ROOT.TEfficiency(hPass.GetValue(),hPass.GetValue()+hFail.GetValue())
#         hEff.SetName("eff_YMasss_{0}".format(YmassPoints[i]))
#         hists.append(hPass)
#         hists.append(hFail)
#         hists.append(hEff) #not a hist though, tefficiency
  
#         for h in hists:
#             h.Write()

#     out_f.mkdir("H")
#     tDir = out_f.GetDirectory("H")
#     tDir.cd()
    
#     hPass = HpassedTagger.DataFrame.Histo1D(("HpassedTagger_pt","HpassedTagger_pt",100,0,2000),"GenH_pt")
#     hFail = HfailedTagger.DataFrame.Histo1D(("HfailedTagger_pt","HfailedTagger_pt",100,0,2000),"GenH_pt")
#     hEff  = ROOT.TEfficiency(hPass.GetValue(),hPass.GetValue()+hFail.GetValue())
#     hEff.SetName("eff_H")
#     hPass.Write()
#     hFail.Write()
#     hEff.Write()


#     out_f.Close()
# #------------------------------------------------

print("Total time: "+str((time.time()-start_time)/60.) + ' min')