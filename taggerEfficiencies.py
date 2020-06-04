# -*- coding: latin-1 -*-
import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from HAMMER.Tools import CMS_lumi
from HAMMER.Tools.Common import *
from HAMMER.Analyzer import *

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
                default   =   'YH4b',
                dest      =   'process',
                help      =   'Process in the given MC file')
parser.add_option('-s', '--sig', action="store_true",dest="isSignal",default=True)
parser.add_option('-b', '--bkg', action="store_false",dest="isSignal")
parser.add_option('-m', '--massY', metavar='GenY mass (if MC signal)', type=int, action='store',
                default   =   200,
                dest      =   'massY',
                help      =   'Mass of the Y')
parser.add_option('-d', '--outdir', metavar='ODIR', type='string', action='store',
                default   =   '.',
                dest      =   'outdir',
                help      =   'Output directory.')


# Import the C++
cc = CommonCscripts() # library of simple C++ functions
CompileCpp(cc.vector) # Compile (via gInterpreter) the string of C++ code
CompileCpp(cc.invariantMass)
CompileCpp('HAMMER/Framework/deltaRMatching.cc') # Compile a full file 

(options, args) = parser.parse_args()
start_time 		= time.time()
massY 			= options.massY
process 		= options.process


#FatJet_deepTagMD_ZHbbvsQCD
#FatJet_ParticleNetMD_probXbb
tagger = 'FatJet_ParticleNetMD_probXbb'
#pnet
#dak8
taggerShort = 'pnet'
print(options.input)
if(options.isSignal):
	a = analyzer(options.input)
	newcolumns = VarGroup("newcolumns")
	newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
	newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
	newcolumns.Add("GenY_pt" ,"getGen_Y_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
	newcolumns.Add("GenH_pt" ,"getGen_H_pt(nGenPart,GenPart_pdgId,GenPart_pt)")

	a.Cut("YMass_{0}".format(massY),"GenModel_YMass_{0}==1".format(massY))

	kinematicCuts = CutGroup("kinematicCuts")
	kinematicCuts.Add("nFatJet","nFatJet>1")
	kinematicCuts.Add("boostedJets","FatJet_pt[0]>200 && FatJet_pt[1]>200")
	kinematicCuts.Add("etaJet0","FatJet_eta[0]>-2.5 && FatJet_eta[0]<2.5")
	kinematicCuts.Add("etaJet1","FatJet_eta[1]>-2.5 && FatJet_eta[1]<2.5")
	a.Apply([newcolumns,kinematicCuts])
	checkpoint 	= a.GetActiveNode()

	#-------------------____H____-------------------#

	a.Cut("matchedH","matchedH>-1 && matchedH<2")#We're looking only at two leading jets

	variablesH = VarGroup("colsH")
	variablesH.Add("H_{0}".format(tagger),"{0}[matchedH]".format(tagger))
	variablesH.Add("H_FatJet_pt","FatJet_pt[matchedH]")

	a.Apply([variablesH])
	#out_vars   	= ["nFatJet","nGenPart","FatJet_ParticleNetMD_.*","FatJet_pt","FatJet_eta","matched.*","H_FatJet_pt","H_FatJet_deepTagMD_ZHbbvsQCD"]
	#a.GetActiveNode().Snapshot(out_vars,options.outdir+'/'+options.output,'Events',lazy=False,openOption='RECREATE')

	hMatchedH	= a.GetActiveNode().DataFrame.Histo2D(('matchedH_pt_vs_tag_Y{0}_{1}'.format(massY,taggerShort),'H-matched FatJet pt vs Tag',30,0,2000,50,0,1),'H_FatJet_pt','H_{0}'.format(tagger))
	end_node_H = a.GetActiveNode()
	# #-------------------____Y____-------------------#
	a.SetActiveNode(checkpoint)
	a.Cut("matchedY","matchedY>-1 && matchedY<2")

	variablesY = VarGroup("colsY")
	variablesY.Add("Y_{0}".format(tagger),"{0}[matchedY]".format(tagger))
	variablesY.Add("Y_FatJet_pt","FatJet_pt[matchedY]")

	a.Apply([variablesY])
	hMatchedY	= a.GetActiveNode().DataFrame.Histo2D(('matchedY_pt_vs_tag_Y{0}_{1}'.format(massY,taggerShort),'Y-matched FatJet pt vs Tag',30,0,2000,50,0,1),'Y_FatJet_pt','Y_{0}'.format(tagger))


	out = ROOT.TFile.Open(options.outdir+'/'+options.output,'UPDATE')
	hMatchedH.Write()
	hMatchedY.Write()
	end_node_Y = a.GetActiveNode()

	#a.PrintNodeTree('sigNodeTree',verbose=False)

	out.Close()

else:
	a = analyzer(options.input)
	kinematicCuts = CutGroup("kinematicCuts")
	kinematicCuts.Add("nFatJet","nFatJet>1")
	kinematicCuts.Add("boostedJets","FatJet_pt[0]>200 && FatJet_pt[1]>200")# || (FatJet_pt[0]>{0} && FatJet_pt[1]>300)".format(YptCut))#one jet is boosted H, other boosted Y
	kinematicCuts.Add("etaJet0","FatJet_eta[0]>-2.5 && FatJet_eta[0]<2.5")
	kinematicCuts.Add("etaJet1","FatJet_eta[1]>-2.5 && FatJet_eta[1]<2.5")
	a.Apply([kinematicCuts])
	a.Define("FatJet0_pt","FatJet_pt[0]")
	a.Define("FatJet0_ParticleNetMD_probXbb","{0}[0]".format(tagger))
	a.Define("FatJet1_pt","FatJet_pt[1]")
	a.Define("FatJet1_ParticleNetMD_probXbb","{0}[1]".format(tagger))
	checkpoint 	= a.GetActiveNode()

	#-------------------____FatJet[0]____-------------------#
	hFatJet0	= a.GetActiveNode().DataFrame.Histo2D(('FatJet[0]_pt_vs_tag_{0}_{1}'.format(massY,taggerShort),'FatJet0 pt vs Tag',30,0,2000,50,0,1),'FatJet0_pt','FatJet0_ParticleNetMD_probXbb')
	end_node_0  = a.GetActiveNode()
	#-------------------____FatJet[1]____-------------------#
	a.SetActiveNode(checkpoint)
	hFatJet1	= a.GetActiveNode().DataFrame.Histo2D(('FatJet[1]_pt_vs_tag_{0}_{1}'.format(massY,taggerShort),'FatJet1 pt vs Tag',30,0,2000,50,0,1),'FatJet1_pt','FatJet1_ParticleNetMD_probXbb')
	end_node_1  = a.GetActiveNode()

	out = ROOT.TFile.Open(options.outdir+'/'+options.output,'UPDATE')
	hFatJet0.Write()
	hFatJet1.Write()
	#a.PrintNodeTree('bkgNodeTree',verbose=True)

	out.Close()	
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
