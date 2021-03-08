import ROOT as r
import math
import numpy as np

r.gROOT.SetBatch(True)

def calcSaturated(pred,obs):
	saturated = 0.
	for i in range(len(pred)):
		f 	= pred[i]
		d 	= obs[i]
		#val = f-d+d*np.log(d/f)
		val = (d-f)*(d-f)/(2*f)
		saturated+=val
	return 2*saturated

for year in ["16","17","18"]:
	for region in ["L","T"]:
		postfitFile = r.TFile.Open("fitDiagnostics_{0}_{1}.root".format(region,year))
		postfitPred = postfitFile.Get("shapes_fit_s/{0}_CR/total".format(region))

		morphedFile	= r.TFile.Open("CR_{0}_{1}/morphedWorkspace.root".format(region,year))
		morphedW	= morphedFile.Get("w")
		dataObs 	= r.RooAbsData.createHistogram( morphedW.data('data_obs'), 'hData', morphedW.var('CMS_th1x') )

		toyFile 	= r.TFile.Open("CR_{0}_{1}/higgsCombinegof.GenerateOnly.mH120.10.root".format(region,year))

		predYield 	= []
		dataYield	= []
		for i in range(1,postfitPred.GetNbinsX()+1):
			predYield.append(postfitPred.GetBinContent(i))
			dataYield.append(dataObs.GetBinContent(i))

		dataGOF = calcSaturated(predYield,dataYield)
		print("{0}_{1} GOF: {2}".format(region,year,dataGOF))


# toyGOFs = []
# for nToy in range(1,501):
# 	toyYield 	= []
# 	toyDataset  = toyFile.Get("toys/toy_{0}".format(nToy))
# 	toyDataObs 	= r.RooAbsData.createHistogram( toyDataset, 'hToy{0}'.format(nToy), morphedW.var('CMS_th1x') )
# 	for i in range(1,postfitPred.GetNbinsX()+1):
# 		toyYield.append(toyDataObs.GetBinContent(i))
# 	toyGOFs.append(calcSaturated(predYield,toyYield))

# print("Toy GOF: {0} +/- {1}".format(np.mean(toyGOFs),np.std(toyGOFs)))
# print("Data GOF: {0}".format(dataGOF))
# dataDev = np.abs((dataGOF-np.mean(toyGOFs))/np.std(toyGOFs))
# print("Std deviations from mean: {0}".format(dataDev))
