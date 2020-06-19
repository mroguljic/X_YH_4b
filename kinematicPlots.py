import ROOT as r
from optparse import OptionParser
from time import sleep
import json


def stackHistos(data,region,tagger,outFile):
    hStack       = r.THStack("hs","{0} region, {1} tagger".format(region,tagger))
    legend       = r.TLegend(0.6,0.7,0.9,0.9)
    histos       = []
    for sample, sample_cfg in data.items():
        h = getInvMass_h(sample,sample_cfg,region,tagger)
        histos.append(h)

    histos.sort(key=lambda x: x.GetName())    

    c = r.TCanvas("c","c",1000,1000)
    c.SetLogy()
    flagQCD = False
    hSignal = False
    for h in histos:
        print(h)
        if "X" in h.GetName():
            hSignal = h
            continue
        hStack.Add(h)
        if "QCD" in h.GetName():
            if flagQCD==False:
                legend.AddEntry(h,"QCD")
                flagQCD=True
            continue
        if "tt" in h.GetName():
            legend.AddEntry(h,"ttbar")


    hStack.Draw("hist")
    hStack.GetXaxis().SetLimits(1000., 3000.);
    hStack.SetMinimum(1)
    hStack.SetMaximum(1300)
    if(hSignal):
        legend.AddEntry(hSignal,"X->HY->4b")
        hSignal.Draw("hist L same")

    legend.Draw()
    c.Update()
    c.SaveAs(outFile)


def getInvMass_h (sample,sample_cfg,region,tagger,luminosity=137000):#inverse fb
    tempFile = r.TFile.Open(sample_cfg["file"])
    hCutFlow = tempFile.Get("hCutFlow_{0}".format(tagger))
    h2d      = tempFile.Get("{0}_mjHY_mjH_{1}_{2}".format(sample,tagger,region))
    nTotal   = hCutFlow.GetBinContent(1)
    nRegion  = h2d.Integral()
    xsec     = sample_cfg['xsec']    
    eff      = nRegion/nTotal
    norm     = eff*luminosity*xsec
    hInvMass = h2d.ProjectionX("{0}_mjHY_{1}_{2}".format(sample,tagger,region))
    hInvMass.Scale(norm/hInvMass.Integral())
    hInvMass.SetTitle("{0}_{1}_{2} HY invariant mass".format(sample,tagger,region))   
    hInvMass.Rebin(5) 
    color    = sample_cfg["color"]

    if "X" in str(sample):
        hInvMass.SetLineColor(color)
        hInvMass.SetLineWidth(3)
    else:
        hInvMass.SetFillColorAlpha(color,0.50)
        hInvMass.SetLineWidth(0)

    hInvMass.SetDirectory(0)#otherwise the histogram is destroyed when file is closed
    tempFile.Close()

    return hInvMass



if __name__ == '__main__':
    r.gROOT.SetBatch()
    parser = OptionParser()
    parser.add_option('-j', '--json', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'json',
                help      =   'Json file containing names, paths to histograms, xsecs etc.')
    (options, args) = parser.parse_args()

    with open(options.json) as json_file:
        data = json.load(json_file)
        stackHistos(data,"TT","pnet","TT_pnet.pdf")
        stackHistos(data,"LL","pnet","LL_pnet.pdf")
        stackHistos(data,"TT","dak8","TT_dak8.pdf")
        stackHistos(data,"LL","dak8","LL_pnet.pdf")
