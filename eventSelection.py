import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools import CMS_lumi
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
                default   =   'X1600_Y100',
                dest      =   'process',
                help      =   'Process in the given MC file')
parser.add_option('-s', '--sig', action="store_true",dest="isSignal",default=False)
parser.add_option('-b', '--bkg', action="store_false",dest="isSignal",default=False)
parser.add_option('--data',action="store_true",dest="isData",default=False)
parser.add_option('-m', '--massY', metavar='GenY mass (if MC signal)', type=int, action='store',
                default   =   200,
                dest      =   'massY',
                help      =   'Mass of the Y')
parser.add_option('-d', '--outdir', metavar='ODIR', type='string', action='store',
                default   =   '.',
                dest      =   'outdir',
                help      =   'Output directory.')
# parser.add_option('-t', '--tagger', metavar='FatJet_Tagger', type='string', action='store',
#                 default   =   'FatJet_ParticleNetMD_probXbb',
#                 dest      =   'tagger',
#                 help      =   'Name of tagger for jet tagging')
# parser.add_option('--taggerShort', metavar='Short tagger suffix', type='string', action='store',
#                 default   =   'pnet',
#                 dest      =   'taggerShort',
#                 help      =   'Will be pasted at the end of histos')


(options, args) = parser.parse_args()
start_time = time.time()


CompileCpp('/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/massMatching.cc') 
CompileCpp("/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/common.cc") 
CompileCpp("/afs/cern.ch/work/m/mrogulji/X_YH_4b/TIMBER/TIMBER/Framework/deltaRMatching.cc") 


a = analyzer(options.input)
histos      = []
# small_rdf = a.GetActiveNode().DataFrame.Range(1000) # makes an RDF with only the first nentries considered
# small_node = Node('small',small_rdf) # makes a node out of the dataframe
# a.SetActiveNode(small_node) # tell analyzer about the node by setting it as the active node

if(options.isSignal):
    YMass = options.massY
    a.Cut("YMass","GenModel_YMass_{0}==1".format(YMass))

totalEvents = a.GetActiveNode().DataFrame.Count().GetValue()

a.Cut("nFatJet","nFatJet>1")

#need to define this if we want to fill n-1 histograms
preselColumns = VarGroup("Preselection Columns")
preselColumns.Add("DeltaEta","abs(FatJet_eta[0] - FatJet_eta[1])")
preselColumns.Add("pT0","FatJet_pt[0]")
preselColumns.Add("pT1","FatJet_pt[1]")
preselColumns.Add("Eta0","FatJet_eta[0]")
preselColumns.Add("Eta1","FatJet_eta[1]")
preselColumns.Add("mSD0","FatJet_msoftdrop[0]")
preselColumns.Add("mSD1","FatJet_msoftdrop[1]")
a.Apply([preselColumns])

preselectionCuts = CutGroup('Preselection')
preselectionCuts.Add("DeltaEta_cut","DeltaEta < 1.3")
preselectionCuts.Add("pT0_cut","pT0 > 300")
preselectionCuts.Add("pT1_cut","pT1 > 200")
preselectionCuts.Add("Eta0_cut","abs(Eta0) < 2.4")
preselectionCuts.Add("Eta1_cut","abs(Eta1) < 2.4")
preselectionCuts.Add("mSD0_cut","mSD0 > 30")
preselectionCuts.Add("mSD1_cut","mSD1 > 30")

nminusOneNodes = a.Nminus1(a.GetActiveNode(),preselectionCuts) # NOTE: Returns the nodes with N-1 selections
nminusOneHists = HistGroup('nminus1Hists') # NOTE: HistGroup used to batch operate on histograms

nMinusOneLimits = {"DeltaEta":[0.,5.0,100],"pT0":[0.,2000.,100],"pT1":[0.,2000.,100],"mSD0":[0.,330.,33],"mSD1":[30.,330.,33],"Eta0":[-3.,3.,60],"Eta1":[-3.,3.,60]}

