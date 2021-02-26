import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib
from root_numpy import hist2array
import matplotlib.ticker as ticker

matplotlib.use('Agg')

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

def cutFlowWithData(data,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,sigXSec=0.01,luminosity="35.9"):
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
        if not "data" in sample:
            h = tempFile.Get("{0}_cutflow_nom".format(sample))
        else:
            h = tempFile.Get("{0}_cutflow".format(sample))

        hist, edges = hist2array(h,return_edges=True)
        if("data_obs" in sample or "SingleMuon" in sample):
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
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.01})
    plt.subplots_adjust(left=0.11, bottom=0.2, right=0.95, top=0.90)
    axs = axs.flatten()
    plt.sca(axs[0])
    hep.histplot(histosBkg,edgesBkg[0],stack=True,ax=axs[0],label = labelsBkg,edgecolor='black', linewidth=1.2, histtype="fill",facecolor=colorsBkg)
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    if(log):
        axs[0].set_yscale("log")
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    axs[0].set_ylabel(yTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    axs[1].set_ylabel("Data/Bkg")
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc = 'best',ncol=2)

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.4,1.6])
    axs[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
    axisTicks = axs[1].get_xticks().tolist()
    axisTicks = ["zero", "Skimmed", "Trigger", "Tight lepton", "Mu $p_{T}$>40GeV","MET>60","Lepton-side b-tagged AK4","HT>500","ProbeJet found","ST>500"]
    axs[1].set_xticklabels(axisTicks,rotation=45,fontsize=14)
    plt.scatter(centresData, hRatio,color="k")
    plt.errorbar(centresData,hRatio, yerr=errorsRatio, fmt='o',color="k")    


    print("Saving {0}".format(outFile))
    plt.savefig(outFile)
    plt.savefig(outFile.replace("pdf","png"))

    plt.clf()

def plotVarStack(data,var,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=True,rebinX=1,luminosity="0",text=""):
    histos = []
    labels  = []
    edges   = []
    colors  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element) to be similar to other processes
    labelsData = []
    rHistoBkg = False
    rHistoData= False
    data = sorted(data.items(), key=lambda x: x[1]["order"])#VERY HANDY, reads samples in order
    for sample, sample_cfg in data:
        print(sample)
        tempFile = r.TFile.Open(sample_cfg["file"])
        if("muon" in sample.lower() or "data" in sample.lower()):
            if("STbefore" in var):
                var=var.replace("before","")
            print("{0}_{1}".format(sample,var))
            h = tempFile.Get("{0}_{1}".format(sample,var))
            h.SetDirectory(0)
            h.RebinX(rebinX)
            hist, edges = hist2array(h,return_edges=True)
            histosData.append(hist)
            if(rHistoData):
                rHistoData.Add(h)
            else:
                rHistoData = h
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])
            continue  
        else:
            h = tempFile.Get("{0}_{1}_nom".format(sample,var))
            h.SetDirectory(0)
            h.RebinX(rebinX)
            hist, hEdges = hist2array(h,return_edges=True)
            histos.append(hist)
            if(rHistoBkg):
                rHistoBkg.Add(h)
            else:
                rHistoBkg = h
            edges.append(hEdges[0])
            labels.append(sample_cfg["label"])
            colors.append(sample_cfg["color"])
            if(sample_cfg["label"]=="ttbar"):
                labels[-1]=r"t$\bar{t}$"#json restrictions workaround


    centresData = (edgesData[0][:-1] + edgesData[0][1:])/2.
    errorsData  = np.sqrt(histosData[0])
    hTotalBkg = np.sum(histos,axis=0)
    hRatio = np.divide(histosData[0],hTotalBkg)
    rHistoData.Divide(rHistoBkg)
    hRatioCentres, hRatioVals, hRatioErrors = histToScatter(rHistoData)
    
    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])

    hep.histplot(histos,edges[0],stack=True,ax=axs[0],label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    if(log):
        axs[0].set_yscale("log")
    axs[0].legend()
    axs[0].set_ylabel(yTitle)
    axs[1].set_xlabel(xTitle)
    axs[1].set_ylabel("Data/MC")
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    if(text):
        plt.text(0.1, 0.85,text, horizontalalignment='left',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc='best',ncol=1)#loc = 'best'

    plt.sca(axs[1])#switch to lower pad
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.49,1.51])
    plt.errorbar(hRatioCentres,hRatioVals, yerr=hRatioErrors, fmt='o',color="k") 


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
            h = tempFile.Get("{0}_mSD{1}_I".format(sample,pTBin))
            h.RebinX(rebinX)
            hist, edges = hist2array(h,return_edges=True)
            histosData.append(hist)
            edgesData.append(edges[0])
            labelsData.append(sample_cfg["label"])
            continue  
        if(roothistos==[]):
            hqq = tempFile.Get("{0}_unmatched_mSD{1}_I".format(sample,pTBin))
            hbq = tempFile.Get("{0}_bqq_mSD{1}_I".format(sample,pTBin))
            hbqq = tempFile.Get("{0}_bq_mSD{1}_I".format(sample,pTBin))
            hother = tempFile.Get("{0}_qq_mSD{1}_I".format(sample,pTBin))
            hqq.SetDirectory(0)
            hbq.SetDirectory(0)
            hbqq.SetDirectory(0)
            hother.SetDirectory(0)
            roothistos.append(hqq)
            roothistos.append(hbq)
            roothistos.append(hbqq)
            roothistos.append(hother)
        else:
            hqq = tempFile.Get("{0}_unmatched_mSD{1}_I".format(sample,pTBin))
            hbq = tempFile.Get("{0}_bqq_mSD{1}_I".format(sample,pTBin))
            hbqq = tempFile.Get("{0}_bq_mSD{1}_I".format(sample,pTBin))
            hother = tempFile.Get("{0}_qq_mSD{1}_I".format(sample,pTBin))
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

    #convert data to scatter
    centresData = (edgesData[0][:-1] + edgesData[0][1:])/2.
    errorsData  = np.sqrt(histosData[0])
    hTotalBkg = np.sum(histos,axis=0)
    hRatio = np.divide(histosData[0],hTotalBkg)

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])


    hep.histplot(histos,edges[0],stack=True,ax=axs[0],label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    plt.errorbar(centresData,histosData[0], yerr=errorsData, fmt='o',color="k",label = labelsData[0])    
    if(log):
        axs[0].set_yscale("log")
    axs[0].legend()
    axs[0].set_ylabel(yTitle)
    axs[1].set_xlabel(xTitle)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    axs[1].set_ylabel("Data/MC")
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    lumiText = luminosity + " $fb^{-1} (13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    if(text):
        plt.text(0.1, 0.85,text, horizontalalignment='left',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)
    plt.legend(loc='best',ncol=1)#loc = 'best'

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.49,1.51])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.scatter(centresData,hRatio,color="k")    

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
        plotVarStack(data,"MET_I","results/plots/semileptonic/{0}/MET{0}_I.png".format(year),xTitle="MET [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[0,1000],log=True,rebinX=1,luminosity=luminosity)
        plotVarStack(data,"HT_I","results/plots/semileptonic/{0}/HT{0}_I.png".format(year),xTitle="HT [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)
        plotVarStack(data,"ST_I","results/plots/semileptonic/{0}/ST{0}_I.png".format(year),xTitle="ST [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e5],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)
        plotVarStack(data,"lepton_pT_I","results/plots/semileptonic/{0}/lepton_pT{0}_I.png".format(year),xTitle="Muon $p_{T}$ [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[0,1000],log=True,rebinX=1,luminosity=luminosity)
        # cutFlowWithData(data,"results/plots/semileptonic/{0}/cutflow_{0}.png".format(year),xTitle="",yTitle="Events",xRange=[1.5,10.5],yRange=[None,10e15],log=True,sigXSec=1.0,luminosity=luminosity)
        # # plotVarStack(data,"MET_I_noCor","results/plots/semileptonic/{0}/MET{0}_I_noCor.png".format(year),xTitle="MET [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[0,1000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"HT_I_noCor","results/plots/semileptonic/{0}/HT{0}_I_noCor.png".format(year),xTitle="HT [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"ST_I_noCor","results/plots/semileptonic/{0}/ST{0}_I_noCor.png".format(year),xTitle="ST [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e5],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)
        # plotVarStack(data,"lepton_pT_I_noCor","results/plots/semileptonic/{0}/lepton_pT{0}_I_noCor.png".format(year),xTitle="Muon $p_{T}$ [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e4],xRange=[0,1000],log=True,rebinX=1,luminosity=luminosity)


        # plotVarStack(data,"mSD_I","results/plots/semileptonic/{0}/mSD{0}_I.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[10e-1,10e6],xRange=[60,210],log=True,luminosity=luminosity,text="ParticleNet inclusive")
        # plotVarStack(data,"mSD_I","results/plots/semileptonic/{0}/mSD{0}_lin_I.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,4000],xRange=[60,210],log=False,luminosity=luminosity,text="ParticleNet inclusive")
        # plotVarStack(data,"mSD_T","results/plots/semileptonic/{0}/mSD{0}_T.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[10e-1,10e6],xRange=[60,210],log=True,luminosity=luminosity,text="ParticleNet > 0.95")
        # plotVarStack(data,"mSD_T","results/plots/semileptonic/{0}/mSD{0}_lin_T.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,300],xRange=[60,210],log=False,luminosity=luminosity,text="ParticleNet > 0.95")
        # plotVarStack(data,"mSD_L","results/plots/semileptonic/{0}/mSD{0}_L.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[10e-1,10e6],xRange=[60,210],log=True,luminosity=luminosity,text="0.8 < ParticleNet < 0.95")
        # plotVarStack(data,"mSD_L","results/plots/semileptonic/{0}/mSD{0}_lin_L.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,500],xRange=[60,210],log=False,luminosity=luminosity,text="0.8 < ParticleNet < 0.95")
        # plotVarStack(data,"mSD_AT","results/plots/semileptonic/{0}/mSD{0}_AT.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[10e-1,10e6],xRange=[60,210],log=True,luminosity=luminosity,text="ParticleNet < 0.8")
        # plotVarStack(data,"mSD_AT","results/plots/semileptonic/{0}/mSD{0}_lin_AT.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,4000],xRange=[60,210],log=False,luminosity=luminosity,text="ParticleNet < 0.8")





        #plotVarStack(data,"STbefore_I","results/plots/semileptonic/{0}/STbefore{0}_I.png".format(year),xTitle="ST [GeV]",yTitle="Events/100 GeV",yRange=[10e-1,10e5],xRange=[400,2000],log=True,rebinX=1,luminosity=luminosity)


        # plotTagJetCategories(data,"results/plots/semileptonic/{0}/mSDCats{0}.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Jets/20 GeV",yRange=[10e0,3500],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        # plotTagJetCategories(data,"results/plots/semileptonic/{0}/mSDCats_pTLo{0}_I.png".format(year),pTBin="Lo",xTitle="Soft drop mass [GeV]",yTitle="Jets/20 GeV",yRange=[0,1000],xRange=[0,300],log=False,rebinX=2,text="300 GeV<$p_{T}$<500 GeV",luminosity=luminosity)
        # plotTagJetCategories(data,"results/plots/semileptonic/{0}/mSDCats_pTHi{0}_I.png".format(year),pTBin="Hi",xTitle="Soft drop mass [GeV]",yTitle="Jets/20 GeV",yRange=[0,1000],xRange=[0,300],log=False,rebinX=2,text="$p_{T}$>500 GeV",luminosity=luminosity)


        # plotVarMCStack(data,"unmatched_mSD_I","results/plots/semileptonic/{0}/mSD_unmatched{0}.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        # plotVarMCStack(data,"bqq_mSD_I","results/plots/semileptonic/{0}/mSD_bqq{0}.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        # plotVarMCStack(data,"bq_mSD_I","results/plots/semileptonic/{0}/mSD_bq{0}.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)
        # plotVarMCStack(data,"qq_mSD_I","results/plots/semileptonic/{0}/mSD_qq{0}.png".format(year),xTitle="Soft drop mass [GeV]",yTitle="Events/20 GeV",yRange=[0,None],xRange=[0,300],log=False,rebinX=2,luminosity=luminosity)

