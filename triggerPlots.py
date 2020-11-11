import ROOT as r
from optparse import OptionParser
import json
import  numpy as np
from tdrStyle import setTDRStyle
setTDRStyle()
#import matplotlib.pyplot as plt
#import mplhep as hep
#plt.style.use(hep.style.CMS)

r.gROOT.SetBatch()
r.gStyle.SetPaintTextFormat(".2f")

def get2DTrigEff(hPass,hTot,outputFile,RebinX=1,RebinY=1,xTitle="",yTitle="",xLimits=[],yLimits=[]):
    h1 = hPass.Clone()
    h1.SetDirectory(0)
    h2 = hTot.Clone()
    h2.SetDirectory(0)

    h1.RebinX(RebinX)
    h1.RebinY(RebinY)
    h2.RebinX(RebinX)
    h2.RebinY(RebinY)
    eff = r.TEfficiency(h1,h2)
    eff.SetTitle(";{0};{1}".format(xTitle,yTitle))
    c = r.TCanvas("","",1500,1500)
    eff.Draw("col text 45")
    r.gPad.Update()
    g = eff.GetPaintedHistogram()
    if(xLimits):
        g.GetXaxis().SetRangeUser(xLimits[0],xLimits[1])
    if(yLimits):
        g.GetYaxis().SetRangeUser(yLimits[0],yLimits[1])
    r.gPad.Update()
    if(outputFile):
        c.SaveAs(outputFile)
    return eff

def getTrigEff(hPass,hTot,outputFile="",RebinX=1,xTitle="",yTitle="",color=0):
    h1 = hPass.Clone()
    h1.SetDirectory(0)
    h2 = hTot.Clone()
    h2.SetDirectory(0)

    h1.RebinX(RebinX)
    h2.RebinX(RebinX)
    eff = r.TEfficiency(h1,h2)
    #Debug
    c2 = r.TCanvas("c2","c2",1000,1000)
    c2.cd()
    h1.Draw("h")
    h2.SetLineColor(r.kRed)
    h2.Draw("h same")
    c2.SaveAs("debug.png")
    eff.SetTitle(";{0};{1}".format(xTitle,yTitle))
    c = r.TCanvas("","",1500,1500)
    c.cd()
    if(color!=0):
        eff.SetLineColor(color)
    eff.SetLineWidth(3)
    eff.Draw()
    if(outputFile):
        c.SaveAs(outputFile)
    return eff


def plotTrigEffs(efficiencies,labels,outputFile,xLimits=[],yLimits=[]):
    c = r.TCanvas("","",2000,2000)
    legend = r.TLegend(0.45,0.2,0.85,0.5)
    legend.SetFillStyle(0)
    legend.SetLineWidth(0)
    for i,eff in enumerate(efficiencies):
        if(i==0):
            eff.Draw("A")
            r.gPad.Update()
            g = eff.GetPaintedGraph()
            if(xLimits):
                g.GetXaxis().SetRangeUser(xLimits[0],xLimits[1])
            if(yLimits):
                g.GetYaxis().SetRangeUser(yLimits[0],yLimits[1])
            r.gPad.Update()
        else:
            eff.Draw("same")
        legend.AddEntry(eff,labels[i],"L")
    legend.Draw()
    c.SaveAs(outputFile)

parser = OptionParser()
parser.add_option('-j', '--json', metavar='IFILE', type='string', action='store',
            default   =   '',
            dest      =   'json',
            help      =   'Json file containing names, paths to histograms, xsecs etc.')
(options, args) = parser.parse_args()

effs_mJJ = []
effs_mJY  = []
labels    = []
with open(options.json) as json_file:
    data = json.load(json_file)
    for sample, sample_cfg in data.items():
        f = r.TFile.Open(sample_cfg["file"])
        labels.append(sample_cfg["label"])
        h2D_Tot             = f.Get("{0}_noTriggers".format(sample))
        h2D_Tot.SetDirectory(0)
        h_mJJ_Tot           = h2D_Tot.ProjectionX("mJJ_tot_{0}".format(sample),1)#excluding underflow bin!
        h_mJY_Tot           = h2D_Tot.ProjectionY("mJY_tot_{0}".format(sample),1)

        h2D_AllTrigers      = f.Get("{0}_triggersAll".format(sample))
        h2D_AllTrigers.SetDirectory(0)

        h_mJJ_AllTrigers    = h2D_AllTrigers.ProjectionX("mJJ_all_{0}".format(sample),1)
        h_mJY_AllTrigers    = h2D_AllTrigers.ProjectionY("mJY_all_{0}".format(sample),1)

        h2D_withoutBTrig    = f.Get("{0}_triggersNoBtag".format(sample))
        h2D_withoutBTrig.SetDirectory(0)
        h_mJJ_withoutBTrig  = h2D_withoutBTrig.ProjectionX("mJJ_no_b_{0}".format(sample),1)
        h_mJY_withoutBTrig  = h2D_withoutBTrig.ProjectionY("mJY_no_b_{0}".format(sample),1)

        eff_mJJ = getTrigEff(h_mJJ_AllTrigers,h_mJJ_Tot,"".format(sample),RebinX=5,xTitle="m_{jj}[GeV]",yTitle="Efficiency/50 GeV",color=sample_cfg["color"])
        effs_mJJ.append(eff_mJJ)
        eff_mJY = getTrigEff(h_mJY_AllTrigers,h_mJY_Tot,"".format(sample),RebinX=2,xTitle="m_{Y}[GeV]",yTitle="Efficiency/20 GeV",color=sample_cfg["color"])
        effs_mJY.append(eff_mJY)
        get2DTrigEff(h2D_AllTrigers,h2D_Tot,"results/plots/2017/trigger/{0}_mJJ_mJ_allTrigger.png".format(sample),RebinX=5,RebinY=2,xTitle="m_{jj} / 50 GeV",yTitle="m_{Y} / 20 GeV",xLimits=[750,1500],yLimits=[30,330])
        get2DTrigEff(h2D_withoutBTrig,h2D_Tot,"results/plots/2017/trigger/{0}_mJJ_mJ_noBTrigger.png".format(sample),RebinX=5,RebinY=2,xTitle="m_{jj} / 50 GeV",yTitle="m_{Y} / 20 GeV",xLimits=[750,1500],yLimits=[30,330])
        f.Close()

plotTrigEffs(effs_mJJ,labels,"results/plots/2017/trigger/all_mJJ.png",xLimits=[750,1500],yLimits=[0.0,1.1])
plotTrigEffs(effs_mJY,labels,"results/plots/2017/trigger/all_mJY.png",xLimits=[30,330],yLimits=[0.0,1.1])