import ROOT as r
from optparse import OptionParser
import os
import json

parser = OptionParser()

parser.add_option('-j', '--json', metavar='IFILE', type='string', action='store',
            default   =   '',
            dest      =   'json',
            help      =   'Json file containing names, paths to histograms, xsecs etc.')

(options, args) = parser.parse_args()


with open(options.json) as json_file:
    data = json.load(json_file)
    for sample, sample_cfg in data.items():
        print(sample)
        f = r.TFile.Open(sample_cfg["file"])
        h = f.Get("{0}_cutflow".format(sample))
        nBin = h.GetNbinsX()
        nTotal = h.GetBinContent(1)
        for i in range(1,9):
            cutLabel = h.GetXaxis().GetBinLabel(i)
            nCut = h.GetBinContent(i)
            print(nCut)#/nTotal)
            #print(i, cutLabel, nCut)




