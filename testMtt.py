import ROOT

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *
import sys

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
                default   =   'TTbarHad',
                dest      =   'process',
                help      =   'Process in the given MC file')

(options, args) = parser.parse_args()
start_time = time.time()


CompileCpp("TIMBER/Framework/common.cc") 
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/helperFunctions.cc") 
CompileCpp("TIMBER/Framework/TTstitching.cc")

xsecs = {"TTbarHad":377.96,"TTbarSemi":365.34,"TTbarMtt700":66.85,"TTbarMtt1000":16.38}
xsec  = xsecs[options.process]
lumi  = 41500 

histos=[]
a = analyzer(options.input)
nProc = 10000
small_rdf = a.GetActiveNode().DataFrame.Range(nProc) # makes an RDF with only the first nentries considered
small_node = Node('small',small_rdf) # makes a node out of the dataframe
a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node
sumGenW = a.GetActiveNode().DataFrame.Sum("genWeight")


a.Define("topIdx","getPartIdx(nGenPart,GenPart_pdgId,GenPart_statusFlags,6)")
a.Define("antitopIdx","getPartIdx(nGenPart,GenPart_pdgId,GenPart_statusFlags,-6)")
a.Cut("twoTops","topIdx>-1 && antitopIdx>-1") #perhaps unnecessary
nTwoTops = a.GetActiveNode().DataFrame.Count().GetValue()
print(nProc,nTwoTops)
a.Define("topVector","analyzer::TLvector(GenPart_pt[topIdx],GenPart_eta[topIdx],GenPart_phi[topIdx],GenPart_mass[topIdx])")
a.Define("antitopVector","analyzer::TLvector(GenPart_pt[antitopIdx],GenPart_eta[antitopIdx],GenPart_phi[antitopIdx],GenPart_mass[antitopIdx])")
a.Define("MTT",'analyzer::invariantMass(topVector,antitopVector)')
a.Define("topPt",'GenPart_pt[topIdx]')
a.Define("antitopPt",'GenPart_pt[antitopIdx]')
hMTTincl  = a.DataFrame.Histo1D(('MTT',';M_{TT} [GeV];;',30,0,3000.),"MTT","genWeight")
histos.append(hMTTincl)
a.Cut("nFatJet","nFatJet>1")
a.Cut("pT","FatJet_pt[0]>450 && FatJet_pt[1]>450")
hMTT  = a.DataFrame.Histo1D(('MTT_postPt',';M_{TT} [GeV];;',30,0,3000.),"MTT","genWeight")
histos.append(hMTT)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    #h.Scale(lumi*xsec/sumGenW)
    h.Write()
out_f.Close()

#a.PrintNodeTree('node_tree.dot',verbose=True) #not supported at the moment
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
