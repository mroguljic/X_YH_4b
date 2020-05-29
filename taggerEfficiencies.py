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

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-s', '--sig', action="store_true",dest="isSignal",default=True)
parser.add_option('-b', '--bkg', action="store_false",dest="isSignal")
parser.add_option('-m', '--massY', metavar='FILE', type=int, action='store',
                default   =   200,
                dest      =   'massY',
                help      =   'Mass of the Y.')
parser.add_option('-d', '--outdir', metavar='FILE', type='string', action='store',
                default   =   '.',
                dest      =   'outdir',
                help      =   'Output directory.')


# Import the C++
cc = CommonCscripts() # library of simple C++ functions
CompileCpp(cc.vector) # Compile (via gInterpreter) the string of C++ code
CompileCpp(cc.invariantMass)
CompileCpp('HAMMER/Framework/deltaRMatching.cc') # Compile a full file 

(options, args) = parser.parse_args()
start_time = time.time()
massY = options.massY
wp = 0.7

print(options.input)
if(options.isSignal):
	a = analyzer(options.input)
	newcolumns = VarGroup("newcolumns")
	newcolumns.Add("matchedH","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[0]")
	newcolumns.Add("matchedY","doDRMatching(nFatJet, nGenPart, FatJet_phi, FatJet_eta, GenPart_phi, GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)[1]")
	newcolumns.Add("GenY_pt" ,"getGen_Y_pt(nGenPart,GenPart_pdgId,GenPart_pt)")
	newcolumns.Add("GenH_pt" ,"getGen_H_pt(nGenPart,GenPart_pdgId,GenPart_pt)")

	# out_vars   = ["nFatJet","nGenPart","FatJet_ParticleNetMD_.*","FatJet_pt","FatJet_eta","matched.*"]
	a.Cut("YMass_{0}".format(massY),"GenModel_YMass_{0}==1".format(massY))

	#YptCut 		= 50*round((2*massY/0.8)/50)
	kinematicCuts = CutGroup("kinematicCuts")
	kinematicCuts.Add("nFatJet","nFatJet>1")
	kinematicCuts.Add("boostedJets","FatJet_pt[0]>200 && FatJet_pt[1]>200")# || (FatJet_pt[0]>{0} && FatJet_pt[1]>300)".format(YptCut))#one jet is boosted H, other boosted Y
	kinematicCuts.Add("etaJet0","FatJet_eta[0]>-2.5 && FatJet_eta[0]<2.5")
	kinematicCuts.Add("etaJet1","FatJet_eta[1]>-2.5 && FatJet_eta[1]<2.5")
	a.Apply([newcolumns,kinematicCuts])
	checkpoint 	= a.GetActiveNode()

	#-------------------____H____-------------------#

	a.Cut("matchedH","matchedH>-1 && matchedH<2")#We're looking only at two leading jets

	variablesH = VarGroup("colsH")
	variablesH.Add("H_FatJet_ParticleNetMD_probXbb","FatJet_ParticleNetMD_probXbb[matchedH]")
	variablesH.Add("H_FatJet_pt","FatJet_pt[matchedH]")

	a.Apply([variablesH])
	#out_vars   	= ["nFatJet","nGenPart","FatJet_ParticleNetMD_.*","FatJet_pt","FatJet_eta","matched.*","H_FatJet_pt","H_FatJet_ParticleNetMD_probXbb"]
	#a.GetActiveNode().Snapshot(out_vars,options.outdir+'/'+options.output,'Events',lazy=False,openOption='RECREATE')

	totalH 		= a.GetActiveNode().DataFrame.Histo1D(('H_FatJet_pt total Y{0}'.format(massY),'H-matched FatJet pt',20,0,2000),'H_FatJet_pt')

	a.Cut("H_Xbb","H_FatJet_ParticleNetMD_probXbb>{0}".format(wp))
	passingH 	= a.GetActiveNode().DataFrame.Histo1D(('H_FatJet_pt pass Y{0}'.format(massY),'H-matched FatJet pt',20,0,2000),'H_FatJet_pt')

	effH = ROOT.TEfficiency (passingH.GetValue(), totalH.GetValue())
	effH.SetName("HtaggingEff_Y{0}".format(massY))

	end_node_H = a.GetActiveNode()
	# #-------------------____Y____-------------------#
	a.SetActiveNode(checkpoint)
	a.Cut("matchedY","matchedY>-1 && matchedY<2")

	variablesY = VarGroup("colsY")
	variablesY.Add("Y_FatJet_ParticleNetMD_probXbb","FatJet_ParticleNetMD_probXbb[matchedY]")
	variablesY.Add("Y_FatJet_pt","FatJet_pt[matchedY]")

	a.Apply([variablesY])
	totalY 		= a.GetActiveNode().DataFrame.Histo1D(('Y{0}_FatJet_pt total'.format(massY),'Y-matched FatJet pt'.format(massY),20,0,2000),'Y_FatJet_pt')

	taggerCut   = CutGroup("YtaggerCut")
	a.Cut("Y_Xbb","Y_FatJet_ParticleNetMD_probXbb>{0}".format(wp))
	passingY 	= a.GetActiveNode().DataFrame.Histo1D(('Y{0}_FatJet_pt pass'.format(massY),'Y{0}-matched FatJet pt'.format(massY),20,0,2000),'Y_FatJet_pt')

	effY = ROOT.TEfficiency (passingY.GetValue(), totalY.GetValue())
	effY.SetName("YtaggingEff_Y{0}".format(massY))

	out = ROOT.TFile.Open(options.output,'UPDATE')
	totalH.Write() 
	passingH.Write()
	effH.Write()
	totalY.Write() 
	passingY.Write()
	effY.Write()
	end_node_Y = a.GetActiveNode()

	a.PrintNodeTree('sigNodeTree',verbose=True)

	out.Close()

