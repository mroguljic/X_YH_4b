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


def rebin2DHisto(hToRebin,hModel,name):
    hRes = hModel.Clone(name)
    hRes.Reset()
    xaxis = hToRebin.GetXaxis()
    yaxis = hToRebin.GetYaxis()
    xaxis_re = hRes.GetXaxis()
    yaxis_re = hRes.GetYaxis()
    for i in range(1,hToRebin.GetNbinsX()+1):
        for j in range(1,hToRebin.GetNbinsY()+1):
            x = xaxis.GetBinCenter(i)
            y = yaxis.GetBinCenter(j)
            value = hToRebin.GetBinContent(i,j)
            hRes.Fill(x,y,value)
    hRes.SetDirectory(0)
    return hRes

def get2DTrigEff(hPass,hTot,outputFile,RebinX=1,RebinY=1,xTitle="",yTitle="",xLimits=[],yLimits=[],label=""):
    print(label)
    h1 = hPass.Clone()
    h1.SetDirectory(0)
    h2 = hTot.Clone()
    h2.SetDirectory(0)

    nBinsX = int((xLimits[1]-xLimits[0])/100)
    print(nBinsX)
    customMJYbins = np.array([60.,80.,100.,120.,140.,160.,200.,250.,320.],dtype='float64')
    h2Model = r.TH2F("h2Model","h2Model",nBinsX,xLimits[0],xLimits[1],len(customMJYbins)-1,customMJYbins)

    h1 = rebin2DHisto(h1,h2Model,"rebinnedPass")
    h2 = rebin2DHisto(h2,h2Model,"rebinnedFail")

    # h1.RebinX(RebinX)
    # h1.RebinY(RebinY)
    # h2.RebinX(RebinX)
    # h2.RebinY(RebinY)
    eff = r.TEfficiency(h1,h2)
    eff.SetTitle(";{0};{1}".format(xTitle,yTitle))
    c = r.TCanvas("a","a",1500,1500)
    c.cd()
    eff.Draw("col text 45")
    r.gPad.Update()
    g = eff.GetPaintedHistogram()
    g.GetYaxis().SetTitleOffset(1.25)
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
        c.SaveAs(outputFile.replace("pdf","png"))
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
        c.SaveAs(outputFile.replace("pdf","png"))
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
    legend.SetTextSize(0.04)
    legend.Draw()
    c.SaveAs(outputFile)
    c.SaveAs(outputFile.replace("pdf","png"))

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

