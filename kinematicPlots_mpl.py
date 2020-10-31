import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import uproot4
from root_numpy import hist2array

def nMinusOnePlot(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[]):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    for sample, sample_cfg in data.items():
        tempFile = uproot4.open(sample_cfg["file"])
        h = tempFile["{0}_nm1_{1}".format(sample,cut)]
        if("X" in sample):
            histosSig.append(h)
            labelsSig.append(sample_cfg["label"])
        else:
            histosBkg.append(h)
            labelsBkg.append(sample_cfg["label"])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    hep.cms.label(loc=0)

    for i,h in enumerate(histosBkg):
        hep.histplot(h, stack=True,ax=ax,label = labelsBkg[i], histtype="fill",edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h,stack=False,ax=ax,label = labelsSig[i],linewidth=3,zorder=2)
    plt.yscale("log")
    ax.legend()
    ax.set_xlabel(xTitle)
    ax.set_ylabel(yTitle)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)

def getInvMass_h(h3d,rebin):
    hInvMass = h3d.ProjectionZ("projecionMJJ")
    hInvMass.Rebin(rebin) 
    hist, edges = hist2array(hInvMass,return_edges=True)
    return hist,edges[0]

def getmJY_h(h,rebin):
    h.Rebin(rebin) 
    hist, edges = hist2array(h,return_edges=True)
    return hist,edges[0]

def plotMJY(data,outFile,tagger,region,rebin=1,xTitle="",yTitle="",yRange=[],xRange=[]):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        hTemp = tempFile.Get("{0}_mjY_{1}_{2}".format(sample,tagger,region))
        if("X" in sample):
            h,edges = getmJY_h(hTemp,rebin)
            histosSig.append([h,edges])
            labelsSig.append(sample_cfg["label"])
        else:
            h,edges = getmJY_h(hTemp,rebin)
            histosBkg.append([h,edges])
            labelsBkg.append(sample_cfg["label"])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    hep.cms.label(loc=0)

    stackHistosBkg = []
    stackEdgesBkg  = []
    for i,h in enumerate(histosBkg):
        stackHistosBkg.append(h[0])
        stackEdgesBkg.append(h[1])

    hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=True,ax=ax,label = labelsBkg, histtype="fill",edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3)
    plt.yscale("log")
    ax.legend()
    ax.set_xlabel(xTitle)
    ax.set_ylabel(yTitle)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)

def plotMJJ(data,outFile,tagger,region,rebin=1,xTitle="",yTitle="",yRange=[],xRange=[]):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        h3d = tempFile.Get("{0}_mjY_mjH_mjjHY_{1}_{2}".format(sample,tagger,region))
        if("X" in sample):
            h,edges = getInvMass_h(h3d,rebin)
            histosSig.append([h,edges])
            labelsSig.append(sample_cfg["label"])
        else:
            h,edges = getInvMass_h(h3d,rebin)
            histosBkg.append([h,edges])
            labelsBkg.append(sample_cfg["label"])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    hep.cms.label(loc=0)

    stackHistosBkg = []
    stackEdgesBkg  = []
    for i,h in enumerate(histosBkg):
        stackHistosBkg.append(h[0])
        stackEdgesBkg.append(h[1])

    hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=True,ax=ax,label = labelsBkg, histtype="fill",edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3)
    plt.yscale("log")
    ax.legend()
    ax.set_xlabel(xTitle)
    ax.set_ylabel(yTitle)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)    



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
        # nMinusOnePlot(data,"pnet0","results/plots/nm1/pnet0.png",xTitle="Leading jet ParticleNet score",yTitle="Events/0.01")
        # nMinusOnePlot(data,"pnet1","results/plots/nm1/pnet1.png",xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01")
        # nMinusOnePlot(data,"mSD0","results/plots/nm1/mSD0.png",xTitle="Leading jet $m_{SD}[GeV]$",yTitle="Events/10 GeV")
        # nMinusOnePlot(data,"mSD1","results/plots/nm1/mSD1.png",xTitle="Sub-leading jet $m_{SD}[GeV]$",yTitle="Events/10 GeV")
        # nMinusOnePlot(data,"DeltaEta","results/plots/nm1/DeltaEta.png",xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05")

        plotMJJ(data,"results/plots/kinematic/mJJ_pnet_TT.png","pnet","TT",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[700,2000],yRange=[1,10e6])
        plotMJJ(data,"results/plots/kinematic/mJJ_pnet_LL.png","pnet","LL",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[700,2000],yRange=[1,10e6])
        plotMJJ(data,"results/plots/kinematic/mJJ_dak8_TT.png","dak8","TT",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[700,2000],yRange=[1,10e6])
        plotMJJ(data,"results/plots/kinematic/mJJ_dak8_LL.png","dak8","LL",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[700,2000],yRange=[1,10e6])

        plotMJY(data,"results/plots/kinematic/mJY_pnet_TT.png","pnet","TT",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])
        plotMJY(data,"results/plots/kinematic/mJY_pnet_LL.png","pnet","LL",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])
        plotMJY(data,"results/plots/kinematic/mJY_dak8_TT.png","dak8","TT",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])
        plotMJY(data,"results/plots/kinematic/mJY_dak8_LL.png","dak8","LL",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])



