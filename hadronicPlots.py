import matplotlib
matplotlib.use('Agg')

import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
from root_numpy import hist2array

def histToScatter(h):
    xVals  = []
    yVals  = []
    errors = []

    for i in range(1,h.GetNbinsX()+1):
        yVals.append(h.GetBinContent(i))
        xVals.append(h.GetBinCenter(i))
        errors.append(h.GetBinError(i))

    xVals=np.asarray(xVals)
    yVals=np.asarray(yVals)
    errors=np.asarray(errors)

    return xVals,yVals,errors   

def plotShapeUnc(file,sample,unc,region,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,luminosity="35.9",projection="MJY",text=""):
    histos = []
    labels  = []
    edges   = []
    colors  = ["black","blue","red"]
    variations = ["nom","{0}Down".format(unc),"{0}Up".format(unc)]
    tempFile = r.TFile.Open(file)
    for variation in variations:
        h2 = tempFile.Get("{0}_mJY_mJJ_{1}_{2}".format(sample,region,variation))
        if(projection=="MJY"):
            h = h2.ProjectionX("{0}_mJY_{1}_{2}".format(sample,region,variation),1,-1)
        else:
            h = h2.ProjectionY("{0}_mJJ_{1}_{2}".format(sample,region,variation),1,-1)
        hist, hEdges = hist2array(h,return_edges=True)
        histos.append(hist)
        edges.append(hEdges[0])
        labels.append("{0} {1}".format(sample,variation))
    tempFile.Close()

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
    plt.legend(loc='best',ncol=1)#loc = 'best'
    if(text):
        plt.text(0.75, 0.75, text, horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=18)

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

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

def cutFlowWithData(data,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,sigXSec=0.01,luminosity="35.9",scaleQCD=False):
    histosSig  = []
    colorsSig  = []
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
        h = tempFile.Get("{0}_cutflow_nom".format(sample))
        hist, edges = hist2array(h,return_edges=True)
        # hist = np.delete(hist,0)#removing count before triggers
        # edges[0] = np.delete(edges[0],0)
        if("MX" in sample):
            #continue
            hist = hist*(sigXSec/0.01)#assuming signal is lumiscaled to 10fb
            histosSig.append(hist)
            edgesSig.append(edges[0])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])

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
    if(scaleQCD):
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
       hep.histplot(h,edgesSig[i],stack=False,ax=axs[0],label = labelsSig[i],linewidth=3,zorder=2,color=colorsSig[i])
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
    plt.legend(loc=(0.02,0.60),ncol=2)#loc = 'best'
    plt.text(0.28, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 pb", horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.1,1.9])
    axs[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
    axisTicks = axs[1].get_xticks().tolist()
    axisTicks = ["zero","Processed", "Skimmed", "Trigger", "Eta", "JetID", "$p_{T}$", "Lepton Veto","$M_{JJ}$","Higgs mass","$\Delta\eta$","TT","LL","AL_T","AL_L","AL_AL"]
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
        h = tempFile.Get("{0}_nm1_{1}_nom".format(sample,cut))
        h.RebinX(rebinX)
        if("MX" in sample):
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

def plotMJY(data,outFile,region,rebin=1,xTitle="",yTitle="",yRange=[],xRange=[],luminosity="35.9",log=False,firstybin=1,lastybin=-1,stack=True,text=""):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    colorsBkg = []
    colorsSig = []
    ymin = 0
    ymax = 0
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        #tag = sample_cfg["tag"]
        tag = sample
        h2d = tempFile.Get("{0}_mJY_mJJ_{1}_nom".format(tag,region))
        #h2d = tempFile.Get("mJJ_mJY_{0}_{1}".format(region,tag))
        if(ymin==0):
            ymin = h2d.GetYaxis().GetBinLowEdge(firstybin)
            if(lastybin==-1):
                lastybin=h2d.GetNbinsY()
            ymax = h2d.GetYaxis().GetBinUpEdge(lastybin)
        if("X" in sample):
            hInvMass = h2d.ProjectionX("{0}_mJY_{1}".format(tag,region),firstybin,lastybin)#avoid underflow
            hInvMass.Rebin(rebin)
            hist, edges = hist2array(hInvMass,return_edges=True)

            histosSig.append([hist,edges[0]])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
        elif("data_obs" in sample or "JetHT" in sample):
                continue   
        else:
            hInvMass = h2d.ProjectionX("{0}_mJY_{1}".format(tag,region),firstybin,lastybin)#avoid underflow
            hInvMass.Rebin(rebin)
            hist, edges = hist2array(hInvMass,return_edges=True)
            histosBkg.append([hist,edges[0]])
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

    hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=stack,ax=ax,label = labelsBkg,facecolor=colorsBkg, histtype="fill",edgecolor='black')
    #hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=stack,ax=ax,label = labelsBkg,color=colorsBkg)
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3,color=colorsSig[i])
    if(log):
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

    lumiText = luminosity + " $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(text=lumiText, ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.text(0.05, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 10 fb", horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=25)
    MJJrangeText = str(ymin) + "$<M_{JJ}$<" + str(ymax)
    plt.text(0.05, 0.65, MJJrangeText, horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=25)
    if(text):
        plt.text(0.05, 0.55, text, horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=25)
    plt.legend(loc=(0.5,0.5),ncol=1,fontsize=25)#loc = 'best'
    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))
    
    plt.clf()

