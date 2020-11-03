import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import uproot4
from root_numpy import hist2array

def nMinusOnePlotWithData(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True):
    histosSig  = []
    labelsSig  = []
    edgesSig   = []
    histosBkg  = []
    edgesBkg   = []
    labelsBkg  = []
    colorsBkg  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element) to be similar to other processes
    labelsData = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_nm1_{1}".format(sample,cut))
        h.SetBinContent(0,0)#get rid of underflow, may mess up scaling
        if("X" in sample):
            hist, edges = hist2array(h,return_edges=True)
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
        elif("data_obs" in sample):
            hist, edges = hist2array(h,return_edges=True)
            histosData.append(hist)
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])            
        else:
            hist, edges = hist2array(h,return_edges=True)
            histosBkg.append(hist)
            edgesBkg.append(edges[0])
            labelsBkg.append(sample_cfg["label"])
            if(sample_cfg["label"]=="ttbar"):
                labelsBkg[-1]=r"t$\bar{t}$"#json restrictions workaround
            colorsBkg.append(sample_cfg["color"])

    #----QCD scaling to data----#
    hDataMinusBkgs = histosData[0]
    QCDposition    = -1
    #print(np.sum(hDataMinusBkgs))
    for i,hBkg in enumerate(histosBkg):
        if("Multijet" in labelsBkg[i]):
            QCDposition = i
            continue
        else:
            hDataMinusBkgs = np.subtract(hDataMinusBkgs,hBkg)
        #print(labelsBkg[i])
        #print(np.sum(hDataMinusBkgs))
    if(QCDposition==-1):
        print("No QCD in bkg, skipping reweighting")
    else:
        scale = np.sum(hDataMinusBkgs)/np.sum(histosBkg[QCDposition])
        print("QCD scale {0}".format(scale))
        histosBkg[QCDposition] = histosBkg[QCDposition]*scale
    #--------------------------#

    #convert data to scatter
    centresData = (edgesData[0][:-1] + edgesData[0][1:])/2.
    errorsData  = np.sqrt(histosData[0])

    #calculate ratio and errors
    hTotalBkg = np.sum(histosBkg,axis=0)
    errorsTotalBkg = np.sqrt(hTotalBkg)

    for i,value in enumerate(hTotalBkg):
        if(value==0):
            hTotalBkg[i]=0.01#avoid division by zero
    hRatio = np.divide(histosData[0],hTotalBkg)
    errorsRatio = []
    for i in range(len(hRatio)):
        f2 = hRatio[i]*hRatio[i]
        a2 = errorsData[i]*errorsData[i]/(histosData[0][i]*histosData[0][i])
        b2 = errorsTotalBkg[i]*errorsTotalBkg[i]/(hTotalBkg[i]*hTotalBkg[i])
        sigma2 = f2*(a2+b2)
        sigma = np.sqrt(sigma2)
        errorsRatio.append(sigma)
    errorsRatio = np.asarray(errorsRatio)
    #print(hRatio)


    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    hep.histplot(histosBkg,edgesBkg[0],stack=True,ax=axs[0],label = labelsBkg, histtype="fill",color=colorsBkg,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    for i,h in enumerate(histosSig):
        hep.histplot(h,edgesSig[i],stack=False,ax=axs[0],label = labelsSig[i],linewidth=3,zorder=2)
    if(log):
        axs[0].set_yscale("log")
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    axs[0].set_ylabel(yTitle)
    axs[1].set_ylabel("Data/MC")
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    hep.cms.lumitext(text='37.80 $fb^{-1} (13 TeV)$', ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("Simulation WIP",loc=1)
    plt.text(0.37, 0.85, r"pp$\rightarrow$X$\rightarrow$HY$\rightarrow\bar{b}\bar{b}$bb cross sections = 10 fb", horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)
    plt.legend(loc="best")#loc = (0.4,0.2))

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.6,1.4])

    #plt.scatter(centresData, hRatio,color="k")
    plt.errorbar(centresData,hRatio, yerr=errorsRatio, fmt='o',color="k")    


    print("Saving {0}".format(outFile))
    plt.savefig(outFile)


