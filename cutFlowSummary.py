import ROOT as r
from optparse import OptionParser
import os
import json
import csv
import numpy as np

parser = OptionParser()

parser.add_option('-j', '--json', metavar='IFILE', type='string', action='store',
            default   =   '',
            dest      =   'json',
            help      =   'Json file containing names, paths to histograms, xsecs etc.')

(options, args) = parser.parse_args()

totalBkg = []

with open(options.json) as json_file:
    labels = ["Sample"]
    values = []
    data = json.load(json_file)
    labelFlag = False

    for sample, sample_cfg in data.items():
        if ("MX" in sample):
            datasetType = "sig"
        elif ("JetHT" in sample):
            datasetType = "data"
        else:
            datasetType = "bkg"
            

        f = r.TFile.Open(sample_cfg["file"])
        #h = f.Get("{0}_cutflow_nom".format(sample_cfg["prefix"]))
        h = f.Get("{0}_cutflow_nom".format(sample))
        # if(sample=="ttbar"):
        #     h = f.Get("TTbar_cutflow")
        nBin = h.GetNbinsX()
        totalBkgRow = []
        latexRow = sample+" &"
        for i in range(1,nBin+1):
            if(labelFlag==False):
                labels.append(h.GetXaxis().GetBinLabel(i))
            nCut = h.GetBinContent(i)
            if(nCut>10000):
                latexRow = latexRow +" {0:1.2e} &".format(nCut)
            else:   
                latexRow = latexRow +" {0:.2f} &".format(nCut)
            totalBkgRow.append(nCut)

        if(labelFlag==False):
            labelFlag=True
            print(" & ".join(labels), " \\\\")
        latexRow = latexRow[:-2]+"\\\\"
        print(latexRow)
        if(datasetType=="bkg"):
            if len(totalBkg)==0:
                totalBkg=totalBkgRow
            else:
                totalBkg = np.add(totalBkg,totalBkgRow)
        # a = latexRow.split(" & ")
        # print("{0} {1} {2}".format(a[0],a[-4],a[-5]))

latexTotalBkg = "Total bkg "
for val in totalBkg:
    if(val>10000):
        latexTotalBkg += "& {0:1.2e} ".format(val)
    else:
        latexTotalBkg += "& {0:.2f} ".format(val)
print(latexTotalBkg+"\\\\")

