import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
from root_numpy import hist2array

def plotVarSeparated(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,luminosity="35.9"):
    histos = []
    labels  = []
    edges   = []
    colors  = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_{1}".format(sample,cut))
        hist, hEdges = hist2array(h,return_edges=True)
        histos.append(hist)
        edges.append(hEdges[0])
        labels.append(sample_cfg["label"])
        colors.append(sample_cfg["color"])
        if(sample_cfg["label"]=="ttbar"):
            labels[-1]=r"t$\bar{t}$"#json restrictions workaround

    for i,h in enumerate(histos):
        scale = 1./np.sum(h)
        histos[i] = h*scale

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    for i,h in enumerate(histos):
        hep.histplot(h,edges[i],stack=False,ax=ax,label = labels[i],linewidth=3,zorder=2,color=colors[i])
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
    hep.cms.lumitext(lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("WiP",loc=1)
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc=(0.02,0.5),ncol=1)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

def nMinusOnePlotSeparated(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,sigXSec=0.01,luminosity="35.9",rebinX=1):
    histosSig  = []
    labelsSig  = []
    edgesSig   = []
    histosBkg  = []
    edgesBkg   = []
    labelsBkg  = []
    colorsBkg  = []
    colorsSig  = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_nm1_{1}".format(sample,cut))
        h.RebinX(rebinX)
        if("X" in sample):
            hist, edges = hist2array(h,return_edges=True)
            hist = hist*(sigXSec/0.01)
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
        elif("data_obs" in sample):
            continue       
        else:
            hist, edges = hist2array(h,return_edges=True)
            histosBkg.append(hist)
            edgesBkg.append(edges[0])
            labelsBkg.append(sample_cfg["label"])
            if(sample_cfg["label"]=="ttbar"):
                labelsBkg[-1]=r"t$\bar{t}$"#json restrictions workaround
            colorsBkg.append(sample_cfg["color"])


    for i,hBkg in enumerate(histosBkg):
        scale = 1./np.sum(hBkg)
        histosBkg[i] = hBkg*scale
    for i,hSig in enumerate(histosSig):
        scale = 1./np.sum(hSig)
        histosSig[i] = hSig*scale


    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    hep.histplot(histosBkg,edgesBkg[0],stack=False,ax=ax,label = labelsBkg, histtype="step",color=colorsBkg)
    for i,h in enumerate(histosSig):
        hep.histplot(h,edgesSig[i],stack=False,ax=ax,label = labelsSig[i],linewidth=3,zorder=2,color=colorsSig[i])
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
    hep.cms.lumitext(lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("WiP",loc=1)
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc=(0.02,0.5),ncol=2)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

def effCutflow(inFile,sample,outFile,xTitle="",yTitle="",label="",yRange=[],xRange=[],log=False,luminosity="35.9"):
    tempFile = r.TFile.Open(inFile)
    hTemp = tempFile.Get("{0}_cutflow".format(sample))
    hist, edges = hist2array(hTemp,return_edges=True)
    #print(sample)
    #print(hist)
    for i in range(1,5):#tagger regions only pnet and dak8 TT/LL
        hist[-i]=hist[-i]/hist[0]
    for i in range(5,len(hist)):#skip tagging regions
        hist[-i]=hist[-i]/hist[0]
    hist[0]=1.
    #print(hist)

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    ax.locator_params(nbins=12, axis='x')
    hep.histplot(hist,edges[0],ax=ax,label=label,histtype="step",color='black')
    if(log):
        ax.set_yscale("log")
    ax.legend()
    ax.set_xlabel(xTitle)
    ax.set_ylabel(yTitle)

    hep.cms.lumitext(text='2018', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc="best")#loc = (0.4,0.2))
    
    axisTicks = ax.get_xticks().tolist()
    axisTicks = [0,"No cuts", "Triggers", "Jets definition", "Preselection", "H-jet $m_{SD}$","H,Y pT cut","ParticlNet TT","ParticlNet LL","DeepAK8 TT","DeepAK8 LL"]
    ax.set_xticklabels(axisTicks,rotation=45,fontsize=14)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

