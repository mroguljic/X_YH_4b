import ROOT as r
from optparse import OptionParser
from time import sleep
import json


def makeHistos(data):
    luminosity = 137000 #inverse pb
    hStack_TT = r.THStack("hstt","Stack histo TT")
    hStack_LL = r.THStack("hsll","Stack histo LL")
    legend = r.TLegend(0.6,0.7,0.9,0.9)
    histos_TT = []
    histos_LL = []
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg['file'])
        hCutFlow = tempFile.Get("hCutFlow")
        totalN   = hCutFlow.GetBinContent(1)
        TT_count = hCutFlow.GetBinContent(3)
        LL_count = hCutFlow.GetBinContent(4)
        eff_TT   = TT_count/totalN
        eff_LL   = LL_count/totalN
        xsec     = sample_cfg['xsec']
        TT_norm  = eff_TT*luminosity*xsec
        LL_norm  = eff_LL*luminosity*xsec
        h_TT     = tempFile.Get((str(sample)+"_invMass_TT"))
        h_LL     = tempFile.Get((str(sample)+"_invMass_LL"))
        h_TT.SetDirectory(0)
        h_LL.SetDirectory(0)
        h_TT.Scale(TT_norm/h_TT.Integral())
        h_LL.Scale(LL_norm/h_LL.Integral())
        h_TT.SetTitle(str(sample))
        h_TT.SetName(str(sample)+"_name")
        color   = sample_cfg["color"]
        h_TT.SetFillColorAlpha(color,0.50)
        h_LL.SetFillColorAlpha(color,0.50)
        h_TT.SetLineColor(color)
        h_LL.SetLineColor(color)
        histos_TT.append(h_TT)
        histos_LL.append(h_LL)
        tempFile.Close()

    for h in histos_TT:
        print(h)
        hStack_TT.Add(h)
        legend.AddEntry(h)
    for h in histos_LL:
        print(h)
        hStack_LL.Add(h)
    c = r.TCanvas("c","c",1000,1000)
    #c.SetLogy()

    hStack_TT.Draw("hist")
    hStack_TT.GetXaxis().SetLimits(1300., 1800.);
    hStack_TT.SetMinimum(1)
    hStack_TT.SetMaximum(200)

    legend.Draw()
    c.Update()
    c.SaveAs("invM_TT.pdf")

    c.Clear()

    hStack_LL.Draw("hist")
    hStack_LL.GetXaxis().SetLimits(1300., 1800.);
    hStack_LL.SetMinimum(1)
    hStack_LL.SetMaximum(200)
    legend.Draw()
    c.Update()
    c.SaveAs("invM_LL.pdf")

if __name__ == '__main__':
    r.gROOT.SetBatch()
    with open("results.json") as json_file:
        data = json.load(json_file)
        makeHistos(data)