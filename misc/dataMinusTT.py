import ROOT as r
import sys
import numpy as np


tplDir      = sys.argv[1]
year     = ""
if("2016" in tplDir):
    year = 16
if("2017" in tplDir):
    year = 17
if("2018" in tplDir):
    year = 18
dataFile    = r.TFile.Open(tplDir+"/JetHT{0}.root".format(year))
TTfile      = r.TFile.Open(tplDir+"/TTbar{0}.root".format(year))
newHistos   = []

for key in dataFile.GetListOfKeys():
    hData   = key.ReadObj()
    hName   = hData.GetName()
    hData.SetDirectory(0)
    #print(hName)
    if("_mJY_mJJ_" in hName):
        newHistoName = hName.replace("data_obs","QCD")
        hTTName      = hName.replace("data_obs","TTbar")
        hTT          = TTfile.Get(hTTName)
        newHisto     = hData.Clone(newHistoName)
        newHisto.Add(hTT,-1)
        newHistos.append(newHisto)
    else:
        continue

outFile = r.TFile.Open("{0}/dataMinusTTbar.root".format(tplDir),"RECREATE")
outFile.cd()
for h in newHistos:
    h.Write()
outFile.Close()