else:
	a = analyzer(options.input)
	kinematicCuts = CutGroup("kinematicCuts")
	kinematicCuts.Add("nFatJet","nFatJet>1")
	kinematicCuts.Add("boostedJets","FatJet_pt[0]>200 && FatJet_pt[1]>200")# || (FatJet_pt[0]>{0} && FatJet_pt[1]>300)".format(YptCut))#one jet is boosted H, other boosted Y
	kinematicCuts.Add("etaJet0","FatJet_eta[0]>-2.5 && FatJet_eta[0]<2.5")
	kinematicCuts.Add("etaJet1","FatJet_eta[1]>-2.5 && FatJet_eta[1]<2.5")
	a.Apply([kinematicCuts])
	checkpoint 	= a.GetActiveNode()

	#-------------------____FatJet[0]____-------------------#
	a.Define("FatJet0_pt","FatJet_pt[0]")
	totalJet0	= a.GetActiveNode().DataFrame.Histo1D(('FatJet0_pt total','FatJet0 pt',20,0,2000),'FatJet0_pt')
	a.Cut("Jet0_Xbb","FatJet_ParticleNetMD_probXbb[0]>{0}".format(wp))
	passingJet0 = a.GetActiveNode().DataFrame.Histo1D(('FatJet0_pt pass','FatJet0 pt',20,0,2000),'FatJet0_pt')

	effJet0 = ROOT.TEfficiency (passingJet0.GetValue(), totalJet0.GetValue())
	effJet0.SetName("Jet0_taggingEff")

	end_node_H = a.GetActiveNode()
	#-------------------____FatJet[1]____-------------------#
	a.SetActiveNode(checkpoint)
	a.Define("FatJet1_pt","FatJet_pt[1]")
	totalJet1	= a.GetActiveNode().DataFrame.Histo1D(('FatJet1_pt total','FatJet1 pt',20,0,2000),'FatJet1_pt')
	a.Cut("Jet1_Xbb","FatJet_ParticleNetMD_probXbb[1]>{0}".format(wp))
	passingJet1 = a.GetActiveNode().DataFrame.Histo1D(('FatJet1_pt pass','FatJet1 pt',20,0,2000),'FatJet1_pt')

	effJet1 = ROOT.TEfficiency (passingJet1.GetValue(), totalJet1.GetValue())
	effJet1.SetName("Jet1_taggingEff")

	end_node_H = a.GetActiveNode()

	out = ROOT.TFile.Open(options.output,'UPDATE')
	totalJet0.Write() 
	passingJet0.Write()
	effJet0.Write()
	totalJet1.Write() 
	passingJet1.Write()
	effJet1.Write()
	end_node_Y = a.GetActiveNode()

	a.PrintNodeTree('bkgNodeTree',verbose=True)

	out.Close()	
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