# Add hists to group and write out at the end
for nkey in nminusOneNodes.keys():
    #print(nkey)
    if nkey == 'full': continue
    var = nkey.replace('_cut','').replace('minus_','')
    hist = nminusOneNodes[nkey].DataFrame.Histo1D(("{0}_nm1_{1}".format(options.process,var),"nMinusOne {0}".format(var),nMinusOneLimits[var][2],nMinusOneLimits[var][0],nMinusOneLimits[var][1]),var)
    nminusOneHists.Add(var,hist)


a.SetActiveNode(nminusOneNodes["full"])
n_presel = a.GetActiveNode().DataFrame.Count().GetValue()
a.Define("pnet0","FatJet_ParticleNetMD_probXbb[0]")
a.Define("pnet1","FatJet_ParticleNetMD_probXbb[1]")
h_nm1_pnet0 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnet0'.format(options.process),';Leading jet ParticleNet score;Events/0.01;',100,0,1),"pnet0")
h_nm1_pnet1 = a.GetActiveNode().DataFrame.Histo1D(('{0}_nm1_pnet1'.format(options.process),';Subleading jet ParticleNet score;Events/0.01;',100,1,1),"pnet1")
histos.append(h_nm1_pnet1)
histos.append(h_nm1_pnet0)

a.Define("idxH","higgsMassMatchingAlt(FatJet_msoftdrop[0],FatJet_msoftdrop[1])")
a.Define("idxY","1-idxH")
a.Cut("foundJets","idxH>=0")
a.Define('ptjH','FatJet_pt[idxH]')
a.Define('ptjY','FatJet_pt[idxY]')
a.Define('mjY','FatJet_msoftdrop[idxY]')
a.Define('mjH','FatJet_msoftdrop[idxH]')
a.Define("pnetH","FatJet_ParticleNetMD_probXbb[idxH]")
a.Define("pnetY","FatJet_ParticleNetMD_probXbb[idxY]")
a.Define("dak8H","FatJet_deepTagMD_ZHbbvsQCD[idxH]")
a.Define("dak8Y","FatJet_deepTagMD_ZHbbvsQCD[idxY]")
if not options.isData:
    a.Define("idx_GenJetH","genJetToRecoMatching(nGenJetAK8,FatJet_phi[idxH],FatJet_eta[idxH],GenJetAK8_phi,GenJetAK8_eta)")
    a.Define("idx_GenJetY","genJetToRecoMatching(nGenJetAK8,FatJet_phi[idxY],FatJet_eta[idxY],GenJetAK8_phi,GenJetAK8_eta)")
    a.Define("GenJetH_mass","GenJetAK8_mass[idxH]")
    a.Define("GenJetY_mass","GenJetAK8_mass[idxY]")
    h_idx_reco_vs_gen = a.GetActiveNode().DataFrame.Histo2D(('{0}_reco_vs_gen'.format(options.process),'Reco Idx vs Gen Idx;Reco jet index; Get jet index',3,-1,2,10,-1,9),'idxH','idx_GenJetH')
    histos.append(h_idx_reco_vs_gen)
n_JetMassTagging = a.GetActiveNode().DataFrame.Count().GetValue()

h_ptjY_presel = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_presel'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_presel = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_presel'.format(options.process),'FatJetY pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
h_mjY_presel = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_presel'.format(options.process),'FatJetY mSD;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_presel = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_presel'.format(options.process),'FatJetH mSD;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_idxY = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxY'.format(options.process),'idxY',5,-1,4),'idxY')
h_idxH = a.GetActiveNode().DataFrame.Histo1D(('{0}_idxH'.format(options.process),'idxH',5,-1,4),'idxH')
histos.append(h_ptjY_presel)
histos.append(h_ptjH_presel)
histos.append(h_mjY_presel)
histos.append(h_mjH_presel)
histos.append(h_idxY)
histos.append(h_idxH)

pnet_T = 0.90
pnet_L = 0.80
dak8_T = 0.90
dak8_L = 0.80

newcolumns  = VarGroup("newcolumns")
newcolumns.Add('H_vector', 'analyzer::TLvector(FatJet_pt[idxH],FatJet_eta[idxH],FatJet_phi[idxH],FatJet_msoftdrop[idxH])')
newcolumns.Add('Y_vector',  'analyzer::TLvector(FatJet_pt[idxY],FatJet_eta[idxY],FatJet_phi[idxY],FatJet_msoftdrop[idxY])')
newcolumns.Add('mjjHY',     'analyzer::invariantMass(H_vector,Y_vector)') 

