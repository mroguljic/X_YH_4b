import ROOT
import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

def dropColumns(columnList,isData):
    if(isData):
      HLTfile = open("/afs/cern.ch/work/m/mrogulji/X_YH_4b/HLTsToKeep.txt","r")
      goodHLTs = HLTfile.read().splitlines()                                              
                                                                               
    with open("/afs/cern.ch/work/m/mrogulji/X_YH_4b/columnBlackList.txt","r") as f:                                 
      badColumns = f.read().splitlines()                                       
                                                                               
    for c in columnList:
      if(str(c).startswith("HLT_") and not isData):
        continue
      elif(str(c).startswith("HLT_") and isData):
        if(c in goodHLTs):
          yield c
        else:
          continue
      elif c in badColumns:                                                      
        continue                                                               
      else:                                                                    
        yield c   


parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('--data',action="store_true",dest="isData",default=False)
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')

(options, args) = parser.parse_args()
start_time = time.time()
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/helperFunctions.cc") 

a = analyzer(options.input)

print(a.GetActiveNode().DataFrame.Count().GetValue())
small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
small_node = Node('small',small_rdf) # makes a node out of the dataframe
a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

nTotal = a.GetActiveNode().DataFrame.Count().GetValue()
a.Define("SkimFlag","skimFlag(nFatJet,FatJet_eta,FatJet_pt,FatJet_msoftdrop,nJet,Jet_eta,Jet_pt,nElectron,Electron_cutBased,nMuon,Muon_looseId,Muon_pfIsoId)")
a.Cut("SkimFlagCut","SkimFlag>0")
nSkim = a.GetActiveNode().DataFrame.Count().GetValue()
print(nSkim,nTotal,nSkim/nTotal)

opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
goodcols = [str(c) for c in dropColumns(a.DataFrame.GetColumnNames(),options.isData)] 
a.GetActiveNode().DataFrame.Snapshot("Events",options.output,goodcols,opts)


hCutFlow = ROOT.TH1F('skimInfo',"Number of processed events",2,0.5,2.5)
hCutFlow.AddBinContent(1,nTotal)
hCutFlow.AddBinContent(2,nSkim)
hCutFlow.GetXaxis().SetBinLabel(1, "Total events")
hCutFlow.GetXaxis().SetBinLabel(2, "After skimming")
out_f = ROOT.TFile(options.output,"UPDATE")
out_f.cd()
hCutFlow.Write()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
out_f.Close()
