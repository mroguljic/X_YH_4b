import ROOT

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *
import sys
import pickle



parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')

(options, args) = parser.parse_args()
start_time = time.time()
year = options.year

CompileCpp('TIMBER/Framework/massMatching.cc') 
CompileCpp('TIMBER/Framework/src/PDFweight_uncert.cc') 
CompileCpp("TIMBER/Framework/common.cc") 
CompileCpp("TIMBER/Framework/deltaRMatching.cc") 
CompileCpp("TIMBER/Framework/taggerOrdering.cc") 
CompileCpp("TIMBER/Framework/helperFunctions.cc") 

a = analyzer(options.input)


if(year=="2016"):
    YMass = options.input.split("_")[1]
    YMass = YMass.replace("MY","")
    YMass = YMass.replace(".txt","")
    print("Cutting on MY={0}".format(YMass))
    a.Cut("YMass","GenModel_YMass_{0}==1".format(YMass))


#Jet(s) definition
a.Cut("nFatJet","nFatJet>1")
a.Cut("ID","FatJet_jetId[0]>1 && FatJet_jetId[1]>1")#bit 1 is loose, bit 2 is tight, bit3 is tightlepVeto
if(year=="2016"):
    a.Cut("Eta","abs(FatJet_eta[0])<2.4 && abs(FatJet_eta[1])<2.4")
else:
    a.Cut("Eta","abs(FatJet_eta[0])<2.5 && abs(FatJet_eta[1])<2.5")


evtColumns = VarGroup("Event columns")
evtColumns.Add("FatJet_pt0","FatJet_pt[0]")
evtColumns.Add("FatJet_pt1","FatJet_pt[1]")
evtColumns.Add("FatJet_eta0","FatJet_eta[0]")
evtColumns.Add("FatJet_eta1","FatJet_eta[1]")
evtColumns.Add("mSD0","FatJet_msoftdrop[0]")
evtColumns.Add("mSD1","FatJet_msoftdrop[1]")
a.Apply([evtColumns])

a.Cut("mSD0Cut","mSD0>60")
a.Cut("mSD1Cut","mSD1>60")

if(options.year=="2016"):
    a.Cut("pT","FatJet_pt0>350 && FatJet_pt1>350")
else:
    a.Cut("pT","FatJet_pt0>450 && FatJet_pt1>450")

a.Define("nEle","nElectrons(nElectron,Electron_cutBased,0,Electron_pt,20,Electron_eta)")
#0:fail,1:veto,2:loose,3:medium,4:tight
#condition is, cutBased>cut
a.Define("nMu","nMuons(nMuon,Muon_looseId,Muon_pfIsoId,0,Muon_pt,20,Muon_eta)")
#1=PFIsoVeryLoose, 2=PFIsoLoose, 3=PFIsoMedium, 4=PFIsoTight, 5=PFIsoVeryTight, 6=PFIsoVeryVeryTight
#condition is, pfIsoId>cut
a.Cut("LeptonVeto","nMu==0 && nEle==0")
#need to define variables which we want in n-1 histograms
dijetColumns = VarGroup("dijet Columns")
dijetColumns.Add("DeltaEta","abs(FatJet_eta[0] - FatJet_eta[1])")
dijetColumns.Add('LeadingVector', 'analyzer::TLvector(FatJet_pt0,FatJet_eta[0],FatJet_phi[0],mSD0)')
dijetColumns.Add('SubleadingVector',  'analyzer::TLvector(FatJet_pt1,FatJet_eta[1],FatJet_phi[1],mSD1)')
dijetColumns.Add('MJJ',     'analyzer::invariantMass(LeadingVector,SubleadingVector)') 
a.Apply([dijetColumns])
a.Cut("MJJ_cut","MJJ>700")
a.Cut("DeltaEta_cut","DeltaEta < 1.3")
idxColumns = VarGroup("idxColumns")
idxColumns.Add("idxH","higgsMassMatchingAlt(mSD0,mSD1)")
idxColumns.Add("idxY","1-idxH")
idxCuts   = CutGroup("idxCuts")
idxCuts.Add("Higgs-tagged cut","idxH>=0")
a.Apply([idxColumns])
a.Apply([idxCuts])


