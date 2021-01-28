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
parser.add_option('-w', '--wp', metavar='working points',nargs=2, action="store", type=float,
                default   =   (0.8,0.9),
                dest      =   'wps',
                help      =   'Loose and tight working points')


(options, args) = parser.parse_args()
variation = options.variation
iFile = options.input
if not variation in iFile:
    iFile = iFile.replace(".root","_{0}.root".format(variation))
    print("{0} not in {1}, swapping input to {2}".format(variation,options.input,iFile))


a = analyzer(iFile)
pnetHLo = 0.0
pnetT   = options.wps[1]
pnetL   = options.wps[0]
year    = options.year
histos=[]
if("data" in options.process.lower() or "jetht" in options.process.lower()):
    isData=True
else:
    isData=False

if not isData:
    triggerCorr = Correction('triggerCorrection',"TIMBER/Framework/src/EffLoader.cc",constructor=['"TIMBER/TIMBER/data/TriggerEffs/TriggerEffs.root"','"triggEff_{0}"'.format(year)],corrtype='weight')
    a.AddCorrection(triggerCorr, evalArgs={'xval':'MJJ','yval':0,'zval':0})
a.MakeWeightCols()

a.Define("VRpassT","pnetH>{0} && pnetH<{1} && pnetY>{1}".format(pnetHLo,pnetT))#validation region
a.Define("VRpassL","pnetH>{0} && pnetH<{1} && pnetY>{1} && pnetY<{2}".format(pnetHLo,pnetL,pnetT))#validation region
a.Define("VRfail","pnetH>{0} && pnetH<{1} && pnetY<{1}".format(pnetHLo,pnetL))#validation region
a.Define("TT","pnetH>{0} && pnetY>{0}".format(pnetT))#signal region
a.Define("LL","pnetH>{0} && pnetY>{0} && !(TT)".format(pnetL))#signal region
a.Define("AT","pnetH>{0} && pnetY<{0}".format(pnetL))#anti-tag region
a.Define("ATT","pnetH>{0} && pnetY<{1}".format(pnetT,pnetL))#anti-tag tight region

preDeltaEta = a.GetActiveNode()
#Delta Eta signal region
a.Cut("DeltaEtaSR","DeltaEta<1.3")
nDeltaEta        = a.GetActiveNode().DataFrame.Count().GetValue()
preMJY  = a.GetActiveNode()
a.Cut("MJY_SR","MJY>60")

checkpoint       = a.GetActiveNode()
a.Cut("VRpassTCut","VRpassT==1")
h2DVRT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_VRT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRT)
nVRP = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("VRpassLCut","VRpassL==1")
h2DVRL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_VRL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRL)

a.SetActiveNode(checkpoint)
a.Cut("VRfailCut","VRfail==1")
h2DVRfail  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_VRF'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRfail)
nVRF = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("TTcut","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DTT)
nTT = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("LLcut","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DLL)
nLL = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("ATcut","AT==1")
h2DAT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DAT)
nAT = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("ATTcut","ATT==1")
h2DATT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ATT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DATT)

#MJY<60 GeV sideband
a.SetActiveNode(preMJY)
a.Cut("MJY_MSB_DeltaEta","MJY<60 && MJY>30")
checkpoint       = a.GetActiveNode()
a.Cut("VRpassTCut_MSB","VRpassT==1")
h2DVRT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_VRT'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRT)

a.SetActiveNode(checkpoint)
a.Cut("VRpassLCut_MSB","VRpassL==1")
h2DVRL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_VRL'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRL)

a.SetActiveNode(checkpoint)
a.Cut("VRfailCut_MSB","VRfail==1")
h2DVRfail  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_VRF'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRfail)