effs_MJJ  = []
effs_MJY  = []
effs_pT0  = []
effs_pT1  = []
effs_HT   = []
labels    = []
with open(options.json) as json_file:
    data = json.load(json_file)
    for sample, sample_cfg in data.items():
        f = r.TFile.Open(sample_cfg["file"])
        labels.append(sample_cfg["label"])
        print(sample_cfg["file"])
        print("{0}_noTriggers_SR_nom".format(sample))
        print("{0}_triggersAll_SR_nom".format(sample))
        h2D_Tot             = f.Get("{0}_noTriggers_SR_nom".format(sample))
        h2D_Tot.SetDirectory(0)
        h_MJJ_Tot           = h2D_Tot.ProjectionX("MJJ_tot_{0}_nom".format(sample),1)#excluding underflow bin!
        h_MJY_Tot           = h2D_Tot.ProjectionY("MJY_tot_{0}_nom".format(sample),1)

        h2D_AllTrigers      = f.Get("{0}_triggersAll_SR_nom".format(sample))
        h2D_AllTrigers.SetDirectory(0)

        h_MJJ_AllTrigers    = h2D_AllTrigers.ProjectionX("MJJ_all_{0}".format(sample),1)
        h_MJY_AllTrigers    = h2D_AllTrigers.ProjectionY("MJY_all_{0}".format(sample),1)


        print(h2D_AllTrigers)
        print(h2D_Tot)

        get2DTrigEff(h2D_AllTrigers,h2D_Tot,"results/plots/{0}/trigger/{1}_MJJ_mJ_allTrigger_SR.pdf".format(year,sample),RebinX=10,RebinY=2,xTitle="M_{JJ} [GeV]",yTitle="M_{JY} [GeV]",xLimits=[700,1500],yLimits=[60,320],label=sample_cfg["label"])

        eff_MJJ = getTrigEff(h_MJJ_AllTrigers,h_MJJ_Tot,"".format(sample),RebinX=10,xTitle="M_{JJ}[GeV]",yTitle="Trigger efficiency",color=sample_cfg["color"])
        effs_MJJ.append(eff_MJJ)
        eff_MJY = getTrigEff(h_MJY_AllTrigers,h_MJY_Tot,"".format(sample),RebinX=2,xTitle="M_{JY}[GeV]",yTitle="Trigger efficiency",color=sample_cfg["color"])
        effs_MJY.append(eff_MJY)
        g = r.TFile.Open("TriggerEffs.root","UPDATE")
        g.cd()
        eff_MJJ.SetName("triggEff_{0}".format(year))
        eff_MJJ.Write()
        g.Close()

        hpT0Tot = f.Get("{0}_pT0noTriggers_SR_nom".format(sample))
        hpT0Pass = f.Get("{0}_pT0triggersAll_SR_nom".format(sample))
        hpT1Tot = f.Get("{0}_pT1noTriggers_SR_nom".format(sample))
        hpT1Pass = f.Get("{0}_pT1triggersAll_SR_nom".format(sample))
        hHTTot = f.Get("{0}_HT2p4noTriggers_SR_nom".format(sample))
        hHTPass = f.Get("{0}_HT2p4triggersAll_SR_nom".format(sample))

        if("JetHT" in sample):
            printEffs=False
        else:
            printEffs=False

        eff_pT0 = getTrigEff(hpT0Pass,hpT0Tot,outputFile="",RebinX=1,xTitle="Leading jet p_{T}",yTitle="Efficiency",color=sample_cfg["color"],printEffs=printEffs)
        eff_pT1 = getTrigEff(hpT1Pass,hpT1Tot,outputFile="",RebinX=1,xTitle="Subleading jet p_{T}",yTitle="Efficiency",color=sample_cfg["color"],printEffs=printEffs)
        #eff_HT  = getTrigEff(hHTPass,hHTTot,outputFile="",RebinX=1,xTitle="HT",yTitle="Efficiency",color=sample_cfg["color"],printEffs=printEffs)
        effs_pT0.append(eff_pT0)
        effs_pT1.append(eff_pT1)
        #effs_HT.append(eff_HT)
        f.Close()

# plotTrigEffs(effs_MJJ,labels,"results/plots/{0}/trigger/all_MJJ.pdf".format(year),xLimits=[750,1500],yLimits=[0.5,1.1],legHeader="30 GeV < m_{JY} < 330 GeV")
# plotTrigEffs(effs_MJY,labels,"results/plots/{0}/trigger/all_MJY.pdf".format(year),xLimits=[30,330],yLimits=[0.5,1.1],legHeader="750 GeV < m_{JJ} < 1500 GeV")
# plotTrigEffs(effs_pT0,labels,"results/plots/{0}/trigger/all_pT0.pdf".format(year),xLimits=[300,1000],yLimits=[0.5,1.1])
# plotTrigEffs(effs_pT1,labels,"results/plots/{0}/trigger/all_pT1.pdf".format(year),xLimits=[300,1000],yLimits=[0.5,1.1])
# plotTrigEffs(effs_HT,labels, "results/plots/{0}/trigger/all_HT.pdf".format(year),xLimits=[700,1400],yLimits=[0.5,1.1])

plotTrigEffs(effs_MJJ,labels,"results/plots/{0}/trigger/all_MJJ_SR.pdf".format(year),xLimits=[700,1500],yLimits=[0.5,1.1],legHeader="60 GeV < M_{JY} < 320 GeV")
plotTrigEffs(effs_MJY,labels,"results/plots/{0}/trigger/all_MJY_SR.pdf".format(year),xLimits=[60,320],yLimits=[0.5,1.1],legHeader="700 GeV < M_{JJ} < 1500 GeV")
plotTrigEffs(effs_pT0,labels,"results/plots/{0}/trigger/all_pT0_SR.pdf".format(year),xLimits=[300,1000],yLimits=[0.5,1.1])
# plotTrigEffs(effs_pT1,labels,"results/plots/{0}/trigger/all_pT1_SR.pdf".format(year),xLimits=[300,1000],yLimits=[0.5,1.1])
# plotTrigEffs(effs_HT,labels, "results/plots/{0}/trigger/all_HT_SR.pdf".format(year),xLimits=[700,1400],yLimits=[0.5,1.1])