newcolumns.Add("pnet_TT","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH] > {0}".format(pnet_T))
newcolumns.Add("pnet_LL","FatJet_ParticleNetMD_probXbb[idxY] > {0} && FatJet_ParticleNetMD_probXbb[idxH] > {0} && (!pnet_TT)".format(pnet_L))
newcolumns.Add("pnet_AT","FatJet_ParticleNetMD_probXbb[idxH] > {0} && FatJet_ParticleNetMD_probXbb[idxY]<{1}".format(pnet_L,pnet_L))#Anti-tag region

newcolumns.Add("dak8_TT","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0}".format(dak8_T))
newcolumns.Add("dak8_LL","FatJet_deepTagMD_ZHbbvsQCD[idxY] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0} && (!dak8_TT)".format(dak8_L))
newcolumns.Add("dak8_AT","FatJet_deepTagMD_ZHbbvsQCD[idxH] > {0} && FatJet_deepTagMD_ZHbbvsQCD[idxY]<{1}".format(dak8_L,dak8_L))


h_pnet_pT_H = a.GetActiveNode().DataFrame.Histo2D(('{0}_pnet_pT_H'.format(options.process),'ParticleNet vs pT Y;ParticleNet_H score ;pT_H [GeV];',100,0,1,300,0,3000),'pnetH','ptjH')
h_pnet_pT_Y = a.GetActiveNode().DataFrame.Histo2D(('{0}_pnet_pT_Y'.format(options.process),'ParticleNet vs pT Y;ParticleNet_Y score ;pT_Y [GeV];',100,0,1,300,0,3000),'pnetY','ptjY')
h_dak8_pT_H = a.GetActiveNode().DataFrame.Histo2D(('{0}_dak8_pT_H'.format(options.process),'DeepAK8 vs pT Y;DeepAK8_H score ;pT_H [GeV];',100,0,1,300,0,3000),'dak8H','ptjH')
h_dak8_pT_Y = a.GetActiveNode().DataFrame.Histo2D(('{0}_dak8_pT_Y'.format(options.process),'DeepAK8 vs pT Y;DeepAK8_Y score ;pT_Y [GeV];',100,0,1,300,0,3000),'dak8Y','ptjY')

histos.append(h_pnet_pT_Y)
histos.append(h_pnet_pT_H)
histos.append(h_dak8_pT_Y)
histos.append(h_dak8_pT_H)

a.Apply([newcolumns])

triggerList = ["HLT_AK8DiPFJet280_200_TrimMass30","HLT_AK8PFJet450","HLT_PFHT650_WideJetMJJ900DEtaJJ1p5","HLT_AK8PFHT650_TrimR0p1PT0p03Mass50",
"HLT_AK8PFHT700_TrimR0p1PT0p03Mass50","HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30","HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20"]
triggersStringAll = ' || '.join(triggerList)
triggersStringNoBtag = ' || '.join(triggerList[:-1])
h_noTriggers = a.GetActiveNode().DataFrame.Histo2D(('{0}_noTriggers'.format(options.process),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,750,3250,30,30,330),'mjjHY','mjY')
a.Cut("triggers_all",triggersStringAll)
h_triggersAll = a.GetActiveNode().DataFrame.Histo2D(('{0}_triggersAll'.format(options.process),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,750,3250,30,30,330),'mjjHY','mjY')
checkpoint  = a.GetActiveNode()#node before we start applying tagger cuts
a.Cut("triggers_noBtag",triggersStringNoBtag)
h_triggersNoBtag = a.GetActiveNode().DataFrame.Histo2D(('{0}_triggersNoBtag'.format(options.process),';m_{jj} [GeV] / 10 GeV;mj_{Y} [GeV] / 10 GeV;',250,750,3250,30,30,330),'mjjHY','mjY')

histos.append(h_noTriggers)
histos.append(h_triggersAll)
histos.append(h_triggersNoBtag)

