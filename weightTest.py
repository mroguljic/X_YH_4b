import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser

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


(options, args) = parser.parse_args()
start_time = time.time()
a = analyzer(options.input)

print(a.GetActiveNode().DataFrame.Count().GetValue())
small_rdf = a.GetActiveNode().DataFrame.Range(10000) # makes an RDF with only the first nentries considered
small_node = Node('small',small_rdf) # makes a node out of the dataframe
a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

a.Cut("nFatJet","nFatJet>0")
a.Define("pT0","FatJet_pt[0]")
hBefore = a.GetActiveNode().DataFrame.Histo1D(("ptBefore","",3,0,3000.),"pT0")

ptCorr = Correction('hPtCorr',"TIMBER/Framework/src/HistLoader.cc",constructor=["dummySF.root","pT_SF"],corrtype='weight')
a.AddCorrection(ptCorr, evalArgs=['FatJet_pt[0]'])

hAfter  = a.GetActiveNode().DataFrame.Histo1D(("ptAfter","",3,0,3000.),"pT0")
out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
hBefore.Write()
hAfter.Write()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
