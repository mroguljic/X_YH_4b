import ROOT as r
from optparse import OptionParser
import os
import json
import csv

parser = OptionParser()

parser.add_option('-j', '--json', metavar='IFILE', type='string', action='store',
            default   =   '',
            dest      =   'json',
            help      =   'Json file containing names, paths to histograms, xsecs etc.')

(options, args) = parser.parse_args()


with open(options.json) as json_file:
    labels = ["Sample"]
    values = []
    data = json.load(json_file)
    labelFlag = False
    for sample, sample_cfg in data.items():

        f = r.TFile.Open(sample_cfg["file"])
        h = f.Get("{0}_cutflow".format(sample))
        nBin = h.GetNbinsX()
        row  = [sample]
        for i in range(1,nBin+1):
            if(labelFlag==False):
                labels.append(h.GetXaxis().GetBinLabel(i))
            nCut = h.GetBinContent(i)
            row.append(nCut)
        if(labelFlag==False):
            values.append(labels)
            labelFlag=True
        values.append(row)
    print(values)

    with open("out.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(values)