#-----------------pnet------------------#
a.SetActiveNode(checkpoint)
a.Cut("pnet_TT","pnet_TT==1")
n_pnet_TT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_TT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_pnet_TT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_mjH_mjjHY_pnet_TT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_pnet_TT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_TT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_pnet_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_TT'.format(options.process),'FatJetH pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_TT)
histos.append(h_ptjH_pnet_TT)
histos.append(h_mjY_pnet_TT)
histos.append(h_mjH_pnet_TT)
histos.append(h_mjH_mjjHY_pnet_TT)


#Go back to before tagger cuts were made
a.SetActiveNode(checkpoint)
a.Cut("pnet_LL","pnet_LL==1")
n_pnet_LL = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_LL'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_pnet_LL'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_mjH_mjjHY_pnet_LL = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_pnet_LL'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_LL'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_pnet_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_LL'.format(options.process),'FatJetH pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_LL)
histos.append(h_ptjH_pnet_LL)
histos.append(h_mjY_pnet_LL)
histos.append(h_mjH_pnet_LL)
histos.append(h_mjH_mjjHY_pnet_LL)

a.SetActiveNode(checkpoint)
a.Cut("pnet_AT","pnet_AT==1")
n_pnet_AT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_pnet_AT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_pnet_AT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_mjH_mjjHY_pnet_AT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_pnet_AT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_pnet_AT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_pnet_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_pnet_AT'.format(options.process),'FatJetH pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_pnet_AT)
histos.append(h_ptjH_pnet_AT)
histos.append(h_mjY_pnet_AT)
histos.append(h_mjH_pnet_AT)
histos.append(h_mjH_mjjHY_pnet_AT)

#-----------------dak8------------------#
a.SetActiveNode(checkpoint)
a.Cut("dak8_TT","dak8_TT==1")
n_dak8_TT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_TT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_dak8_TT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_mjH_mjjHY_dak8_TT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_dak8_TT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_TT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_dak8_TT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_TT'.format(options.process),'FatJetH pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_TT)
histos.append(h_ptjH_dak8_TT)
histos.append(h_mjY_dak8_TT)
histos.append(h_mjH_dak8_TT)
histos.append(h_mjH_mjjHY_dak8_TT)


#Go back to before tagger cuts were made
a.SetActiveNode(checkpoint)
a.Cut("dak8_LL","dak8_LL==1")
n_dak8_LL = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_LL'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_dak8_LL'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_mjH_mjjHY_dak8_LL = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_dak8_LL'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_LL'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_dak8_LL = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_LL'.format(options.process),'FatJetH pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_LL)
histos.append(h_ptjH_dak8_LL)
histos.append(h_mjY_dak8_LL)
histos.append(h_mjH_dak8_LL)
histos.append(h_mjH_mjjHY_dak8_LL)

a.SetActiveNode(checkpoint)
a.Cut("dak8_AT","dak8_AT==1")
n_pnet_AT = a.GetActiveNode().DataFrame.Count().GetValue()
h_mjY_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjY_dak8_AT'.format(options.process),'FatJetY softdrop mass;mSD_Y [GeV];Events / 10 GeV;',30,30,330),'mjY')
h_mjH_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_mjH_dak8_AT'.format(options.process),'FatJetH softdrop mass;mSD_H [GeV];Events / 10 GeV;',30,30,330),'mjH')
h_mjH_mjjHY_dak8_AT = a.GetActiveNode().DataFrame.Histo3D(('{0}_mjY_mjH_mjjHY_dak8_AT'.format(options.process),'mjY vs mjH vs mjjHY;mSD_{Y} [GeV] / 10 GeV;mSD_{H} [GeV] / 10 GeV;m_{jj} [GeV] / 10 GeV',30,30,330,30,30,330,250,750,3250),'mjY','mjH','mjjHY')
h_ptjY_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjY_dak8_AT'.format(options.process),'FatJetY pt;pT_Y [GeV];Events / 10 GeV;',300,0,3000),'ptjY')
h_ptjH_dak8_AT = a.GetActiveNode().DataFrame.Histo1D(('{0}_ptjH_dak8_AT'.format(options.process),'FatJetH pt;pT_H [GeV];Events / 10 GeV;',300,0,3000),'ptjH')
histos.append(h_ptjY_dak8_AT)
histos.append(h_ptjH_dak8_AT)
histos.append(h_mjY_dak8_AT)
histos.append(h_mjH_dak8_AT)
histos.append(h_mjH_mjjHY_dak8_AT)