if(year=="2016"):
    lhaid = 306000#PDFset name stored in branch name, instead of the LHAID
else:
    lhaid = int(a.lhaid)+1#PDFweight branch naming has changed so TIMBER unnecessarily subtracts 1

print("----------USING LHAID: {0}".format(lhaid))

CompileCpp("PDFweight_uncert pdfHandler = PDFweight_uncert({0});".format(lhaid)) 
a.Define("PDFweight","pdfHandler.eval(LHEPdfWeight)")

a.Define("MJY","FatJet_msoftdrop[idxY]")
a.Define("MJH","FatJet_msoftdrop[idxH]")

if(year=="2016"):
    a.Define("pnetH","FatJet_ParticleNetMD_probXbb[idxH]/(FatJet_ParticleNetMD_probXbb[idxH]+FatJet_ParticleNetMD_probQCDb[idxH]+FatJet_ParticleNetMD_probQCDbb[idxH]+FatJet_ParticleNetMD_probQCDc[idxH]+FatJet_ParticleNetMD_probQCDcc[idxH]+FatJet_ParticleNetMD_probQCDothers[idxH])")
    a.Define("pnetY","FatJet_ParticleNetMD_probXbb[idxY]/(FatJet_ParticleNetMD_probXbb[idxY]+FatJet_ParticleNetMD_probQCDb[idxY]+FatJet_ParticleNetMD_probQCDbb[idxY]+FatJet_ParticleNetMD_probQCDc[idxY]+FatJet_ParticleNetMD_probQCDcc[idxY]+FatJet_ParticleNetMD_probQCDothers[idxY])")
else:
    a.Define("pnetH","FatJet_particleNetMD_Xbb[idxH]/(FatJet_particleNetMD_Xbb[idxH]+FatJet_particleNetMD_QCD[idxH])")
    a.Define("pnetY","FatJet_particleNetMD_Xbb[idxY]/(FatJet_particleNetMD_Xbb[idxY]+FatJet_particleNetMD_QCD[idxY])")

a.Define("TT","pnetH>0.98 && pnetY>0.98")
a.Define("LL","pnetH>0.94 && pnetY>0.94 && !(TT)")

a.Define("PDFweight_down","PDFweight[1]")
a.Define("PDFweight_up","PDFweight[0]")

histos = []
checkpoint = a.GetActiveNode()
a.Cut("TT_cut","TT==1")
h_nom = a.DataFrame.Histo2D(('TT_nom',';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY","MJJ")
h_up  = a.DataFrame.Histo2D(('TT_up',';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY","MJJ","PDFweight_up")
h_down  = a.DataFrame.Histo2D(('TT_down',';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY","MJJ","PDFweight_down")
histos.append(h_nom)
histos.append(h_up)
histos.append(h_down)

a.SetActiveNode(checkpoint)
a.Cut("LL_cut","LL==1")
h_nom = a.DataFrame.Histo2D(('LL_nom',';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY","MJJ")
h_up  = a.DataFrame.Histo2D(('LL_up',';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY","MJJ","PDFweight_up")
h_down  = a.DataFrame.Histo2D(('LL_down',';mJY [GeV];mJJ [GeV];',33,60,720,34,800.,4200.),"MJY","MJJ","PDFweight_down")
histos.append(h_nom)
histos.append(h_up)
histos.append(h_down)

f = ROOT.TFile.Open(options.output,"RECREATE")
f.cd()
for h in histos:
    h.Write()
f.Close()
#a.PrintNodeTree('node_tree.dot',verbose=True)
print("Total time: "+str((time.time()-start_time)/60.) + ' min')