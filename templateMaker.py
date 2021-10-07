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
        hist = analyzer.DataFrame.Histo2D(('{0}_{1}_mJY_mJJ_{2}'.format(process,cat,region),';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY_recalc","MJJ","evtWeight")
        separatedHistos.append(hist)
    analyzer.SetActiveNode(beforeNode)
    return separatedHistos

def getTaggingEfficiencies(analyzer,wpL,wpT,scalar="H"):
    beforeNode = analyzer.GetActiveNode()
    nTot = analyzer.DataFrame.Sum("genWeight").GetValue()
    analyzer.Cut("Eff_L_{0}_cut".format(scalar),"pnet{2}>{0} && pnet{2}<{1}".format(wpL,wpT,scalar))
    nL   = analyzer.DataFrame.Sum("genWeight").GetValue()
    analyzer.SetActiveNode(beforeNode)
    analyzer.Cut("Eff_T_{0}_cut".format(scalar),"pnet{1}>{0}".format(wpT,scalar))
    nT   = analyzer.DataFrame.Sum("genWeight").GetValue()
    effL = nL/nTot
    effT = nT/nTot
    analyzer.SetActiveNode(beforeNode)
    return effL, effT


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
                default   =   (0.94,0.98),
                dest      =   'wps',
                help      =   'Loose and tight working points')


(options, args) = parser.parse_args()
variation = options.variation
iFile = options.input
if not variation in iFile:
    if("je" in variation or "jm" in variation):
        if("jmspt" in variation):
            iFile = iFile.replace(".root","_{0}.root".format(variation.replace("pt","")))
        else:
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
    puCorr      = Correction('puReweighting',"TIMBER/Framework/src/puWeight.cc",constructor=['"../TIMBER/TIMBER/data/pileup/PUweights_{0}.root"'.format(year)],corrtype='weight')
    a.AddCorrection(puCorr, evalArgs={'puTrue':'Pileup_nTrueInt'})
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
if("puRwt" in variation):
    if(variation=="puRwtUp"):
        weightString = "weight__puReweighting_up"
    if(variation=="puRwtDown"):
        weightString = "weight__puReweighting_down"

if(year=="2018"):
    #a.Define("evtWeight","genWeight*HEMweight*{0}".format(weightString)) #uncomment when trees with HEM weights are calculated
    a.Define("evtWeight","genWeight*{0}".format(weightString))
else:
    a.Define("evtWeight","genWeight*{0}".format(weightString))

CompileCpp('TIMBER/Framework/src/btagSFHandler.cc')
if(variation=="pnetUp"):
    pnetVar=2
elif(variation=="pnetDown"):
    pnetVar=1
else:
    pnetVar = 0

effH_L = 0.20#placeholder values
effH_T = 0.30
effY_L = 0.20#placeholder values
effY_T = 0.30
if("MX" in options.process):
    effH_L, effH_T = getTaggingEfficiencies(a,pnetL,pnetT,scalar="H")#calculate efficiencies for Hjets
    effY_L, effY_T = getTaggingEfficiencies(a,pnetL,pnetT,scalar="Y")#calculate efficiencies for Yjets  
    print("{0} ParticleNet (L,T) H-efficiencies: ({1:.2f},{2:.2f})".format(options.process,effH_L,effH_T))
    print("{0} ParticleNet (L,T) Y-efficiencies: ({1:.2f},{2:.2f})".format(options.process,effY_L,effY_T))

CompileCpp('btagSFHandler btagHandlerH = btagSFHandler({%f,%f},{%f,%f},%s,%i);' %(pnetL,pnetT,effH_L,effH_T,year,pnetVar))#wps, efficiencies, year, var
CompileCpp('btagSFHandler btagHandlerY = btagSFHandler({%f,%f},{%f,%f},%s,%i);' %(pnetL,pnetT,effY_L,effY_T,year,pnetVar))#wps, efficiencies, year, var


a.Define("TaggerCatH","btagHandlerH.createTaggingCategories(pnetH)")
a.Define("TaggerCatY","btagHandlerY.createTaggingCategories(pnetY)")
if("MX" in options.process):
    a.Define("ScaledPnetH","btagHandlerH.updateTaggingCategories(TaggerCatH,ptjH)")
    a.Define("ScaledPnetY","btagHandlerY.updateTaggingCategories(TaggerCatY,ptjY)")
else:
    a.Define("ScaledPnetH","TaggerCatH")
    a.Define("ScaledPnetY","TaggerCatY")



regionDefs = [("AL_T","ScaledPnetH==0 && ScaledPnetY==2"),("AL_L","ScaledPnetH==0 && ScaledPnetY==1"),("AL_AL","ScaledPnetH==0 && ScaledPnetY==0"),
("TT","ScaledPnetH==2 && ScaledPnetY==2"),("LL","ScaledPnetH>0 && ScaledPnetY>0 && !(TT)"),("L_AL","ScaledPnetH>0 && ScaledPnetY==0"),("T_AL","ScaledPnetH==2 && ScaledPnetY==0"),
("NAL_T","ScaledPnetH==0 && ScaledPnetY==2 && pnetH>0.8"),("NAL_L","ScaledPnetH==0 && ScaledPnetY==1 && pnetH>0.8"),("NAL_AL","ScaledPnetH==0 && ScaledPnetY==0 && pnetH>0.8"),
("WAL_T","ScaledPnetH==0 && ScaledPnetY==2 && pnetH>0.6 && pnetH<0.8"),("WAL_L","ScaledPnetH==0 && ScaledPnetY==1 && pnetH>0.6 && pnetH<0.8"),("WAL_AL","ScaledPnetH==0 && ScaledPnetY==0 && pnetH>0.6 && pnetH<0.8")]#TT needs to be defined before LL which is why we're using something that's ordered (list)
regionYields = {}


#Delta Eta cut
a.Cut("DeltaEtaSR","DeltaEta<1.3")
nDeltaEta  = getNweighted(a,isData)
# if("TTbar" in options.process):
#     hMTT  = a.DataFrame.Histo1D(('{0}_MTT'.format(options.process),';M_{TT} [GeV];;',30,0,3000.),"MTT","evtWeight")
#     histos.append(hMTT)

if("TTbar" in options.process and "jmspt" in options.variation):
    #recalculate 300 according to pt-dependent jms for bqq
    CompileCpp("TIMBER/Framework/src/JMSUncShifter.cc") 
    CompileCpp("JMSUncShifter jmsShifter = JMSUncShifter();") 
    if(options.variation=="jmsptUp"):
        a.Define("MJY_recalc","jmsShifter.ptDependentJMS(MJY,ptjY,1,jetCatY)")
    elif(options.variation=="jmsptDown"):
        a.Define("MJY_recalc","jmsShifter.ptDependentJMS(MJY,ptjY,-1,jetCatY)")
    else:
        print("JMS uncertainty unkown")
        sys.exit()
else:
    a.Define("MJY_recalc","MJY")


a.Cut("MJY_SR","MJY_recalc>60")

if variation=="nom":
    if not isData:
        a.MakeWeightCols('noPUrwt',dropList=["puReweighting"])
        a.Define("noPUrwt_weight","genWeight*weight_noPUrwt__nominal")
        hnPVnoRwt = a.DataFrame.Histo1D(('{0}_nPV_noRwt'.format(options.process),';nPV;;',60,0,60.),"PV_npvsGood","noPUrwt_weight")
        histos.append(hnPVnoRwt)

    hnPV = a.DataFrame.Histo1D(('{0}_nPV'.format(options.process),';nPV;;',60,0,60.),"PV_npvsGood","evtWeight")
    histos.append(hnPV)



if("puRwt" in variation):
    hnPV = a.DataFrame.Histo1D(('{0}_nPV'.format(options.process),';nPV;;',60,0,60.),"PV_npvsGood","evtWeight")
    histos.append(hnPV)

for region,cut in regionDefs:
    a.Define(region,cut)

checkpoint = a.GetActiveNode()

for region,cut in regionDefs:
    a.SetActiveNode(checkpoint)
    a.Cut("{0}_cut".format(region),cut)
    h2d = a.DataFrame.Histo2D(('{0}_mJY_mJJ_{1}'.format(options.process,region),';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY_recalc","MJJ","evtWeight")
    histos.append(h2d)
    regionYields[region] = getNweighted(a,isData)
    if("TTbar" in options.process):
        categorizedHistos = separateTopHistos(a,options.process,region)
        histos.extend(categorizedHistos)
        h2d_pt = a.DataFrame.Histo2D(('{0}_mJY_pT_{1}'.format(options.process,region),';mJY [GeV];pT [GeV];',15,60,360,17,300.,2000.),"MJY_recalc","ptjY","evtWeight")
        histos.append(h2d_pt)


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