if not options.isData:
    a.SetActiveNode(checkpoint)
    a.Cut("genJetIdx","idx_GenJetH>=0 && idx_GenJetY>=0")
    h_genJetMassH = a.GetActiveNode().DataFrame.Histo1D(('{0}_genJetM_H'.format(options.process),'GenJetH softdrop mass;Gen jet H mSD [GeV];Events / 10 GeV;',30,30,330),'GenJetH_mass')
    h_genJetMassY = a.GetActiveNode().DataFrame.Histo1D(('{0}_genJetM_Y'.format(options.process),'GenJetY softdrop mass;Gen jet Y mSD [GeV];Events / 10 GeV;',30,30,330),'GenJetY_mass')
    h_recoJetMassY = a.GetActiveNode().DataFrame.Histo1D(('{0}_recoJetM_Y'.format(options.process),'RecoJetY softdrop mass;Reco jet H mSD [GeV];Events / 10 GeV;',30,30,330),'mjY')
    h_recoJetMassH = a.GetActiveNode().DataFrame.Histo1D(('{0}_recoJetM_H'.format(options.process),'RecoJetH softdrop massReco jet Y mSD [GeV];Events / 10 GeV;',30,30,330),'mjH')
    histos.append(h_genJetMassY)
    histos.append(h_genJetMassH)
    histos.append(h_recoJetMassY)
    histos.append(h_recoJetMassH)

a.SetActiveNode(checkpoint)
a.Cut("dak8H_cut","dak8H>{0}".format(dak8_L))
h_dak8_mjj_mjY = a.GetActiveNode().DataFrame.Histo3D(('{0}_dak8_mjj_mjY'.format(options.process),'DeepAK8_Y vs mjj vs mj_Y - DeepAK8_H > {0};DeepAK8_Y score ;Dijet invariant mass [GeV]; mSD_Y [GeV]'.format(dak8_L),100,0,1,300,0,3000,100,0,1000),'dak8Y','mjjHY','mjY')
histos.append(h_dak8_mjj_mjY)

a.SetActiveNode(checkpoint)
a.Cut("pnetH_cut","pnetH>{0}".format(pnet_L))
h_pnet_mjj_mjY = a.GetActiveNode().DataFrame.Histo3D(('{0}_pnet_mjj_mjY'.format(options.process),'ParticleNet_Y vs mjj vs mj_Y - ParticleNet_H > {0};ParticlNet_Y score ;Dijet invariant mass [GeV]; mSD_Y [GeV]'.format(pnet_L),100,0,1,300,0,3000,100,0,1000),'pnetY','mjjHY','mjY')
histos.append(h_pnet_mjj_mjY)



hCutFlow = ROOT.TH1F("hCutFlow","Number of events after each cut",7,0.5,7.5)
hCutFlow.AddBinContent(1,totalEvents)
hCutFlow.AddBinContent(2,n_presel)
hCutFlow.AddBinContent(3,n_JetMassTagging)
hCutFlow.AddBinContent(4,n_dak8_TT)
hCutFlow.AddBinContent(5,n_dak8_LL)
hCutFlow.AddBinContent(6,n_pnet_TT)
hCutFlow.AddBinContent(7,n_pnet_LL)

hCutFlow.GetXaxis().SetBinLabel(1, "no cuts")
hCutFlow.GetXaxis().SetBinLabel(2, "Preselection")
hCutFlow.GetXaxis().SetBinLabel(3, "Jet H/Y tagging")
hCutFlow.GetXaxis().SetBinLabel(4, "dak8 TT")
hCutFlow.GetXaxis().SetBinLabel(5, "dak8 LL")
hCutFlow.GetXaxis().SetBinLabel(6, "pnet TT")
hCutFlow.GetXaxis().SetBinLabel(7, "pnet LL")

histos.append(hCutFlow)


out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
nminusOneHists.Do('Write')
out_f.Close()

a.PrintNodeTree('node_tree',verbose=True)
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
