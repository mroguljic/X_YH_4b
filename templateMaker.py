#To be used with trees from event selection
import ROOT as r
import time, os
import sys
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

def getNweighted(analyzer,isData):
    if not isData:
        nWeighted = a.DataFrame.Sum("genWeight").GetValue()
    else:
        nWeighted = a.DataFrame.Count().GetValue()
    return nWeighted


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
                help      =   'jer, jes, jmr, jms, trigger, pnet (Up/Down)')
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
    triggerCorr = Correction('triggerCorrection',"TIMBER/Framework/src/EffLoader.cc",constructor=['"../TIMBER/TIMBER/data/TriggerEffs/TriggerEffs.root"','"triggEff_{0}"'.format(year)],corrtype='weight')
    a.AddCorrection(triggerCorr, evalArgs={'xval':'MJJ','yval':0,'zval':0})

if isData:
    a.Define("genWeight","1")


a.MakeWeightCols()

weightString = "weight__nominal"
if("trig" in variation):
    if(variation=="trigUp"):
        weightString = "weight__triggerCorrection_up"
    if(variation=="trigDown"):
        weightString = "weight__triggerCorrection_down"

a.Define("evtWeight","genWeight*{0}".format(weightString))


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
    a.Define("ScaledPnetH","btagHandler.updateTaggingCategories(TaggerCatH,ptjH)")
    a.Define("ScaledPnetY","btagHandler.updateTaggingCategories(TaggerCatY,ptjY)")
else:
    a.Define("ScaledPnetH","TaggerCatH")
    a.Define("ScaledPnetY","TaggerCatY")

a.Define("AL_T","ScaledPnetH==0 && ScaledPnetY==2")#validation region
a.Define("AL_L","ScaledPnetH==0 && ScaledPnetY==1")
a.Define("AL_AL","ScaledPnetH==0 && ScaledPnetY==0")
a.Define("TT","ScaledPnetH==2 && ScaledPnetY==2")#signal region
a.Define("LL","ScaledPnetH>0 && ScaledPnetY>0 && !(TT)")
a.Define("L_AL","ScaledPnetH>0 && ScaledPnetY==0")
a.Define("T_AL","ScaledPnetH==2 && ScaledPnetY==0")

a.Define("NAL_T","ScaledPnetH==0 && ScaledPnetY==2 && pnetH>0.6")#Narrow validation region
a.Define("NAL_L","ScaledPnetH==0 && ScaledPnetY==1 && pnetH>0.6")
a.Define("NAL_AL","ScaledPnetH==0 && ScaledPnetY==0 && pnetH>0.6")
#Delta Eta cut
a.Cut("DeltaEtaSR","DeltaEta<1.3")
nDeltaEta  = getNweighted(a,isData)
if("TTbar" in options.process):
    hMTT  = a.DataFrame.Histo1D(('{0}_MTT'.format(options.process),';M_{TT} [GeV];;',30,0,3000.),"MTT","evtWeight")
    histos.append(hMTT)

a.Cut("MJY_SR","MJY>60")

checkpoint = a.GetActiveNode()
a.Cut("AL_TCut","AL_T==1")
h2DAL_T  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AL_T'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DAL_T)
nAL_T = getNweighted(a,isData)

a.SetActiveNode(checkpoint)
a.Cut("AL_LCut","AL_L==1")
h2DAL_L  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AL_L'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DAL_L)
nAL_L = getNweighted(a,isData)

a.SetActiveNode(checkpoint)
a.Cut("AL_ALCut","AL_AL==1")
h2DAL_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_AL_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DAL_AL)
nAL_AL = getNweighted(a,isData)

a.SetActiveNode(checkpoint)
a.Cut("TTcut","TT==1")
h2DTT  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_TT'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DTT)
nTT = getNweighted(a,isData)

a.SetActiveNode(checkpoint)
a.Cut("LLcut","LL==1")
h2DLL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_LL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DLL)
nLL = getNweighted(a,isData)

a.SetActiveNode(checkpoint)
a.Cut("L_ALcut","L_AL==1")
h2DL_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_L_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DL_AL)
nL_AL = getNweighted(a,isData)

a.SetActiveNode(checkpoint)
a.Cut("T_ALcut","T_AL==1")
h2DT_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_T_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DT_AL)

#Narrow validation region
a.SetActiveNode(checkpoint)
a.Cut("NAL_TCut","NAL_T==1")
h2DNAL_T  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_NAL_T'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DNAL_T)
nNAL_T = a.GetActiveNode().DataFrame.Count().GetValue()

a.SetActiveNode(checkpoint)
a.Cut("NAL_LCut","NAL_L==1")
h2DNAL_L  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_NAL_L'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DNAL_L)

a.SetActiveNode(checkpoint)
a.Cut("NAL_ALCut","NAL_AL==1")
h2DNAL_AL  = a.DataFrame.Histo2D(('{0}_mJY_mJJ_NAL_AL'.format(options.process),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
histos.append(h2DNAL_AL)



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
            #"DeltaEta","TT","LL","L_AL","AL_T","AL_L","AL_AL"
            h.SetBinContent(h.GetNbinsX(),nAL_AL)
            h.SetBinContent(h.GetNbinsX()-1,nAL_L)
            h.SetBinContent(h.GetNbinsX()-2,nAL_T)
            h.SetBinContent(h.GetNbinsX()-3,nL_AL)
            h.SetBinContent(h.GetNbinsX()-4,nLL)
            h.SetBinContent(h.GetNbinsX()-5,nTT)
            h.SetBinContent(h.GetNbinsX()-6,nDeltaEta)
            h.GetXaxis().SetBinLabel(h.GetNbinsX()-6,"DeltaEta < 1.3")
        histos.append(h)

out_f = ROOT.TFile(options.output,options.mode)
out_f.cd()
for h in histos:
    h.SetName(h.GetName()+"_"+options.variation)
    h.Write()
out_f.Close()

#a.PrintNodeTree('test.ps')