def nMinusOnePlot(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[]):
    histosSig = []
    labelsSig = []
    histosBkg = []
    edgesBkg  = []
    edgesSig  = []
    labelsBkg = []
    colorsBkg = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_nm1_{1}".format(sample,cut))
        if("X" in sample):
            hist, edges = hist2array(h,return_edges=True)
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
        else:
            hist, edges = hist2array(h,return_edges=True)
            histosBkg.append(hist)
            edgesBkg.append(edges[0])
            labelsBkg.append(sample_cfg["label"])
            if(sample_cfg["label"]=="ttbar"):
                labelsBkg[-1]=r"t$\bar{t}$"#json restrictions workaround
            colorsBkg.append(sample_cfg["color"])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    hep.histplot(histosBkg,edgesBkg[0], stack=True,ax=ax,label = labelsBkg, histtype="fill",color=colorsBkg,edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h,edgesSig[i],stack=False,ax=ax,label = labelsSig[i],linewidth=3,zorder=2)
    plt.yscale("log")
    ax.legend()
    ax.set_xlabel(xTitle)
    ax.set_ylabel(yTitle)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    hep.cms.lumitext(text='37.80 $fb^{-1} (13 TeV)$', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WIP",loc=1)
    plt.text(0.37, 0.85, r"pp$\rightarrow$X$\rightarrow$HY$\rightarrow\bar{b}\bar{b}$bb cross sections = 10 fb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc="best")#loc = (0.4,0.2))
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
    hep.cms.lumitext(text='37.80 $fb^{-1} (13 TeV)$', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WIP",loc=1)
    plt.text(0.37, 0.85, r"pp$\rightarrow$X$\rightarrow$HY$\rightarrow\bar{b}\bar{b}$bb cross sections = 10 fb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc="best")#loc = (0.4,0.2))
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
    hep.cms.lumitext(text='37.80 $fb^{-1} (13 TeV)$', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WIP",loc=1)
    plt.legend(loc = (0.4,0.2))
    plt.text(0.23, 0.85, "Signal cross sections = 10 fb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
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
        nMinusOnePlotWithData(data,"pnet0","results/plots/nm1/log/pnet0.png",xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],yRange=[1,10e10])
        nMinusOnePlotWithData(data,"pnet1","results/plots/nm1/log/pnet1.png",xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],yRange=[1,10e10])
        nMinusOnePlotWithData(data,"mSD0","results/plots/nm1/log/mSD0.png",xTitle="Leading jet $m_{SD}[GeV]$",yTitle="Events/10 GeV",xRange=[30,330],yRange=[1,10e10])
        nMinusOnePlotWithData(data,"mSD1","results/plots/nm1/log/mSD1.png",xTitle="Sub-leading jet $m_{SD}[GeV]$",yTitle="Events/10 GeV",xRange=[30,330],yRange=[1,10e10])
        nMinusOnePlotWithData(data,"DeltaEta","results/plots/nm1/log/DeltaEta.png",xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],yRange=[1,10e10])

        nMinusOnePlotWithData(data,"pnet0","results/plots/nm1/lin/pnet0.png",xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False)
        nMinusOnePlotWithData(data,"pnet1","results/plots/nm1/lin/pnet1.png",xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False)
        nMinusOnePlotWithData(data,"mSD0","results/plots/nm1/lin/mSD0.png",xTitle="Leading jet $m_{SD}[GeV]$",yTitle="Events/10 GeV",xRange=[30,330],log=False)
        nMinusOnePlotWithData(data,"mSD1","results/plots/nm1/lin/mSD1.png",xTitle="Sub-leading jet $m_{SD}[GeV]$",yTitle="Events/10 GeV",xRange=[30,330],log=False)
        nMinusOnePlotWithData(data,"DeltaEta","results/plots/nm1/lin/DeltaEta.png",xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],log=False)



        # plotMJJ(data,"results/plots/kinematic/mJJ_pnet_TT.png","pnet","TT",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6])
        # plotMJJ(data,"results/plots/kinematic/mJJ_pnet_LL.png","pnet","LL",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6])
        # plotMJJ(data,"results/plots/kinematic/mJJ_dak8_TT.png","dak8","TT",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6])
        # plotMJJ(data,"results/plots/kinematic/mJJ_dak8_LL.png","dak8","LL",rebin=10,xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6])

        # plotMJY(data,"results/plots/kinematic/mJY_pnet_TT.png","pnet","TT",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])
        # plotMJY(data,"results/plots/kinematic/mJY_pnet_LL.png","pnet","LL",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])
        # plotMJY(data,"results/plots/kinematic/mJY_dak8_TT.png","dak8","TT",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])
        # plotMJY(data,"results/plots/kinematic/mJY_dak8_LL.png","dak8","LL",rebin=2,xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/100 GeV",xRange=[60,300],yRange=[1,10e6])



