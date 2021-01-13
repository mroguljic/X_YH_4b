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
        h = f.Get("{0}_cutflow".format(sample))
        # if(sample=="ttbar"):
        #     h = f.Get("TTbar_cutflow")
        nBin = h.GetNbinsX()
        totalBkgRow = []
        latexRow = sample+" &"
        for i in range(1,nBin+1):
            if("dak8" in h.GetXaxis().GetBinLabel(i)):
                continue
            if(labelFlag==False):
                labels.append(h.GetXaxis().GetBinLabel(i))
            nCut = h.GetBinContent(i)
            latexRow = latexRow +" {0:.2f} &".format(nCut)
            totalBkgRow.append(nCut)

        if(labelFlag==False):
            labelFlag=True
            print(" & ".join(labels), " \\\\")
        latexRow = latexRow[:-2]+"\\\\"
        print(latexRow)
        if(datasetType=="bkg"):
            if(sample=="ttbar"):
                continue#adding stitched ttbar to total bkg
            if len(totalBkg)==0:
                totalBkg=totalBkgRow
            else:
                totalBkg = np.add(totalBkg,totalBkgRow)
        #a = latexRow.split(" & ")
        #print("{0}".format(a[0],a[-3],a[-4]))

latexTotalBkg = "Total bkg "
for val in totalBkg:
    latexTotalBkg += "& {0:.2f} ".format(val)
print(latexTotalBkg+"\\\\")