def cutFlowWithData(data,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,sigXSec=0.01,luminosity="35.9"):
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
        h = tempFile.Get("{0}_cutflow".format(sample))
        hist, edges = hist2array(h,return_edges=True)
        # hist = np.delete(hist,0)#removing count before triggers
        # edges[0] = np.delete(edges[0],0)
        if("X" in sample):
            #continue
            hist = hist*(sigXSec/0.01)#assuming signal is lumiscaled to 10fb
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
        elif("data_obs" in sample or "JetHT" in sample):
            histosData.append(hist)
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])            
        else:
            histosBkg.append(hist)
            edgesBkg.append(edges[0])
            labelsBkg.append(sample_cfg["label"])
            if(sample_cfg["label"]=="ttbar"):
                labelsBkg[-1]=r"t$\bar{t}$"#json restrictions workaround
            colorsBkg.append(sample_cfg["color"])

    #----QCD scaling to data----#
    otherBkgYield  = 0
    QCDposition    = -1
    for i,hBkg in enumerate(histosBkg):
        if("Multijet" in labelsBkg[i]):
            QCDposition = i
            continue
        else:
           otherBkgYield+=hBkg[1]
    hDataMinusBkgs = histosData[0][1] - otherBkgYield
    if(QCDposition==-1):
        print("No QCD in bkg, skipping reweighting")
    else:
        scale = np.sum(hDataMinusBkgs)/np.sum(histosBkg[QCDposition][1])
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


    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    hep.histplot(histosBkg,edgesBkg[0],stack=True,ax=axs[0],label = labelsBkg,edgecolor='black', linewidth=1.2, histtype="fill",facecolor=colorsBkg)
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    for i,h in enumerate(histosSig):
       hep.histplot(h,edgesSig[i],stack=False,ax=axs[0],label = labelsSig[i],linewidth=3,zorder=2)
    if(log):
        axs[0].set_yscale("log")
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    axs[0].set_ylabel(yTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    axs[1].set_ylabel("Data/MC")
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc=(0.02,0.4),ncol=2)#loc = 'best'
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.6,1.4])
    axs[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
    axisTicks = axs[1].get_xticks().tolist()
    axisTicks = ["zero","Processed", "Skimmed", "Trigger", "Eta", "$p_{T}$","$\Delta\eta$","$M_{JJ}$","Higgs mass","SR pass","SR fail","VR pass","VR fail"]
    axs[1].set_xticklabels(axisTicks,rotation=45,fontsize=14)
    #plt.scatter(centresData, hRatio,color="k")
    plt.errorbar(centresData,hRatio, yerr=errorsRatio, fmt='o',color="k")    


    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()



def nMinusOnePlotWithData(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,sigXSec=0.01,luminosity="35.9",rebinX=1):
    histosSig  = []
    labelsSig  = []
    edgesSig   = []
    histosBkg  = []
    edgesBkg   = []
    labelsBkg  = []
    colorsBkg  = []
    colorsSig  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element) to be similar to other processes
    labelsData = []

    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_nm1_{1}".format(sample,cut))
        h.RebinX(rebinX)
        if("X" in sample):
            hist, edges = hist2array(h,return_edges=True)
            hist = hist*(sigXSec/0.01)
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
        elif("data_obs" in sample or "JetHT" in sample):
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
    hep.histplot(histosBkg,edgesBkg[0],stack=True,ax=axs[0],label = labelsBkg, histtype="fill",facecolor=colorsBkg,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    for i,h in enumerate(histosSig):
        hep.histplot(h,edgesSig[i],stack=False,ax=axs[0],label = labelsSig[i],linewidth=3,zorder=2,color=colorsSig[i])
    if(log):
        axs[0].set_yscale("log")
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    axs[0].set_ylabel(yTitle)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    axs[1].set_ylabel("Data/MC")
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    hep.cms.text("WiP",loc=1)
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)
    plt.legend(loc=(0.05,0.4),ncol=2)#loc = 'best'

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.,2.1])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    #plt.scatter(centresData, hRatio,color="k")
    plt.errorbar(centresData,hRatio, yerr=errorsRatio, fmt='o',color="k")    


    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()


