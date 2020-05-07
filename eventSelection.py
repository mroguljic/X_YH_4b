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

parser.add_option('-s',"--sig", action="store_true",  dest="isSignal")
parser.add_option('-b',"--bkg", action="store_false", dest="isSignal")

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
wps = [0.7]
#----------Post-trigger cuts---------------------
if(options.isSignal):
    for wp in wps:
        for massPoint in YmassPoints:

            totalOutFile        = "total_Y{1}.root".format(wp,massPoint)
            preselectionOutFile = "preselection_Y{1}.root".format(wp,massPoint)
            selection1OutFile   = "selection1_Y{1}.root".format(wp,massPoint)
            selection2OutFile   = "selection2_Y{1}.root".format(wp,massPoint)

            genMassCut          = CutGroup("genMassCut")
            genMassCut.Add("Y mass","GenModel_YMass_{0}".format(massPoint))
            total               = a.Apply([genMassCut])
            total.Snapshot("GenModel_YMass_{0}".format(massPoint),totalOutFile,treename="total_Y{0}".format(massPoint),lazy=False)

            preselectionCuts    = CutGroup("preselectionCuts")
            preselectionCuts.Add("nFatJet","nFatJet>1")
            preselectionCuts.Add("Leading jets eta","abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4")
            preselectionCuts.Add("Leading jets delta eta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.5")
            preselectionCuts.Add("Leading jets Pt","FatJet_pt[0] > 200 && FatJet_pt[1] > 200")
            newcolumns          = VarGroup("newcolumns")
            newcolumns.Add("deltaEta","FatJet_eta[0]-FatJet_eta[1]")
            newcolumns.Add("Jet0_HPass","FatJet_pt[0]>300 && FatJet_msoftdrop[0]<140 && FatJet_msoftdrop[0]>110 && FatJet_btagHbb[0]>{0}".format(wp))
            newcolumns.Add("Jet1_HPass","FatJet_pt[1]>300 && FatJet_msoftdrop[1]<140 && FatJet_msoftdrop[1]>110 && FatJet_btagHbb[1]>{0}".format(wp))
            newcolumns.Add("deltaEta","FatJet_eta[0]-FatJet_eta[1]")

            preselection        = total.Apply([preselectionCuts,newcolumns])
            preselection.Snapshot("nFatJet|GenModel_YMass_*|Jet0_HPass|Jet1_HPass|FatJet_pt|FatJet_eta|deltaEta",preselectionOutFile,treename='preselection_Y{0}'.format(massPoint),lazy=False)


            selection1Cuts      = CutGroup("selection1Cuts")
            selection1Cuts.Add("Higgs requirement","Jet0_HPass || Jet1_HPass")

            selection1          = preselection.Apply([selection1Cuts])
            selection1.Snapshot("nFatJet|GenModel_YMass_*|Jet0_HPass|Jet1_HPass|FatJet_pt|FatJet_eta|deltaEta",selection1OutFile,treename='selection1_Y{0}'.format(massPoint),lazy=False)

            selection2Cuts      = CutGroup("selection2Cuts")
            otherJetCut         = "(Jet0_HPass==1 && FatJet_msoftdrop[1]>50 && FatJet_btagHbb[1]>{0}) || (Jet1_HPass==1 && FatJet_msoftdrop[0]>50 && FatJet_btagHbb[0]>{0})".format(wp)
            selection2Cuts.Add("Loose H requirement",otherJetCut)
            selection2          = selection1.Apply([selection2Cuts])
            selection2.Snapshot("nFatJet|GenModel_YMass_*|Jet0_HPass|Jet1_HPass|FatJet_pt|FatJet_eta|deltaEta",selection2OutFile,treename='selection2_Y{0}'.format(massPoint),lazy=False)


        wp_outputFile   = options.output+"_wp_{0}.root".format(wp)
        mergeRootF      = "hadd -f {0} preselection_Y* selection1_Y* selection2_Y* total_Y*".format(wp_outputFile)
        cleanUp         = "rm preselection_Y* selection1_Y* selection2_Y* total_Y*"
        print(mergeRootF)
        os.system(mergeRootF)
        print(cleanUp)
        os.system(cleanUp)

else:
    for wp in wps:
        totalOutFile        = "total.root"
        preselectionOutFile = "preselection.root"
        selection1OutFile   = "selection1.root"
        selection2OutFile   = "selection2.root"
        
        newcolumns          = VarGroup("newcolumns")
        newcolumns.Add("deltaEta","FatJet_eta[0]-FatJet_eta[1]")
        newcolumns.Add("Jet0_HPass","FatJet_pt[0]>300 && FatJet_msoftdrop[0]<140 && FatJet_msoftdrop[0]>110 && FatJet_btagHbb[0]>{0}".format(wp))
        newcolumns.Add("Jet1_HPass","FatJet_pt[1]>300 && FatJet_msoftdrop[1]<140 && FatJet_msoftdrop[1]>110 && FatJet_btagHbb[1]>{0}".format(wp))
        total               = a.Apply([newcolumns])
        total.Snapshot("nFatJet",totalOutFile,treename="total",lazy=False)

        preselectionCuts    = CutGroup("preselectionCuts")
        preselectionCuts.Add("nFatJet","nFatJet>1")
        preselectionCuts.Add("Leading jets eta","abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4")
        preselectionCuts.Add("Leading jets delta eta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.5")
        preselectionCuts.Add("Leading jets Pt","FatJet_pt[0] > 200 && FatJet_pt[1] > 200")
        preselection        = total.Apply([preselectionCuts])
        preselection.Snapshot("nFatJet|Jet0_HPass|Jet1_HPass|FatJet_pt|FatJet_eta|deltaEta",preselectionOutFile,treename='preselection',lazy=False)


        selection1Cuts      = CutGroup("selection1Cuts")
        selection1Cuts.Add("Higgs requirement","Jet0_HPass || Jet1_HPass")

        selection1          = preselection.Apply([selection1Cuts])
        selection1.Snapshot("nFatJet|Jet0_HPass|Jet1_HPass|FatJet_pt|FatJet_eta|deltaEta",selection1OutFile,treename='selection1',lazy=False)

        selection2Cuts      = CutGroup("selection2Cuts")
        otherJetCut         = "(Jet0_HPass==1 && FatJet_msoftdrop[1]>50 && FatJet_btagHbb[1]>{0}) || (Jet1_HPass==1 && FatJet_msoftdrop[0]>50 && FatJet_btagHbb[0]>{0})".format(wp)
        selection2Cuts.Add("Loose H requirement",otherJetCut)
        selection2          = selection1.Apply([selection2Cuts])
        selection2.Snapshot("nFatJet|Jet0_HPass|Jet1_HPass|FatJet_pt|FatJet_eta|deltaEta",selection2OutFile,treename='selection2',lazy=False)

        wp_outputFile   = options.output+"_wp_{0}.root".format(wp)
        mergeRootF      = "hadd -f {0} preselection.root selection1.root selection2.root total.root".format(wp_outputFile)
        cleanUp         = "rm preselection.root selection1.root selection2.root total.root"
        print(mergeRootF)
        os.system(mergeRootF)
        print(cleanUp)
        os.system(cleanUp)    

print("Total time: "+str((time.time()-start_time)/60.) + ' min')