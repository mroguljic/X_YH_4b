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

(options, args) = parser.parse_args()
a = analyzer(options.input)
if("data" in options.process):
    isData=True
else:
    isData=False

histos =[]

pnetHi = 0.95
pnetLo = 0.80
pnetCuts = ["probeJetPNet>{0}".format(pnetHi),"probeJetPNet>{0} && probeJetPNet<{1}".format(pnetLo,pnetHi)]
pnetTags = ["T","L"]

beforePnet = a.GetActiveNode()
for i in range(len(pnetCuts)):
    a.Cut("{0}_cut".format(pnetTags[i]),pnetCuts[0])

    hMET = a.DataFrame.Histo1D(('{0}_MET_{1}'.format(options.process,pnetTags[i]),';MET [GeV];Events/100 GeV;',20,0,2000),"MET_pt")
    hHT = a.DataFrame.Histo1D(('{0}_HT_{1}'.format(options.process,pnetTags[i]),';HT [GeV];Events/100;',20,0,2000),"HT")
    hST = a.DataFrame.Histo1D(('{0}_ST_{1}'.format(options.process,pnetTags[i]),';ST [GeV];Events/100;',20,0,2000),"ST")
    hPt = a.DataFrame.Histo1D(('{0}_lepton_pT_{1}'.format(options.process,pnetTags[i]),';pT [GeV];Events/100;',20,0,2000),"lPt")

    histos.append(hMET)
    histos.append(hHT)
    histos.append(hST)
    histos.append(hPt)

    if not isData:
        checkpoint = a.GetActiveNode()
        hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        histos.append(hMassInclusive)

        a.Cut("bqq_{0}".format(pnetTags[i]),"partonCategory==3")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_bqq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutbqq_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_bqq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutbqq_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_bqq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        a.SetActiveNode(checkpoint)

        a.Cut("bq_{0}".format(pnetTags[i]),"partonCategory==2")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_bq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutbq_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_bq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutbq_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_bq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        a.SetActiveNode(checkpoint)

        a.Cut("qq_{0}".format(pnetTags[i]),"partonCategory==1")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_qq_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutqq_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_qq_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutqq_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_qq_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)

        a.SetActiveNode(checkpoint)
        a.Cut("unmatched_{0}".format(pnetTags[i]),"partonCategory==0")
        hMassInclusive = a.DataFrame.Histo1D(('{0}_unmatched_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCutunm_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_unmatched_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCutunm_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_unmatched_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)
        histos.append(hMassInclusive)
    else:
        hMassInclusive = a.DataFrame.Histo1D(('{0}_mSD_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        beforePTcut = a.GetActiveNode()
        hMassLoPT = a.Cut("ptLoCut_{0}".format(pnetTags[i]),"probeJetPt<500 && probeJetPt>300").DataFrame.Histo1D(('{0}_mSD_pTLo_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        a.SetActiveNode(beforePTcut)
        hMassHiPT = a.Cut("ptHiCut_{0}".format(pnetTags[i]),"probeJetPt>500").DataFrame.Histo1D(('{0}_mSD_pTHi_{1}'.format(options.process,pnetTags[i]),';mSD [GeV];Jets/10 GeV;',30,0,300),"probeJetMass")
        histos.append(hMassLoPT)
        histos.append(hMassHiPT)
        histos.append(hMassInclusive)


in_f = ROOT.TFile(options.input)
for key in in_f.GetListOfKeys():
    h = key.ReadObj()
    hName = h.GetName()
    if(hName=="Events"):
        continue
    if("cutflow" in hName.lower()):
        h.SetDirectory(0)
        h.SetName(h.GetName()+"_nom")
        histos.append(h)


out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()