def nMinusOnePlot(data,cut,outFile,xTitle="",yTitle="",yRange=[],xRange=[],sigXSe=0.01):
    histosSig = []
    labelsSig = []
    histosBkg = []
    edgesBkg  = []
    edgesSig  = []
    labelsBkg = []
    colorsBkg = []
    colorsSig = []
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_nm1_{1}".format(sample,cut))
        if("X" in sample):
            hist, edges = hist2array(h,return_edges=True)
            hist = hist*(sigXSec/0.01)
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
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

    hep.histplot(histosBkg,edgesBkg[0], stack=True,ax=ax,label = labelsBkg, histtype="fill",facecolor=colorsBkg,edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h,edgesSig[i],stack=False,ax=ax,label = labelsSig[i],linewidth=3,zorder=2,color=colorsSig[i])
    plt.yscale("log")
    ax.legend()
    ax.set_xlabel(xTitle)
    ax.set_ylabel(yTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    hep.cms.lumitext(text='39.5 $fb^{-1} (13 TeV)$', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc=(0.02,0.5),ncol=2)#loc = 'best'
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

def getInvMass_h(h3d,rebin):
    hInvMass = h3d.ProjectionZ("projecionMJJ")
    hInvMass.Rebin(rebin) 
    hist, edges = hist2array(hInvMass,return_edges=True)
    return hist,edges[0]

def getmJY_h(h,rebin):
    h.Rebin(rebin) 
    hist, edges = hist2array(h,return_edges=True)
    return hist,edges[0]

def plotMJY(data,outFile,tagger,region,rebin=1,xTitle="",yTitle="",yRange=[],xRange=[],sigXSec=0.01):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    colorsBkg = []
    colorsSig = []
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        hTemp = tempFile.Get("{0}_mjY_{1}_{2}".format(sample,tagger,region))
        if("X" in sample):
            h,edges = getmJY_h(hTemp,rebin)
            #signal is normalized to 10fb in .root file
            h = h*(sigXSec/0.01)
            histosSig.append([h,edges])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
        elif("data_obs" in sample):
            continue   
        else:
            h,edges = getmJY_h(hTemp,rebin)
            histosBkg.append([h,edges])
            labelsBkg.append(sample_cfg["label"])
            if(sample_cfg["label"]=="ttbar"):
                labelsBkg[-1]=r"t$\bar{t}$"#json restrictions workaround
            colorsBkg.append(sample_cfg["color"])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    stackHistosBkg = []
    stackEdgesBkg  = []
    for i,h in enumerate(histosBkg):
        stackHistosBkg.append(h[0])
        stackEdgesBkg.append(h[1])

    hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=True,ax=ax,label = labelsBkg,facecolor=colorsBkg, histtype="fill",edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3,color=colorsSig[i])
    plt.yscale("log")
    ax.legend()
    #ax.set_xlabel(xTitle)
    #ax.set_ylabel(yTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    hep.cms.lumitext(text='39.5 $fb^{-1} (13 TeV)$', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc=(0.02,0.5),ncol=2)#loc = 'best'
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

def plotMJJ(data,outFile,tagger,region,rebin=1,xTitle="",yTitle="",yRange=[],xRange=[],sigXSec=0.01):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    colorsBkg = []
    colorsSig = []
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        h3d = tempFile.Get("{0}_mjY_mjH_mjjHY_{1}_{2}".format(sample,tagger,region))
        if("X" in sample):
            h,edges = getInvMass_h(h3d,rebin)
            #signal is normalized to 10fb in .root file
            h = h*(sigXSec/0.01)
            histosSig.append([h,edges])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
        elif("data_obs" in sample):
            continue   
        else:
            h,edges = getInvMass_h(h3d,rebin)
            histosBkg.append([h,edges])
            labelsBkg.append(sample_cfg["label"])
            if(sample_cfg["label"]=="ttbar"):
                labelsBkg[-1]=r"t$\bar{t}$"#json restrictions workaround
            colorsBkg.append(sample_cfg["color"])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    stackHistosBkg = []
    stackEdgesBkg  = []
    for i,h in enumerate(histosBkg):
        stackHistosBkg.append(h[0])
        stackEdgesBkg.append(h[1])

    hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=True,ax=ax,label = labelsBkg,facecolor=colorsBkg, histtype="fill",edgecolor='black')
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3,color=colorsSig[i])
    plt.yscale("log")
    ax.legend()
    #ax.set_xlabel(xTitle)
    #ax.set_ylabel(yTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        ax.set_ylim(yRange)
    if(xRange):
        ax.set_xlim(xRange)
    hep.cms.lumitext(text='39.5 $fb^{-1} (13 TeV)$', ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    plt.legend(loc=(0.02,0.5),ncol=2)#loc = 'best'
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))
    
    plt.clf()

def plotVarStackMC(data,var,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,luminosity="35.9"):
    histos = []
    labels  = []
    edges   = []
    colors  = []
    histosSig  = []
    labelsSig  = []
    colorsSig  = []
    edgesSig   = []

    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        print(sample)
        tempFile = r.TFile.Open(sample_cfg["file"])
        if("jetht" in sample.lower() or "data" in sample.lower()):
            #not plotting data
            continue
        elif("X" in sample):
            h = tempFile.Get("{0}_{1}".format(sample,var))
            h.RebinX(rebinX)
            hist, edges = hist2array(h,return_edges=True)
            histosSig.append([hist,edges[0]])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
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
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3,color=colorsSig[i])
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
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 10 fb", horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=ax, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc=(0.02,0.6),ncol=2)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()