def plotMJJ(data,outFile,region,rebin=1,xTitle="",yTitle="",yRange=[],xRange=[],luminosity="35.9",log=False,firstxbin=1,lastxbin=-1,stack=True,text=""):
    histosSig = []
    labelsSig = []
    histosBkg = []
    labelsBkg = []
    colorsBkg = []
    colorsSig = []
    xmin = 0
    xmax = 0
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        #tag = sample_cfg["tag"]
        tag = sample
        h2d = tempFile.Get("{0}_mJY_mJJ_{1}_nom".format(tag,region))
        if(xmin==0):
            xmin = h2d.GetXaxis().GetBinLowEdge(firstxbin)
            if(lastxbin==-1):
                lastxbin=h2d.GetNbinsX()
            xmax = h2d.GetXaxis().GetBinUpEdge(lastxbin)
        if("X" in sample):
            hInvMass = h2d.ProjectionY("{0}_mJJ_{1}".format(tag,region),firstxbin,lastxbin)#avoid underflow
            hInvMass.Rebin(rebin)
            hist, edges = hist2array(hInvMass,return_edges=True)

            histosSig.append([hist,edges[0]])
            labelsSig.append(sample_cfg["label"])
            colorsSig.append(sample_cfg["color"])
        elif("data_obs" in sample or "JetHT" in sample):
            continue   
        else:
            hInvMass = h2d.ProjectionY("{0}_mJJ_{1}".format(tag,region),firstxbin,lastxbin)#avoid underflow
            hInvMass.Rebin(rebin)
            hist, edges = hist2array(hInvMass,return_edges=True)
            histosBkg.append([hist,edges[0]])
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

    hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=stack,ax=ax,label = labelsBkg,facecolor=colorsBkg, histtype="fill",edgecolor='black')
    #hep.histplot(stackHistosBkg,stackEdgesBkg[0],stack=stack,ax=ax,label = labelsBkg,color=colorsBkg)
    for i,h in enumerate(histosSig):
        hep.histplot(h[0],h[1],stack=False,ax=ax,label = labelsSig[i],zorder=2,linewidth=3,color=colorsSig[i])
    if(log):
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

    lumiText = luminosity + " $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(text=lumiText, ax=None, fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.text(0.05, 0.85, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 10 fb", horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=25)
    MJYrangeText = str(xmin) + "$<M_{JY}$<" + str(xmax)
    plt.text(0.05, 0.65, MJYrangeText, horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=25)
    if(text):
        plt.text(0.05, 0.55, text, horizontalalignment='left',verticalalignment='center',transform=ax.transAxes, fontsize=25)
    plt.legend(loc=(0.5,0.5),ncol=1,fontsize=25)#loc = 'best'
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


