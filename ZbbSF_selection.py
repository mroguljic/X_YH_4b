import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from HAMMER.Tools import CMS_lumi
from HAMMER.Tools.Common import *
from HAMMER.Analyzer import *
import array

parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '/afs/cern.ch/user/m/mrogulji/store/matej/testNtuples/Zqq_hh16.root',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-s', '--set', metavar='DATASET', type='string', action='store',
                default   =   'zqq',
                dest      =   'set',
                help      =   'Dataset being processed: zqq, wqq, tqq, QCDHT700... or data')
parser.add_option('-p', '--process', metavar='PROCESS', type='string', action='store',
                default   =   'zqq',
                dest      =   'process',
                help      =   'zqq, wqq, tqq, qcd or data')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   '.root file to store histograms')
(options, args) = parser.parse_args()
start_time = time.time()

commonc = CommonCscripts()
CompileCpp(commonc.vector)
CompileCpp(commonc.invariantMass)
CompileCpp(commonc.rho)
CompileCpp('HAMMER/Framework/topRejection.cc')
CompileCpp('HAMMER/Framework/leptonVeto.cc') # Compile a full file 


passCutoff=0.9
failCutoff=0.2
ptBins = array.array( 'd', [450, 500, 550, 600, 675, 800, 1200] )
nptBins = len(ptBins)-1


#------------Lumi scaling--------------#
xsecs={}
xsecs['tqq'] = 831760
xsecs['wqq'] = 2788000
xsecs['zqq'] = 1187000
xsecs['QCDHT700'] = 6802000
xsecs['QCDHT1000'] = 1206000
xsecs['QCDHT1500'] = 120400
xsecs['QCDHT2000'] = 25250
lumi = 35.872301001
norm_weight = 1

if options.process!='data':
    tempFile = ROOT.TFile.Open(options.input)
    runs_tree = tempFile.Get("Runs")
    nevents_gen = 0
    
    for i in runs_tree:
        nevents_gen+=i.genEventCount

    xsec = xsecs[options.set]
    norm_weight = lumi*xsec/float(nevents_gen)
    print("Norm weight for dataset {0}: {1}".format(options.set,norm_weight))
#-------------------------------------#


a = analyzer(options.input)
histos      = []
allColumns= a.GetActiveNode().DataFrame.GetColumnNames()
# for column in allColumns:
#   if("HLT" in str(column)):
#       print(column)
small_rdf = a.GetActiveNode().DataFrame.Range(50000) # makes an RDF with only the first nentries considered
small_node = Node('small',small_rdf) # makes a node out of the dataframe
a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node
a.Define("LeadingJet_rho","analyzer::rho(FatJet_msoftdrop[0],FatJet_pt_nom[0])")
Cuts = {
"Triggers":['HLT_PFHT800','HLT_PFHT900','HLT_AK8PFJet360_TrimMass30','HLT_AK8PFHT700_TrimR0p1PT0p03Mass50','HLT_PFHT650_WideJetMJJ950DEtaJJ1p5','HLT_PFHT650_WideJetMJJ900DEtaJJ1p5','HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20','HLT_PFJet450']
}


Cuts["Triggers"] = [x for x in Cuts["Triggers"] if x in allColumns]
yields = [] 
triggerCutString = " || ".join(Cuts["Triggers"])
print(triggerCutString)

yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
a.Cut("Triggers",triggerCutString)
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
a.Cut("eta","abs(FatJet_eta[0]) < 2.5")
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
a.Cut("pt","FatJet_pt_nom[0]>450")
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
a.Cut("rho","LeadingJet_rho>-6.0 && LeadingJet_rho<-2.1")
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
a.Cut("leptonVeto","leptonVeto(nElectron,Electron_cutBased,nMuon,Muon_looseId,nTau,Tau_idMVAnewDM2017v2)==0")
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
a.Cut("topVeto","topRejection(FatJet_phi,FatJet_msoftdrop,nFatJet,Jet_phi,nJet,Jet_btagDeepB,0.2219)==0")
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())
print(yields)


histos=[]

checkpoint  = a.GetActiveNode()
a.Cut("failRegion","FatJet_deepTagMD_ZHbbvsQCD[0]<{0} && FatJet_deepTagMD_ZHbbvsQCD[0]>{1}".format(passCutoff,failCutoff))
h_Fail = a.GetActiveNode().DataFrame.Histo2D(('{0}_fail'.format(options.process),'mass vs pt',23,40,201,nptBins,ptBins),'FatJet_msoftdrop','FatJet_pt_nom')
histos.append(h_Fail)
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())


a.SetActiveNode(checkpoint)
a.Cut("passRegion","FatJet_deepTagMD_ZHbbvsQCD[0]>{0}".format(passCutoff))
h_Pass = a.GetActiveNode().DataFrame.Histo2D(('{0}_pass'.format(options.process),'mass vs pt',23,40,201,nptBins,ptBins),'FatJet_msoftdrop','FatJet_pt_nom')
histos.append(h_Pass)
yields.append(a.GetActiveNode().DataFrame.Count().GetValue())

cutFlow = ROOT.TH1D('{0}_cutflow'.format(options.process), 'Cutflow', 8, 0.5, 8.5)
cutFlow.GetXaxis().SetBinLabel(1, "preselected")
cutFlow.GetXaxis().SetBinLabel(2, "trigger")
cutFlow.GetXaxis().SetBinLabel(3, "eta")
cutFlow.GetXaxis().SetBinLabel(4, "rho")
cutFlow.GetXaxis().SetBinLabel(5, "leptonVeto")
cutFlow.GetXaxis().SetBinLabel(6, "topVeto")
cutFlow.GetXaxis().SetBinLabel(7, "Fail")
cutFlow.GetXaxis().SetBinLabel(8, "Pass")

for i,N in enumerate(yields):
    cutFlow.AddBinContent(i+1,N)
histos.append(cutFlow)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Scale(norm_weight)
    h.Write()
out_f.Close()