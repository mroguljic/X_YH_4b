#To be used with trees from event selection
import ROOT as r
import time, os
from optparse import OptionParser
from collections import OrderedDict

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
parser.add_option('-p', '--process', metavar='PROCESS', type='string', action='store',
                default   =   'ttbarSemi',
                dest      =   'process',
                help      =   'Process in the given file')
parser.add_option('--data',action="store_true",dest="isData",default=False)

(options, args) = parser.parse_args()
a = analyzer(options.input)
histos =[]
hMET = a.DataFrame.Histo1D(('{0}_MET'.format(options.process),';MET [GeV];Events/100 GeV;',20,0,2000),"MET_pt")
hHT = a.DataFrame.Histo1D(('{0}_HT'.format(options.process),';HT [GeV];Events/100;',20,0,2000),"HT")
hST = a.DataFrame.Histo1D(('{0}_ST'.format(options.process),';ST [GeV];Events/100;',20,0,2000),"ST")
hPt = a.DataFrame.Histo1D(('{0}_lepton_pT'.format(options.process),';pT [GeV];Events/100;',20,0,2000),"lPt")

histos.append(hMET)
histos.append(hHT)
histos.append(hST)
histos.append(hPt)

if not options.isData:
    checkpoint = a.GetActiveNode()
    hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    histos.append(hMassInclusive)

    a.Cut("bqq","partonCategory==3")
    hMassInclusive = a.DataFrame.Histo1D(('{0}_bqq_mSD'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    beforePTcut = a.GetActiveNode()
    hMassLoPT = a.Cut("ptLoCutbqq","probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_bqq_mSD_pTLo'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    a.SetActiveNode(beforePTcut)
    hMassHiPT = a.Cut("ptHiCutbqq","probeJetPt>500").DataFrame.Histo1D(('{0}_bqq_mSD_pTHi'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    histos.append(hMassLoPT)
    histos.append(hMassHiPT)
    histos.append(hMassInclusive)
    a.SetActiveNode(checkpoint)

    a.Cut("bq","partonCategory==2")
    hMassInclusive = a.DataFrame.Histo1D(('{0}_bq_mSD'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    beforePTcut = a.GetActiveNode()
    hMassLoPT = a.Cut("ptLoCutbq","probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_bq_mSD_pTLo'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    a.SetActiveNode(beforePTcut)
    hMassHiPT = a.Cut("ptHiCutbq","probeJetPt>500").DataFrame.Histo1D(('{0}_bq_mSD_pTHi'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    histos.append(hMassLoPT)
    histos.append(hMassHiPT)
    histos.append(hMassInclusive)
    a.SetActiveNode(checkpoint)

    a.Cut("qq","partonCategory==1")
    hMassInclusive = a.DataFrame.Histo1D(('{0}_qq_mSD'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    beforePTcut = a.GetActiveNode()
    hMassLoPT = a.Cut("ptLoCutqq","probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_qq_mSD_pTLo'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    a.SetActiveNode(beforePTcut)
    hMassHiPT = a.Cut("ptHiCutqq","probeJetPt>500").DataFrame.Histo1D(('{0}_qq_mSD_pTHi'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    histos.append(hMassLoPT)
    histos.append(hMassHiPT)
    histos.append(hMassInclusive)

    a.SetActiveNode(checkpoint)
    a.Cut("unmatched","partonCategory==0")
    hMassInclusive = a.DataFrame.Histo1D(('{0}_unmatched_mSD'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    beforePTcut = a.GetActiveNode()
    hMassLoPT = a.Cut("ptLoCutunm","probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_unmatched_mSD_pTLo'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    a.SetActiveNode(beforePTcut)
    hMassHiPT = a.Cut("ptHiCutunm","probeJetPt>500").DataFrame.Histo1D(('{0}_unmatched_mSD_pTHi'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    histos.append(hMassLoPT)
    histos.append(hMassHiPT)
    histos.append(hMassInclusive)
    histos.append(hMassInclusive)
else:
    hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    beforePTcut = a.GetActiveNode()
    hMassLoPT = a.Cut("ptLoCut","probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_mSD_pTLo'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    a.SetActiveNode(beforePTcut)
    hMassHiPT = a.Cut("ptHiCut","probeJetPt>500").DataFrame.Histo1D(('{0}_mSD_pTHi'.format(options.process),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
    histos.append(hMassLoPT)
    histos.append(hMassHiPT)
    histos.append(hMassInclusive)



out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()