def plotVarStack(data,var,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,luminosity="35.9"):
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
        if("jetht" in sample.lower() or "data" in sample.lower()):
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
    hep.cms.lumitext(text=lumiText, ax=ax, fontname=None, fontsize=None,loc='best')
    hep.cms.text("WiP",loc='best')
    plt.legend(loc='best',ncol=1)#loc = 'best'

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

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
    odir = "results/plots/{0}/".format(options.year)

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
        # nMinusOnePlotWithData(data,"pnet0","{0}/nm1/log/pnet0.pdf".format(odir),xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],yRange=[1,10e14],sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotWithData(data,"pnet1","{0}/nm1/log/pnet1.pdf".format(odir),xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],yRange=[1,10e14],sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotWithData(data,"DeltaEta","{0}/nm1/log/DeltaEta.pdf".format(odir),xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],yRange=[1,10e14],sigXSec=1.,luminosity=luminosity)
        # nMinusOnePlotWithData(data,"mjjHY","{0}/nm1/log/mjjHY.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[300,3000.],yRange=[1,10e16],sigXSec=1.,luminosity=luminosity)

        # nMinusOnePlotWithData(data,"pnet0","{0}/nm1/lin/pnet0.pdf".format(odir),xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False,sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotWithData(data,"pnet1","{0}/nm1/lin/pnet1.pdf".format(odir),xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False,sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotWithData(data,"DeltaEta","{0}/nm1/lin/DeltaEta.pdf".format(odir),xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],log=False,sigXSec=1.,luminosity=luminosity)
        # nMinusOnePlotWithData(data,"mjjHY","{0}/nm1/lin/mjjHY.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[0,3000.],log=False,sigXSec=1.,luminosity=luminosity)

        # nMinusOnePlotSeparated(data,"pnet0","{0}/nm1_separated/log/pnet0.pdf".format(odir),xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotSeparated(data,"pnet1","{0}/nm1_separated/log/pnet1.pdf".format(odir),xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotSeparated(data,"DeltaEta","{0}/nm1_separated/log/DeltaEta.pdf".format(odir),xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],sigXSec=1.,luminosity=luminosity)
        # nMinusOnePlotSeparated(data,"mjjHY","{0}/nm1_separated/log/mjjHY.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[0,3000.],sigXSec=1.,luminosity=luminosity)
        # plt.close('all')

        # nMinusOnePlotSeparated(data,"pnet0","{0}/nm1_separated/lin/pnet0.pdf".format(odir),xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False,sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotSeparated(data,"pnet1","{0}/nm1_separated/lin/pnet1.pdf".format(odir),xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False,sigXSec=1.,luminosity=luminosity,rebinX=10)
        # nMinusOnePlotSeparated(data,"DeltaEta","{0}/nm1_separated/lin/DeltaEta.pdf".format(odir),xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],log=False,sigXSec=1.,luminosity=luminosity)
        # nMinusOnePlotSeparated(data,"mjjHY","{0}/nm1_separated/lin/mjjHY.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[0,3000.],log=False,sigXSec=1.,luminosity=luminosity)

        # plotVarStackMC(data,"fail_SR_mJJ","{0}/kinematic/mJJ_SR_fail.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStackMC(data,"pass_SR_mJJ","{0}/kinematic/mJJ_SR_pass.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e4],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStackMC(data,"fail_VR_mJJ","{0}/kinematic/mJJ_VR_fail.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e8],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStackMC(data,"pass_VR_mJJ","{0}/kinematic/mJJ_VR_pass.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6],log=True,rebinX=1,luminosity=luminosity)

        plotVarStackMC(data,"fail_SR_mJY","{0}/kinematic/mJY_SR_fail.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e6],log=True,rebinX=2,luminosity=luminosity)
        plotVarStackMC(data,"pass_SR_mJY","{0}/kinematic/mJY_SR_pass.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e4],log=True,rebinX=2,luminosity=luminosity)
        plotVarStackMC(data,"fail_VR_mJY","{0}/kinematic/mJY_VR_fail.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e8],log=True,rebinX=2,luminosity=luminosity)
        plotVarStackMC(data,"pass_VR_mJY","{0}/kinematic/mJY_VR_pass.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e6],log=True,rebinX=2,luminosity=luminosity)
        cutFlowWithData(data,"{0}/cutflows/total_cutflow.pdf".format(odir),xTitle="",yTitle="Events",xRange=[0.5,12.5],yRange=[None,10e18],log=True,sigXSec=1.0,luminosity=luminosity)

