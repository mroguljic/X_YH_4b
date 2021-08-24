import os
from ROOT import *
gROOT.SetBatch(True)

for year in ["16","17","18"]:
    for region in ["L","T"]:
        combineCmd  = "combine -M FitDiagnostics CR_{0}_{1}_full.txt --saveNormalization --saveShapes --saveWithUncertainties".format(region,year)
        mvCmd       = "mv fitDiagnostics.root fitDiagnostics_{0}_{1}.root".format(region,year)
        print(combineCmd)
        os.system(combineCmd)
        print(mvCmd)
        os.system(mvCmd)

        # nuisanceCmd = "python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_{0}_{1}.root  -g nuisance_pulls_{0}_{1}.root --pullDef relDiffAsymErrs --skipFitS".format(region,year)
        # os.system(nuisanceCmd)

        # #Make a PDF of the nuisance_pulls.root
        # if os.path.exists('nuisance_pulls_{0}_{1}.root'.format(region,year)):
        #     nuis_file = TFile.Open('nuisance_pulls_{0}_{1}.root'.format(region,year))
        #     nuis_can = nuis_file.Get('nuisances')
        #     nuis_can.Print('nuisance_pulls_{0}_{1}.pdf'.format(region,year),'pdf')
        #     nuis_file.Close()