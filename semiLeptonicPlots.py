import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
from root_numpy import hist2array

def plotVarStack(data,var,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,luminosity="0"):
    histos = []
    labels  = []
    edges   = []
    colors  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element) to be similar to other processes
    labelsData = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        print(sample)
        tempFile = r.TFile.Open(sample_cfg["file"])
        if("muon" in sample.lower() or "data" in sample.lower()):
            h = tempFile.Get("{0}_{1}".format(sample,var))
            h.RebinX(rebinX)
            hist, edges = hist2array(h,return_edges=True)
            histosData.append(hist)
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])
            continue  
        else:
            h = tempFile.Get("{0}_{1}".format(sample,var))
            h.RebinX(rebinX)
            hist, hEdges = hist2array(h,return_edges=True)
            histos.append(hist)
            edges.append(hEdges[0])
            labels.append(sample_cfg["label"])
            colors.append(sample_cfg["color"])
            if(sample_cfg["label"]=="ttbar"):
                labels[-1]=r"t$\bar{t}$"#json restrictions workaround


    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    centresData = (edgesData[0][:-1] + edgesData[0][1:])/2.
    errorsData  = np.sqrt(histosData[0])

    hep.histplot(histos,edges[0],stack=True,ax=ax,label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    if(log):
        ax.set_yscale("log")
    ax.legend()
    ax.set_ylabel(yTitle)
    ax.set_xlabel(xTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc='best',ncol=1)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.clf()

def plotVarMCStack(data,var,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,luminosity="0"):
    histos = []
    labels  = []
    edges   = []
    colors  = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        print(sample)
        tempFile = r.TFile.Open(sample_cfg["file"])
        if("muon" in sample.lower() or "data" in sample.lower()):
            continue  
        else:
            h = tempFile.Get("{0}_{1}".format(sample,var))
            h.RebinX(rebinX)
            hist, hEdges = hist2array(h,return_edges=True)
            histos.append(hist)
            edges.append(hEdges[0])
            labels.append(sample_cfg["label"])
            colors.append(sample_cfg["color"])
            if(sample_cfg["label"]=="ttbar"):
                labels[-1]=r"t$\bar{t}$"#json restrictions workaround


    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    hep.histplot(histos,edges[0],stack=True,ax=ax,label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    if(log):
        ax.set_yscale("log")
    ax.legend()
    ax.set_ylabel(yTitle)
    ax.set_xlabel(xTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("Simulaton WiP",loc=1)
    plt.legend(loc='best',ncol=1)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.clf()

def plotTagJetMass(data,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,luminosity="0"):
    histos = []
    labels  = []
    edges   = []
    colors  = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_mSDqq".format(sample))
        h.Add(tempFile.Get("{0}_mSDbqq".format(sample)))
        h.Add(tempFile.Get("{0}_mSDbq".format(sample)))
        h.Add(tempFile.Get("{0}_mSDother".format(sample)))
        h.RebinX(rebinX)
        hist, hEdges = hist2array(h,return_edges=True)
        histos.append(hist)
        edges.append(hEdges[0])
        labels.append(sample_cfg["label"])
        colors.append(sample_cfg["color"])
        if(sample_cfg["label"]=="ttbar"):
            labels[-1]=r"t$\bar{t}$"#json restrictions workaround

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    hep.histplot(histos,edges[0],stack=True,ax=ax,label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    if(log):
        ax.set_yscale("log")
    ax.legend()
    ax.set_ylabel(yTitle)
    ax.set_xlabel(xTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc='best',ncol=1)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.clf()

def plotTagJetCategories(data,outFile,pTBin="",xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,text="",luminosity="0"):
    roothistos = []
    histos = []
    labels  = []
    edges   = []
    colors  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element) to be similar to other processes
    labelsData = []
    if(pTBin!=""):#Lo/Hi
        pTBin="_pT"+pTBin
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        if("muon" in sample.lower() or "data" in sample.lower()):
            h = tempFile.Get("{0}_mSD{1}".format(sample,pTBin))
            h.RebinX(rebinX)
            hist, edges = hist2array(h,return_edges=True)
            histosData.append(hist)
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])
            continue  
        if(roothistos==[]):
            hqq = tempFile.Get("{0}_unmatched_mSD{1}".format(sample,pTBin))
            hbq = tempFile.Get("{0}_bqq_mSD{1}".format(sample,pTBin))
            hbqq = tempFile.Get("{0}_bq_mSD{1}".format(sample,pTBin))
            hother = tempFile.Get("{0}_qq_mSD{1}".format(sample,pTBin))
            hqq.SetDirectory(0)
            hbq.SetDirectory(0)
            hbqq.SetDirectory(0)
            hother.SetDirectory(0)
            roothistos.append(hqq)
            roothistos.append(hbq)
            roothistos.append(hbqq)
            roothistos.append(hother)
        else:
            hqq = tempFile.Get("{0}_unmatched_mSD{1}".format(sample,pTBin))
            hbq = tempFile.Get("{0}_bqq_mSD{1}".format(sample,pTBin))
            hbqq = tempFile.Get("{0}_bq_mSD{1}".format(sample,pTBin))
            hother = tempFile.Get("{0}_qq_mSD{1}".format(sample,pTBin))
            hqq.SetDirectory(0)
            hbq.SetDirectory(0)
            hbqq.SetDirectory(0)
            hother.SetDirectory(0)
            roothistos[0].Add(hqq)
            roothistos[1].Add(hbq)
            roothistos[2].Add(hbqq)
            roothistos[3].Add(hother)

    labels = ["unmatched","bqq","bq","qq"]
    colors = ["turquoise","firebrick","salmon","limegreen"]
    for h in roothistos:
        h.RebinX(rebinX)
        hist, hEdges = hist2array(h,return_edges=True)
        histos.append(hist)
        edges.append(hEdges[0])


    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    #convert data to scatter
    centresData = (edgesData[0][:-1] + edgesData[0][1:])/2.
    errorsData  = np.sqrt(histosData[0])

    hep.histplot(histos,edges[0],stack=True,ax=ax,label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    if(log):
        ax.set_yscale("log")
    ax.legend()
    ax.set_ylabel(yTitle)
    ax.set_xlabel(xTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    if(text):
        plt.text(0.1, 0.85,text, horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc='best',ncol=1)#loc = 'best'


    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.clf()

if __name__ == '__main__':
    r.gROOT.SetBatch()
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

    if(year=="2016"):
        luminosity="35.9"
    elif(year=="2017"):
        luminosity="41.5"
    elif(year=="2018"):
        luminosity="59.8"
    elif(year=="RunII"):
        luminosity="137.2"
    else:
        print("Year not specified")
        luminosity="0"

    with open(options.json) as json_file:
        data = json.load(json_file)
      
        # plotVarStack(data,"MET","results/plots/semileptonic/{0}/MET{0}.pdf".format(year),xTitle="MET [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[0,1000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"HT","results/plots/semileptonic/{0}/HT{0}.pdf".format(year),xTitle="HT [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"ST","results/plots/semileptonic/{0}/ST{0}.pdf".format(year),xTitle="ST [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e5],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"lepton_pT","results/plots/semileptonic/{0}/lepton_pT{0}.pdf".format(year),xTitle="Muon $p_{T}$ [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[0,1000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"mSD","results/plots/semileptonic/{0}/mSD{0}.pdf".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[10e-1,10e4],xRange=[0,300],log=True,rebinX=2,luminosity=luminosity)

        # plotTagJetCategories(data,"results/plots/semileptonic/{0}/mSDCats{0}.pdf".format(year),xTitle="Soft drop mass [GeV]",yTitle="Jets/20 GeV",yRange=[10e0,3500],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        # plotTagJetCategories(data,"results/plots/semileptonic/{0}/mSDCats_pTLo{0}.pdf".format(year),pTBin="Lo",xTitle="Soft drop mass [GeV]",yTitle="Jets/20 GeV",yRange=[10e0,3500],xRange=[0,300],log=False,rebinX=2,text="300 GeV<$p_{T}$<500 GeV",luminosity=luminosity)
        # plotTagJetCategories(data,"results/plots/semileptonic/{0}/mSDCats_pTHi{0}.pdf".format(year),pTBin="Hi",xTitle="Soft drop mass [GeV]",yTitle="Jets/20 GeV",yRange=[10e0,3500],xRange=[0,300],log=False,rebinX=2,text="$p_{T}$>500 GeV",luminosity=luminosity)


        plotVarMCStack(data,"unmatched_mSD","results/plots/semileptonic/{0}/mSD_unmatched{0}.pdf".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        plotVarMCStack(data,"bqq_mSD","results/plots/semileptonic/{0}/mSD_bqq{0}.pdf".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        plotVarMCStack(data,"bq_mSD","results/plots/semileptonic/{0}/mSD_bq{0}.pdf".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        plotVarMCStack(data,"qq_mSD","results/plots/semileptonic/{0}/mSD_qq{0}.pdf".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)

