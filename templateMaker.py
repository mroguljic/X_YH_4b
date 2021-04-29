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
        nWeighted = analyzer.DataFrame.Sum("genWeight").GetValue()
    else:
        nWeighted = analyzer.DataFrame.Count().GetValue()
    return nWeighted

def separateTopHistos(analyzer,process,region):
    cats = {"unm":0,"qq":1,"bq":2,"bqq":3}

    separatedHistos = []
    beforeNode = analyzer.GetActiveNode()
    for cat in cats:
        analyzer.SetActiveNode(beforeNode)
        analyzer.Cut("{0}_{1}_{2}_cut".format(process,cat,region),"jetCatY=={0}".format(cats[cat]))
        hist = analyzer.DataFrame.Histo2D(('{0}_{1}_mJY_mJJ_{2}'.format(process,cat,region),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
        separatedHistos.append(hist)
    analyzer.SetActiveNode(beforeNode)
    return separatedHistos



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
    if("TTbar" in options.process):
        ptrwtCorr = Correction('topPtReweighting',"TIMBER/Framework/src/TopPt_reweighting.cc",corrtype='weight')
        a.AddCorrection(ptrwtCorr, evalArgs={'genTPt':'topPt','genTbarPt':'antitopPt'})

if isData:
    a.Define("genWeight","1")


a.MakeWeightCols()

weightString = "weight__nominal"
if("trig" in variation):
    if(variation=="trigUp"):
        weightString = "weight__triggerCorrection_up"
    if(variation=="trigDown"):
        weightString = "weight__triggerCorrection_down"
if("ptRwt" in variation):
    if(variation=="ptRwtUp"):
        weightString = "weight__topPtReweighting_up"
    if(variation=="ptRwtDown"):
        weightString = "weight__topPtReweighting_down"

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



regionDefs = [("AL_T","ScaledPnetH==0 && ScaledPnetY==2"),("AL_L","ScaledPnetH==0 && ScaledPnetY==1"),("AL_AL","ScaledPnetH==0 && ScaledPnetY==0"),
("TT","ScaledPnetH==2 && ScaledPnetY==2"),("LL","ScaledPnetH>0 && ScaledPnetY>0 && !(TT)"),("L_AL","ScaledPnetH>0 && ScaledPnetY==0"),("T_AL","ScaledPnetH==2 && ScaledPnetY==0"),
("NAL_T","ScaledPnetH==0 && ScaledPnetY==2 && pnetH>0.6"),("NAL_L","ScaledPnetH==0 && ScaledPnetY==1 && pnetH>0.6"),("NAL_AL","ScaledPnetH==0 && ScaledPnetY==0 && pnetH>0.6"),
("WAL_T","ScaledPnetH==0 && ScaledPnetY==2 && pnetH>0.2"),("WAL_L","ScaledPnetH==0 && ScaledPnetY==1 && pnetH>0.2"),("WAL_AL","ScaledPnetH==0 && ScaledPnetY==0 && pnetH>0.2")]#TT needs to be defined before LL which is why we're using something that's ordered (list)
regionYields = {}


#Delta Eta cut
a.Cut("DeltaEtaSR","DeltaEta<1.3")
nDeltaEta  = getNweighted(a,isData)
if("TTbar" in options.process):
    hMTT  = a.DataFrame.Histo1D(('{0}_MTT'.format(options.process),';M_{TT} [GeV];;',30,0,3000.),"MTT","evtWeight")
    histos.append(hMTT)

a.Cut("MJY_SR","MJY>60")

for region,cut in regionDefs:
    a.Define(region,cut)

checkpoint = a.GetActiveNode()

for region,cut in regionDefs:
    a.SetActiveNode(checkpoint)
    a.Cut("{0}_cut".format(region),cut)
    h2d = a.DataFrame.Histo2D(('{0}_mJY_mJJ_{1}'.format(options.process,region),';mJY [GeV];mJJ [GeV];',15,60,360,22,800.,3000.),"MJY","MJJ","evtWeight")
    histos.append(h2d)
    regionYields[region] = getNweighted(a,isData)
    if("TTbar" in options.process):
        categorizedHistos = separateTopHistos(a,options.process,region)
        histos.extend(categorizedHistos)


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
            h.SetBinContent(h.GetNbinsX(),regionYields["AL_AL"])
            h.SetBinContent(h.GetNbinsX()-1,regionYields["AL_L"])
            h.SetBinContent(h.GetNbinsX()-2,regionYields["AL_T"])
            h.SetBinContent(h.GetNbinsX()-3,regionYields["L_AL"])
            h.SetBinContent(h.GetNbinsX()-4,regionYields["LL"])
            h.SetBinContent(h.GetNbinsX()-5,regionYields["TT"])
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
