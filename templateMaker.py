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
                help      =   'A root file to analyze')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('-p', '--process', metavar='PROCESS', type='string', action='store',
                default   =   'X1600_Y100',
                dest      =   'process',
                help      =   'Process in the given file')
parser.add_option('-v','--var', metavar='variation', type='string', action='store',
                default   =   "nom",
                dest      =   'variation',
                help      =   'jmrUp/Down, jmsUp/Down, jesUp/Down, jerUp/Down')
parser.add_option('-m', metavar='mode', type='string', action='store',
                default   =   "RECREATE",
                dest      =   'mode',
                help      =   'RECREATE or UPDATE outputfile')



variation = options.variation
(options, args) = parser.parse_args()
a = analyzer(options.input)
pnetHLo = 0.0
pnetT   = 0.90
pnetL   = 0.8
year    = options.year
histos=[]
if("data" in options.process.lower() or "jetht" in options.process.lower()):
    isData=True
else:
    isData=False

if not isData:
    triggerCorr = Correction('triggerCorrection',"TIMBER/Framework/src/EffLoader.cc",constructor=['"TIMBER/TIMBER/data/TriggerEffs/TriggerEffs.root"','"triggEff_{0}"'.format(year)],corrtype='weight')
    a.AddCorrection(triggerCorr, evalArgs={'xval':'mjjHY','yval':0,'zval':0})
a.MakeWeightCols()

a.Define("VRpass","pnetH>{0} && pnetH<{1} && pnetY>{1}".format(pnetHLo,pnetL))#validation region
a.Define("VRfail","pnetH>{0} && pnetH<{1} && pnetY<{1}".format(pnetHLo,pnetL))#validation region
a.Define("TT","pnetH>{0} && pnetY>{0}".format(pnetT))#signal region
a.Define("LL","pnetH>{0} && pnetY>{0} && !(TT)".format(pnetL))#signal region
a.Define("AT","pnetH>{0} && pnetY<{0}".format(pnetL))#anti-tag region
checkpoint = a.GetActiveNode()

a.Cut("VRpassCut","VRpass==1")
h2DVRpass  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_VRP'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,20,1000.,3000.),"mjY","mjjHY","weight__nominal")
hMJVRpass  = a.DataFrame.Histo1D(('{0}_mJY_VRP'.format(options.process),';mJY [GeV];;',15,60,360),"mjY","weight__nominal")
hMJJVRpass = a.DataFrame.Histo1D(('{0}_mJJ_VRP'.format(options.process),';mJJ [GeV];;',20,1000.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DVRpass,hMJVRpass,hMJJVRpass])
nVRP = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("VRfailCut","VRfail==1")
h2DVRfail  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_VRF'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,20,1000.,3000.),"mjY","mjjHY","weight__nominal")
hMJVRfail  = a.DataFrame.Histo1D(('{0}_mJY_VRF'.format(options.process),';mJY [GeV];;',15,60,360),"mjY","weight__nominal")
hMJJVRfail = a.DataFrame.Histo1D(('{0}_mJJ_VRF'.format(options.process),';mJJ [GeV];;',20,1000.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DVRfail,hMJVRfail,hMJJVRfail])
nVRF = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("TTcut","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,20,1000.,3000.),"mjY","mjjHY","weight__nominal")
hMJTT  = a.DataFrame.Histo1D(('{0}_mJY_TT'.format(options.process),';mJY [GeV];;',15,60,360),"mjY","weight__nominal")
hMJJTT = a.DataFrame.Histo1D(('{0}_mJJ_TT'.format(options.process),';mJJ [GeV];;',20,1000.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DTT,hMJTT,hMJJTT])
nTT = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("LLcut","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,20,1000.,3000.),"mjY","mjjHY","weight__nominal")
hMJLL  = a.DataFrame.Histo1D(('{0}_mJY_LL'.format(options.process),';mJY [GeV];;',15,60,360),"mjY","weight__nominal")
hMJJLL = a.DataFrame.Histo1D(('{0}_mJJ_LL'.format(options.process),';mJJ [GeV];;',20,1000.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DLL,hMJLL,hMJJLL])
nLL = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("ATcut","AT==1")
h2DAT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,20,1000.,3000.),"mjY","mjjHY","weight__nominal")
hMJAT  = a.DataFrame.Histo1D(('{0}_mJY_AT'.format(options.process),';mJY [GeV];;',15,60,360),"mjY","weight__nominal")
hMJJAT = a.DataFrame.Histo1D(('{0}_mJJ_AT'.format(options.process),';mJJ [GeV];;',20,1000.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DAT,hMJAT,hMJJAT])
nAT = a.GetActiveNode().DataFrame.Count().GetValue()

if(isData):
    nTT = 0
    nLL = 0
#include histos from evt sel in the template file for nominal template
if(options.variation=="nom")
    in_f = ROOT.TFile(options.input)
    for key in in_f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        if(hName=="Events"):
            continue
        h.SetDirectory(0)
        if("cutflow" in hName.lower()):
            h.SetBinContent(h.GetNbinsX(),nVRF)
            h.SetBinContent(h.GetNbinsX()-1,nVRP)
            h.SetBinContent(h.GetNbinsX()-2,nLL)
            h.SetBinContent(h.GetNbinsX()-3,nTT)
            h.GetXaxis().SetBinLabel(h.GetNbinsX(),"VR_F")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-1,"VR_P")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-2,"SR_LL")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-3,"SR_TT")
        histos.append(h)

out_f = ROOT.TFile(options.output,options.mode)
out_f.cd()
for h in histos:
    h.SetName(h.GetName()+options.variation)
    h.Write()
out_f.Close()
