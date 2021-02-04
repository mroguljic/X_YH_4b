#To be used with trees from event selection
import ROOT as r
import time, os
import sys
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
                default   =   (0.8,0.95),
                dest      =   'wps',
                help      =   'Loose and tight working points')


(options, args) = parser.parse_args()
variation = options.variation
iFile = options.input
if not variation in iFile:
    if("je" in variation or "jm" in variation):
        iFile = iFile.replace(".root","_{0}.root".format(variation))
        print("{0} not in {1}, swapping input to {2}".format(variation,options.input,iFile))
    else:
        if not("nom" in iFile):
            iFile = iFile.replace(".root","_nom.root")


if("MX" not in options.process and "pnet" in options.variation):
    sys.exit()
    #Running pnet shape unc for signal only

a = analyzer(iFile)
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
weightString = "weight__nominal"
if("trig" in variation):
    if(variation=="trigUp"):
        weightString = "triggerCorrection__up"
    if(variation=="trigDown"):
        weightString = "triggerCorrection__down"

CompileCpp('TIMBER/Framework/src/btagSFHandler.cc')
if(variation=="pnetUp"):
    pnetVar=2
elif(variation=="pnetDown"):
    pnetVar=1
else:
    pnetVar = 0
CompileCpp('btagSFHandler btagHandler = btagSFHandler({%f,%f},{0.73,0.53},%s,%i);' %(pnetL,pnetT,year,pnetVar))#wps, efficiencies, year, var
a.Define("TaggerCatH","btagHandler.createTaggingCategories(pnetH)")
a.Define("TaggerCatY","btagHandler.createTaggingCategories(pnetY)")
if("MX" in options.process):
    a.Define("ScaledPnetH","btagHandler.updateTaggingCategories(TaggerCatH,ptjH)")#replaced 450.0 with Pt!
    a.Define("ScaledPnetY","btagHandler.updateTaggingCategories(TaggerCatY,ptjY)")#replaced 450.0 with Pt!
else:
    a.Define("ScaledPnetH","TaggerCatH")
    a.Define("ScaledPnetY","TaggerCatY")
# hTaggerH   = a.DataFrame.Histo1D(('beforeSF','',3,0,3),"TaggerCatH")
# hUpdatedH  = a.DataFrame.Histo1D(('afterSF','',3,0,3),"ScaledPnetH")
# histos.append(hTaggerH)
# histos.append(hUpdatedH)

a.Define("AL_T","ScaledPnetH==0 && ScaledPnetY==2")#validation region
a.Define("AL_L","ScaledPnetH==0 && ScaledPnetY==1")
a.Define("AL_AL","ScaledPnetH==0 && ScaledPnetY==0")
a.Define("TT","ScaledPnetH==2 && ScaledPnetY==2")#signal region
a.Define("LL","ScaledPnetH>0 && ScaledPnetY>0 && !(TT)")
a.Define("L_AL","ScaledPnetH>0 && ScaledPnetY==0")
a.Define("T_AL","ScaledPnetH==2 && ScaledPnetY==0")

#Delta Eta cut
a.Cut("DeltaEtaSR","DeltaEta<1.3")
nDeltaEta        = a.GetActiveNode().DataFrame.Count().GetValue()
a.Cut("MJY_SR","MJY>60")

checkpoint       = a.GetActiveNode()
a.Cut("AL_TCut","AL_T==1")
h2DAL_T  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AL_T'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DAL_T)
nAL_T = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("AL_LCut","AL_L==1")
h2DAL_L  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AL_L'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DAL_L)

a.SetActiveNode(checkpoint)
a.Cut("AL_ALCut","AL_AL==1")
h2DAL_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AL_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DAL_AL)
nAL_AL = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("TTcut","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DTT)
nTT = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("LLcut","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DLL)
nLL = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("L_ALcut","L_AL==1")
h2DL_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_L_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DL_AL)
nL_AL = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("T_ALcut","T_AL==1")
h2DT_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_T_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ",weightString)
histos.append(h2DT_AL)



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
            h.SetBinContent(h.GetNbinsX(),nAL_AL)
            h.SetBinContent(h.GetNbinsX()-1,nAL_T)
            h.SetBinContent(h.GetNbinsX()-2,nL_AL)
            h.SetBinContent(h.GetNbinsX()-3,nLL)
            h.SetBinContent(h.GetNbinsX()-4,nTT)
            h.SetBinContent(h.GetNbinsX()-5,nDeltaEta)
            h.GetXaxis().SetBinLabel(h.GetNbinsX(),"AL_AL")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-1,"AL_L")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-2,"L_AL")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-3,"LL")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-4,"TT")
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-5,"DeltaEta < 1.3")
        histos.append(h)

out_f = ROOT.TFile(options.output,options.mode)
out_f.cd()
for h in histos:
    h.SetName(h.GetName()+"_"+options.variation)
    h.Write()
out_f.Close()

#a.PrintNodeTree('test.ps')