def plotProjectionDataMC(data,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,projection="X",luminosity="35.9",text=""):
    histos = []
    labels  = []
    edgesBkg   = []
    colors  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element)
    labelsData = []
    hRatio     = 0
    hRootBkg   = 0
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        print(sample)
        tempFile = r.TFile.Open(sample_cfg["file"])
        if("jetht" in sample.lower() or "data" in sample.lower()):
            h2    = tempFile.Get(sample_cfg["histo"])
            if(projection=="X"):
                h = h2.ProjectionX("px_{0}".format(sample),1,-1)#1 avoids underflow
            else:
                h = h2.ProjectionY("py_{0}".format(sample),1,-1)#1 avoids underflow
            h.RebinX(rebinX)
            h.SetDirectory(0)
            hRatio = h
            hist, edges = hist2array(h,return_edges=True)
            histosData.append(hist)
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])
            continue  
        else:
            h2    = tempFile.Get(sample_cfg["histo"])
            if(projection=="X"):
                h = h2.ProjectionX("px_{0}".format(sample),1,-1)
            else:
                h = h2.ProjectionY("py_{0}".format(sample),1,-1)
            h.RebinX(rebinX)
            h.SetDirectory(0)
            if(hRootBkg):
                hRootBkg.Add(h)
            else:
                hRootBkg = h

            hist, edges = hist2array(h,return_edges=True)
            histos.append(hist)
            edgesBkg.append(edges[0])
            labels.append(sample_cfg["label"])
            colors.append(sample_cfg["color"])
            if(sample_cfg["label"]=="TTbar"):
                labels[-1]=r"t$\bar{t}$"#json restrictions workaround

    hRatio.Divide(hRootBkg)
    hRatioCentres, hRatioVals, hRatioErrors = histToScatter(hRatio)


    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    if(log):
        axs[0].set_yscale("log")
    centresData = (edgesData[0][:-1] + edgesData[0][1:])/2.
    errorsData  = np.sqrt(histosData[0])

    hep.histplot(histos,edges[0],stack=True,ax=axs[0],label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    axs[0].legend()
    plt.ylabel(yTitle, horizontalalignment='right', y=1.0)
    #axs[1].set_xlabel(xTitle)
    axs[1].set_ylabel("Data/MC")
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc='best',ncol=1)#loc = 'best'

    if(text):
        plt.text(0.75, 0.45, text, horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)


    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.0,2.0])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    plt.errorbar(hRatioCentres,hRatioVals, yerr=hRatioErrors, fmt='o',color="k") 

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
        nMinusOnePlotWithData(data,"pnet0","{0}/nm1/log/pnet0.pdf".format(odir),xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],yRange=[1,10e14],sigXSec=1.,luminosity=luminosity,rebinX=10)
        nMinusOnePlotWithData(data,"pnet1","{0}/nm1/log/pnet1.pdf".format(odir),xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],yRange=[1,10e14],sigXSec=1.,luminosity=luminosity,rebinX=10)
        nMinusOnePlotWithData(data,"DeltaEta","{0}/nm1/log/DeltaEta.pdf".format(odir),xTitle="$\Delta \eta (J1,J2)$",yTitle="Events/0.05",xRange=[0,4.5],yRange=[1,10e14],sigXSec=1.,luminosity=luminosity)
        nMinusOnePlotWithData(data,"MJJ","{0}/nm1/log/MJJ.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[300,3000.],yRange=[1,10e16],sigXSec=1.,luminosity=luminosity)

        nMinusOnePlotWithData(data,"pnet0","{0}/nm1/lin/pnet0.pdf".format(odir),xTitle="Leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False,sigXSec=1.,luminosity=luminosity,rebinX=10)
        nMinusOnePlotWithData(data,"pnet1","{0}/nm1/lin/pnet1.pdf".format(odir),xTitle="Sub-leading jet ParticleNet score",yTitle="Events/0.01",xRange=[0,1],log=False,sigXSec=1.,luminosity=luminosity,rebinX=10)
        nMinusOnePlotWithData(data,"DeltaEta","{0}/nm1/lin/DeltaEta.pdf".format(odir),xTitle="$\Delta \eta (j1,j2)$",yTitle="Events/0.05",xRange=[0,4.5],log=False,sigXSec=1.,luminosity=luminosity)
        nMinusOnePlotWithData(data,"MJJ","{0}/nm1/lin/MJJ.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[0,3000.],log=False,sigXSec=1.,luminosity=luminosity)

        # plotVarStackMC(data,"fail_SR_mJJ","{0}/kinematic/mJJ_SR_fail.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStackMC(data,"pass_SR_mJJ","{0}/kinematic/mJJ_SR_pass.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e4],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStackMC(data,"fail_VR_mJJ","{0}/kinematic/mJJ_VR_fail.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e8],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStackMC(data,"pass_VR_mJJ","{0}/kinematic/mJJ_VR_pass.pdf".format(odir),xTitle="Dijet invariant mass [GeV]",yTitle="Events/100 GeV",xRange=[750,2050],yRange=[1,10e6],log=True,rebinX=1,luminosity=luminosity)

        # plotVarStackMC(data,"fail_SR_mJY","{0}/kinematic/mJY_SR_fail.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e6],log=True,rebinX=2,luminosity=luminosity)
        # plotVarStackMC(data,"pass_SR_mJY","{0}/kinematic/mJY_SR_pass.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e4],log=True,rebinX=2,luminosity=luminosity)
        # plotVarStackMC(data,"fail_VR_mJY","{0}/kinematic/mJY_VR_fail.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e8],log=True,rebinX=2,luminosity=luminosity)
        # plotVarStackMC(data,"pass_VR_mJY","{0}/kinematic/mJY_VR_pass.pdf".format(odir),xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20 GeV",xRange=[30,330],yRange=[1,10e6],log=True,rebinX=2,luminosity=luminosity)
        cutFlowWithData(data,"{0}/cutflows/total_cutflow.pdf".format(odir),xTitle="",yTitle="Events",xRange=[0.5,15.5],yRange=[None,10e13],log=True,sigXSec=1.0,luminosity=luminosity)
        #Money plots
        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_TT_lin.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0,None],xRange=[1000,3000],luminosity=luminosity,log=False,text="{0}, TT region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_TT_lin.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[60,360],luminosity=luminosity,log=False,text="{0}, TT region".format(year))
        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_LL_lin.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0,None],xRange=[1000,3000],luminosity=luminosity,log=False,text="{0}, LL region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_LL_lin.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[60,360],luminosity=luminosity,log=False,text="{0}, LL region".format(year))

        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_TT_SR_lin.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0,None],xRange=[1000,3000],luminosity=luminosity,log=False,firstxbin=1,lastxbin=4,text="{0}, TT region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_TT_SR_lin.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[60,360],luminosity=luminosity,log=False,firstybin=6,lastybin=10,text="{0}, TT region".format(year))
        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_LL_SR_lin.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0,None],xRange=[1000,3000],luminosity=luminosity,log=False,firstxbin=1,lastxbin=4,text="{0}, LL region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_LL_SR_lin.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[60,360],luminosity=luminosity,log=False,firstybin=6,lastybin=10,text="{0}, LL region".format(year))

        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_TT_log.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0.01,10e6],xRange=[1000,3000],luminosity=luminosity,log=True,text="{0}, TT region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_TT_log.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0.01,10e6],xRange=[60,360],luminosity=luminosity,log=True,text="{0}, TT region".format(year))
        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_LL_log.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0.01,10e6],xRange=[1000,3000],luminosity=luminosity,log=True,text="{0}, LL region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_LL_log.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0.01,10e6],xRange=[60,360],luminosity=luminosity,log=True,text="{0}, LL region".format(year))

        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_TT_SR_log.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0.01,10e6],xRange=[1000,3000],luminosity=luminosity,log=True,firstxbin=1,lastxbin=4,text="{0}, TT region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_TT_SR_log.pdf".format(odir,year),"TT",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0.01,10e6],xRange=[60,360],luminosity=luminosity,log=True,firstybin=6,lastybin=10,text="{0}, TT region".format(year))
        plotMJJ(data,"{0}/moneyPlots/{1}_MJJ_LL_SR_log.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JJ}$ [GeV]",yTitle="Events/100 GeV",yRange=[0.01,10e6],xRange=[1000,3000],luminosity=luminosity,log=True,firstxbin=1,lastxbin=4,text="{0}, LL region".format(year))
        plotMJY(data,"{0}/moneyPlots/{1}_MJY_LL_SR_log.pdf".format(odir,year),"LL",rebin=1,xTitle="$M_{JY}$ [GeV]",yTitle="Events/20 GeV",yRange=[0.01,10e6],xRange=[60,360],luminosity=luminosity,log=True,firstybin=6,lastybin=10,text="{0}, LL region".format(year))
        #Variations
        # variations = ["jes","jer","jmr","jms"]
        # for sample, sample_cfg in data.items():
        #     for variation in variations:
        #         plotShapeUnc(sample_cfg["file"],sample,variation,"TT","results/variations/WP_0.8_0.9/2016/{0}_{1}_TT_MJY.pdf".format(sample, variation),xTitle="MJY[GeV]",yTitle="Events/20 GeV",yRange=[1.,1000],xRange=[],log=True,luminosity="35.9",projection="MJY",text="WPs=[0.8,0.9] TT region")
        #         plotShapeUnc(sample_cfg["file"],sample,variation,"TT","results/variations/WP_0.8_0.9/2016/{0}_{1}_TT_MJJ.pdf".format(sample, variation),xTitle="MJJ[GeV]",yTitle="Events/100 GeV",yRange=[1.,1000],xRange=[],log=True,luminosity="35.9",projection="MJJ",text="WPs=[0.8,0.9] TT region")
        #         plotShapeUnc(sample_cfg["file"],sample,variation,"LL","results/variations/WP_0.8_0.9/2016/{0}_{1}_LL_MJY.pdf".format(sample, variation),xTitle="MJY[GeV]",yTitle="Events/20 GeV",yRange=[1.,1000],xRange=[],log=True,luminosity="35.9",projection="MJY",text="WPs=[0.8,0.9] LL region")
        #         plotShapeUnc(sample_cfg["file"],sample,variation,"LL","results/variations/WP_0.8_0.9/2016/{0}_{1}_LL_MJJ.pdf".format(sample, variation),xTitle="MJJ[GeV]",yTitle="Events/100 GeV",yRange=[1.,1000],xRange=[],log=True,luminosity="35.9",projection="MJJ",text="WPs=[0.8,0.9] LL region")








