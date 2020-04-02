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
a.Define("doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)","myMatchedJets")


preselection1 = CutGroup('preselection1')
preselection1.Add("nFatJets","nFatJet > 1")

newcolumns = VarGroup("newcolumns")
newcolumns.Add("matchedH","myMatchedJets[0]")
newcolumns.Add("matchedY","myMatchedJets[1]")


preselected = a.Apply([preselection1,newcolumns])
preselected.Snapshot("nFatJet|nGenPart|FatJet*|Gen*",'snapshot_example.root',treename='preselected',lazy=False)

print("Total time: "+str((time.time()-start_time)/60.) + ' min')