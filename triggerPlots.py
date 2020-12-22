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

def get2DTrigEff(hPass,hTot,outputFile,RebinX=1,RebinY=1,xTitle="",yTitle="",xLimits=[],yLimits=[],label=""):
    print(label)
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
    c = r.TCanvas("a","a",1500,1500)
    c.cd()
    eff.Draw("col text 45")
    r.gPad.Update()
    g = eff.GetPaintedHistogram()
    if(xLimits):
        g.GetXaxis().SetRangeUser(xLimits[0],xLimits[1])
    if(yLimits):
        g.GetYaxis().SetRangeUser(yLimits[0],yLimits[1])
    r.gPad.Update()

    #legend = r.TLegend(0.2,0.8,0.6,1.0)
    legend = r.TLegend(0.18,0.8,0.45,1.0)
    legend.SetFillStyle(0)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.04)
    legend.SetHeader(label)
    #legend.AddEntry(eff,label,"L")
    legend.Draw()
    r.gPad.Update()
    if(outputFile):
        c.SaveAs(outputFile)
    c.Close()
    return eff

def getTrigEff(hPass,hTot,outputFile="",RebinX=1,xTitle="",yTitle="",color=0,xLimits=[],yLimits=[],printEffs=False):
    h1 = hPass.Clone()
    h1.SetDirectory(0)
    h2 = hTot.Clone()
    h2.SetDirectory(0)

    h1.RebinX(RebinX)
    h2.RebinX(RebinX)
    eff = r.TEfficiency(h1,h2)
    if(printEffs):
        print(xTitle)
        for i in range(1,h1.GetNbinsX()):
            print(h1.GetBinCenter(i),eff.GetEfficiency(i))
    eff.SetTitle(";{0};{1}".format(xTitle,yTitle))
    c = r.TCanvas("","",1500,1500)
    c.cd()
    if(color!=0):
        eff.SetLineColor(color)
    eff.SetLineWidth(3)
    eff.Draw("A")
    r.gPad.Update()
    g = eff.GetPaintedGraph()
    if(xLimits):
        g.GetXaxis().SetRangeUser(xLimits[0],xLimits[1])
    if(yLimits):
        g.GetYaxis().SetRangeUser(yLimits[0],yLimits[1])
    r.gPad.Update()
    if(outputFile):
        c.SaveAs(outputFile)
    return eff


def plotTrigEffs(efficiencies,labels,outputFile,xLimits=[],yLimits=[],legHeader=""):
    c = r.TCanvas("","",2000,2000)
    legend = r.TLegend(0.50,0.18,0.90,0.42)
    legend.SetHeader(legHeader,"C")
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
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
parser.add_option('-y', '--year', metavar='IFILE', type='string', action='store',
            default   =   '',
            dest      =   'year',
            help      =   'Json file containing names, paths to histograms, xsecs etc.')
(options, args) = parser.parse_args()
year = options.year

effs_mJJ  = []
effs_mJY  = []
effs_pT0  = []
effs_pT1  = []
effs_HT   = []
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

        get2DTrigEff(h2D_AllTrigers,h2D_Tot,"results/plots/{0}/trigger/{1}_mJJ_mJ_allTrigger.pdf".format(year,sample),RebinX=10,RebinY=2,xTitle="m_{JJ} [GeV]",yTitle="m_{JY} [GeV]",xLimits=[750,1500],yLimits=[30,330],label=sample_cfg["label"])

        eff_mJJ = getTrigEff(h_mJJ_AllTrigers,h_mJJ_Tot,"".format(sample),RebinX=10,xTitle="m_{JJ}[GeV]",yTitle="Efficiency",color=sample_cfg["color"])
        effs_mJJ.append(eff_mJJ)
        eff_mJY = getTrigEff(h_mJY_AllTrigers,h_mJY_Tot,"".format(sample),RebinX=2,xTitle="m_{JY}[GeV]",yTitle="Efficiency",color=sample_cfg["color"])
        effs_mJY.append(eff_mJY)
        g = r.TFile.Open("TriggerEffs.root","UPDATE")
        g.cd()
        eff_mJJ.SetName("triggEff_{0}".format(year))
        eff_mJJ.Write()
        g.Close()

        hpT0Tot = f.Get("{0}_pT0noTriggers".format(sample))
        hpT0Pass = f.Get("{0}_pT0triggersAll".format(sample))
        hpT1Tot = f.Get("{0}_pT1noTriggers".format(sample))
        hpT1Pass = f.Get("{0}_pT1triggersAll".format(sample))
        hHTTot = f.Get("{0}_HT2p4noTriggers".format(sample))
        hHTPass = f.Get("{0}_HT2p4triggersAll".format(sample))

        if("data" in sample):
            printEffs=True
        else:
            printEffs=False

        eff_pT0 = getTrigEff(hpT0Pass,hpT0Tot,outputFile="",RebinX=1,xTitle="Leading jet p_{T}",yTitle="Efficiency",color=sample_cfg["color"],printEffs=printEffs)
        eff_pT1 = getTrigEff(hpT1Pass,hpT1Tot,outputFile="",RebinX=1,xTitle="Subleading jet p_{T}",yTitle="Efficiency",color=sample_cfg["color"],printEffs=printEffs)
        eff_HT  = getTrigEff(hHTPass,hHTTot,outputFile="",RebinX=1,xTitle="HT",yTitle="Efficiency",color=sample_cfg["color"],printEffs=printEffs)
        effs_pT0.append(eff_pT0)
        effs_pT1.append(eff_pT1)
        effs_HT.append(eff_HT)
        f.Close()

plotTrigEffs(effs_mJJ,labels,"results/plots/{0}/trigger/all_mJJ.pdf".format(year),xLimits=[750,1500],yLimits=[0.5,1.1],legHeader="30 GeV < m_{JY} < 330 GeV")
plotTrigEffs(effs_mJY,labels,"results/plots/{0}/trigger/all_mJY.pdf".format(year),xLimits=[30,330],yLimits=[0.5,1.1],legHeader="750 GeV < m_{JJ} < 1500 GeV")
plotTrigEffs(effs_pT0,labels,"results/plots/{0}/trigger/all_pT0.pdf".format(year),xLimits=[300,1000],yLimits=[0.5,1.1])
plotTrigEffs(effs_pT1,labels,"results/plots/{0}/trigger/all_pT1.pdf".format(year),xLimits=[300,1000],yLimits=[0.5,1.1])
plotTrigEffs(effs_HT,labels, "results/plots/{0}/trigger/all_HT.pdf".format(year),xLimits=[700,1400],yLimits=[0.5,1.1])