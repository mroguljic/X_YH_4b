import ROOT as r
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')

(options, args) = parser.parse_args()


f = r.TFile.Open(options.input)
h = f.Get("hCutFlow")
nBin = h.GetNbinsX()
nTotal = h.GetBinContent(1)
nPreviousCut = h.GetBinContent(1)
for i in range(1,nBin+1):
	cutLabel = h.GetXaxis().GetBinLabel(i)
	nCut = h.GetBinContent(i)
	relRatio = nCut/nPreviousCut
	nPreviousCut = nCut
	absRatio = nCut/nTotal
	print("{0} {1:.3e} {2:.3e}".format(cutLabel,nCut,relRatio,absRatio))