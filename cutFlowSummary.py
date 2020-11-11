import ROOT as r
from optparse import OptionParser
import os
parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')

(options, args) = parser.parse_args()

Y_masses = ["60","80","90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
X_masses = ["800","900","1000","1200","1400","1600","1800","2000"]


years = ["2016","2017","2018"]
year = "2016" 
sigSamples = {}   
inputDir = "/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/histograms/2016/nonScaled/".format(year)

lowestEff = 1.0
highestEff = 0.0
lowSample = ""
hiSample = ""
for X in X_masses:
    for Y in Y_masses:
        sigFile = "{0}/X{1}_Y{2}.root".format(inputDir,X,Y)
        sigSample = "X{0}_Y{1}".format(X,Y)
        #print(sigFile)
        if os.path.isfile(sigFile):
            sigSamples[sigSample] = sigFile
            f = r.TFile.Open(sigFile)
            h = f.Get("{0}_cutflow".format(sigSample))
            nBin = h.GetNbinsX()
            nTotal = h.GetBinContent(1)
            nPreviousCut = h.GetBinContent(1)
            #print(sigSample, nTotal)
            pnetTT = h.GetBinContent(7)
            pnetLL = h.GetBinContent(8)
            sigRegionEff = (pnetLL+pnetTT)/nTotal
            print(X,Y, sigRegionEff, pnetTT+pnetLL,nTotal)
            if(sigRegionEff < lowestEff):
                lowestEff = sigRegionEff
                lowSample = sigSample
            if(sigRegionEff > highestEff):
                highestEff = sigRegionEff
                hiSample = sigSample

            for i in range(1,nBin+1):
                cutLabel = h.GetXaxis().GetBinLabel(i)
                nCut = h.GetBinContent(i)
               # print(i)
               # print(cutLabel)
               # print(nCut)
print(highestEff,hiSample)
print(lowestEff,lowSample)