a.SetActiveNode(checkpoint)
a.Cut("TTcut_MSB","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DTT)

a.SetActiveNode(checkpoint)
a.Cut("LLcut_MSB","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DLL)

a.SetActiveNode(checkpoint)
a.Cut("ATcut_MSB","AT==1")
h2DAT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_AT'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DAT)

a.SetActiveNode(checkpoint)
a.Cut("ATTcut_MSB","ATT==1")
h2DATT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_MSB_ATT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DATT)


a.SetActiveNode(preDeltaEta)
#Delta eta sideband
a.Cut("DeltaEtaSB","DeltaEta>1.5")
preMJY  = a.GetActiveNode()
a.Cut("MJY_ESB","MJY>60")
checkpoint = a.GetActiveNode()

a.Cut("VRpassCutT_ESB","VRpassT==1")
h2DVRT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_VRT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRT)

a.SetActiveNode(checkpoint)
a.Cut("VRpassCutL_ESB","VRpassL==1")
h2DVRL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_VRL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRL)

a.SetActiveNode(checkpoint)
a.Cut("VRfailCut_ESB","VRfail==1")
h2DVRfail  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_VRF'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRfail)

a.SetActiveNode(checkpoint)
a.Cut("TTcut_ESB","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DTT)

a.SetActiveNode(checkpoint)
a.Cut("LLcut_ESB","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DLL)

a.SetActiveNode(checkpoint)
a.Cut("ATcut_ESB","AT==1")
h2DAT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_AT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DAT)

a.SetActiveNode(checkpoint)
a.Cut("ATTcut_ESB","ATT==1")
h2DATT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_ATT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DATT)

a.SetActiveNode(preMJY)
a.Cut("MJY_DeltaEta","MJY<60 && MJY>30")
checkpoint = a.GetActiveNode()

a.Cut("VRpassCutT_ESB_MSB","VRpassT==1")
h2DVRT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_VRT'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRT)

a.SetActiveNode(checkpoint)
a.Cut("VRpassCutL_ESB_MSB","VRpassL==1")
h2DVRL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_VRL'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRL)

a.SetActiveNode(checkpoint)
a.Cut("VRfailCut_ESB_MSB","VRfail==1")
h2DVRfail  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_VRF'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DVRfail)

a.SetActiveNode(checkpoint)
a.Cut("TTcut_ESB_MSB","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DTT)

a.SetActiveNode(checkpoint)
a.Cut("LLcut_ESB_MSB","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DLL)

a.SetActiveNode(checkpoint)
a.Cut("ATcut_ESB_MSB","AT==1")
h2DAT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_AT'.format(options.process),';mJY [GeV];mJJ [GeV];',3,30,60,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DAT)

a.SetActiveNode(checkpoint)
a.Cut("ATTcut_ESB_MSB","ATT==1")
h2DATT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_ESB_MSB_ATT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","weight__nominal")
histos.append(h2DATT)

if(isData):
    nTT = 0
    nLL = 0
#include histos from evt sel in the template file for nominal template
if(options.variation=="nom"):
    in_f = ROOT.TFile(iFile)
    for key in in_f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        if(hName=="Events"):
            continue
        h.SetDirectory(0)
        if("cutflow" in hName.lower()):
            h.SetBinContent(h.GetNbinsX(),nVRF)
            h.SetBinContent(h.GetNbinsX()-1,nVRP)
            h.SetBinContent(h.GetNbinsX()-2,nAT)
            h.SetBinContent(h.GetNbinsX()-3,nLL)
            h.SetBinContent(h.GetNbinsX()-4,nTT)
            h.SetBinContent(h.GetNbinsX()-5,nDeltaEta)
            h.GetXaxis().SetBinLabel(h.GetNbinsX(),"VR_F")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-1,"VR_P")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-2,"SR_AT")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-3,"SR_LL")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-4,"SR_TT")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-5,"DeltaEta < 1.3")
        histos.append(h)

out_f = ROOT.TFile(options.output,options.mode)
out_f.cd()
for h in histos:
    h.SetName(h.GetName()+"_"+options.variation)
    h.Write()
out_f.Close()

#a.PrintNodeTree('test.ps')
