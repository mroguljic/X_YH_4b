import ROOT as r
import numpy as np
import sys
import matplotlib

matplotlib.use('Agg')
from optparse import OptionParser
from time import sleep
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
from root_numpy import hist2array
import os.path
import ctypes

r.gROOT.SetBatch(True)
r.gStyle.SetOptFit(111)

def rebinHisto(hModel,hToRebin,name,scale=1.0):
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
            i_re = xaxis_re.FindBin(x)
            j_re = yaxis_re.FindBin(y)
            value = hToRebin.GetBinContent(i,j)
            if(value<0.):
                value = 0.
            err = hToRebin.GetBinError(i,j)
            err_re = np.sqrt(hRes.GetBinError(i_re,j_re)*hRes.GetBinError(i_re,j_re)+err*err)
            hRes.Fill(x,y,value)
            hRes.SetBinError(i_re,j_re,err_re)
    hRes.Scale(scale)
    hRes.SetDirectory(0)
    return hRes

def get_binning_x(hLow,hSig,hHigh):
    bins = []
    for i in range(1,hLow.GetNbinsX()+1):
        bins.append(hLow.GetXaxis().GetBinLowEdge(i))
    for i in range(1,hSig.GetNbinsX()+1):
        bins.append(hSig.GetXaxis().GetBinLowEdge(i))
    for i in range(1,hHigh.GetNbinsX()+2):#low edge of overflow is high edge of last bin
        bins.append(hHigh.GetXaxis().GetBinLowEdge(i))
    bins = np.array(bins,dtype='float64')
    return bins

def get_binning_y(hLow,hSig,hHigh):
    #histos should have same binning in Y
    bins = []
    for i in range(1,hLow.GetNbinsY()+2):
        bins.append(hLow.GetYaxis().GetBinLowEdge(i))
    bins = np.array(bins,dtype='float64')
    return bins

def merge_low_sig_high(hLow,hSig,hHigh,hName="temp"):
    n_x_low     = hLow.GetNbinsX()
    n_x_sig     = hSig.GetNbinsX()
    n_x_high    = hHigh.GetNbinsX()
    n_x         = n_x_low + n_x_sig + n_x_high
    n_y         = hLow.GetNbinsY()#assumes Y bins are the same
    bins_x      = get_binning_x(hLow,hSig,hHigh)
    bins_y      = get_binning_y(hLow,hSig,hHigh)
    h_res       = r.TH2F(hName,"",n_x,bins_x,n_y,bins_y)
    #h_res.SetBinErrorOption(1)
    for i in range(1,n_x_low+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+0,j,hLow.GetBinContent(i,j))
            h_res.SetBinError(i+0,j,hLow.GetBinError(i,j))

    for i in range(1,n_x_sig+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+n_x_low,j,hSig.GetBinContent(i,j))
            h_res.SetBinError(i+n_x_low,j,hSig.GetBinError(i,j))

    for i in range(1,n_x_high+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+n_x_sig+n_x_low,j,hHigh.GetBinContent(i,j))
            h_res.SetBinError(i+n_x_sig+n_x_low,j,hHigh.GetBinError(i,j))

    return h_res


def get2DPostfitPlot(file,process,region,tagging):
    #regoin LL/TT, tagging fail/pass
    #process 16_TTbar_bqq, data_obs, qcd
    f       = r.TFile.Open(file)
    hLow    = f.Get("{0}_LOW_{1}_postfit/{2}".format(tagging,region,process))
    hSig    = f.Get("{0}_SIG_{1}_postfit/{2}".format(tagging,region,process))
    hHigh   = f.Get("{0}_HIGH_{1}_postfit/{2}".format(tagging,region,process))
    h2      = merge_low_sig_high(hLow,hSig,hHigh,hName="h2_{0}_{1}_{2}".format(process,region,tagging))
    h2.SetDirectory(0)
    return h2

def getUncBand(totalHistos):
    yLo = []
    yUp = []
    for i in range(1,totalHistos.GetNbinsX()+1):
        errLo  = totalHistos.GetBinErrorLow(i)
        errUp  = totalHistos.GetBinErrorUp(i)
        mcPred = totalHistos.GetBinContent(i)
        yLo.append(mcPred-errLo)
        yUp.append(mcPred+errUp)
    return np.array(yLo), np.array(yUp)


def calculatePull(hData,hTotBkg,uncBand):
    pulls = []
    for i,dataYield in enumerate(hData):
        mcYield     = hTotBkg[i]
        diff        = dataYield-mcYield
        dataErr     = np.sqrt(dataYield)
        mcErr       = (uncBand[1][i]-uncBand[0][i])/2
        sigma       = np.sqrt(mcErr*mcErr+dataErr*dataErr)
        pull        = diff/sigma
        if(dataYield==0):
            pull    = 0
        pulls.append(pull)
    return np.array(pulls)


def plotShapes(hData,hQCD,hTTbar,hTotBkg,uncBand,hSignals,labelsSig,colorsSig,xlabel,outputFile,xRange=[],yRange=[]):

    print(outputFile)
    print("Data\ttotal\tQCD\tTTbar")
    dataYield  = 0
    qcdYield   = 0
    ttbarYield = 0
    bkgYield   = 0
    qcdErr     = ctypes.c_double(1.)
    ttbarErr   = ctypes.c_double(1.)
    bkgErr     = ctypes.c_double(1.)

    dataYield  = hData.Integral()
    qcdYield   = hQCD.IntegralAndError(1,hQCD.GetNbinsX(),qcdErr,"")
    ttbarYield = hTTbar.IntegralAndError(1,hTTbar.GetNbinsX(),ttbarErr,"")
    bkgYield   = hTotBkg.IntegralAndError(1,hTotBkg.GetNbinsX(),bkgErr,"")


    print("{0:.1f}\t{1:.1f} +/- {2:.1f}\t{3:.1f} +/- {4:.1f}\t{5:.1f} +/- {6:.1f}".format(dataYield,bkgYield,bkgErr.value,qcdYield,qcdErr.value,ttbarYield,ttbarErr.value))


    hData, edges    = hist2array(hData,return_edges=True)
    centresData     = (edges[0][:-1] + edges[0][1:])/2.#Bin centres
    errorsData      = np.sqrt(hData)
    xerrorsData     = []

    for i in range(len(edges[0])-1):
        xerror = (edges[0][i+1]-edges[0][i])/2.
        xerrorsData.append(xerror)

    hTTbar, edges   = hist2array(hTTbar,return_edges=True)
    hQCD, edges     = hist2array(hQCD,return_edges=True)
    hTotBkg, edges  = hist2array(hTotBkg,return_edges=True)
    histosBkg       = [hQCD,hTTbar]
    labelsBkg       = ["QCD",r"t$\bar{t}$"]
    colorsBkg       = ["gold","firebrick"]

    histosSig       = []
    for hSignal in hSignals:
        hTemp, edgesTemp = hist2array(hSignal,return_edges=True)
        histosSig.append(hTemp)


    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    hep.histplot(histosBkg,edges[0],stack=True,ax=axs[0],label = labelsBkg, histtype="fill",facecolor=colorsBkg,edgecolor='black')
    plt.errorbar(centresData,hData, yerr=errorsData, xerr=xerrorsData, fmt='o',color="k",label = "Data")    
    plt.fill_between(edges[0][0:-1],uncBand[0],uncBand[1],facecolor="none", hatch="xxx", edgecolor="grey", linewidth=0.0,step="post")

    for i,h in enumerate(histosSig):
        hep.histplot(h,edges[0],stack=False,ax=axs[0],label = labelsSig[i],linestyle="--",linewidth=2,zorder=2,color=colorsSig[i])


    axs[0].legend()
    plt.ylabel("Events/bin",horizontalalignment='right', y=1.0)
    axs[1].set_ylabel("Pulls")

    if(xRange):
        axs[0].set_xlim(xRange)
    if(yRange):
        axs[0].set_ylim(yRange)

    lumiText = "138$fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc='best',ncol=2)

    if(len(hSignals)>0):
        plt.text(0.65, 0.40, r"$\sigma$(pp$\rightarrow$X$\rightarrow$HY$\rightarrow b\bar{b} b\bar{b}$) = 1 fb", horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=22)

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=0.0, xmin=0, xmax=1, color="r")
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="grey",linestyle="--",alpha=0.5)
    axs[1].axhline(y=-1.0, xmin=0, xmax=1, color="grey",linestyle="--",alpha=0.5)
    axs[1].axhline(y=2.0, xmin=0, xmax=1, color="grey",linestyle="-.",alpha=0.5)
    axs[1].axhline(y=-2.0, xmin=0, xmax=1, color="grey",linestyle="-.",alpha=0.5)
    axs[1].set_ylim([-3.0,3.0])
    plt.xlabel(xlabel,horizontalalignment='right', x=1.0)
    pulls = calculatePull(hData,hTotBkg,uncBand)
    hep.histplot(pulls,edges[0],ax=axs[1],linewidth=1,histtype="fill",facecolor="blue",edgecolor='black')

    print("Saving ", outputFile)
    plt.savefig(outputFile)
    plt.savefig(outputFile.replace("png","pdf"))

    plt.clf()


def getSignals(signalsToPlot,region):
    tplDir = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/templates/WP_0.94_0.98/"
    histos = []
    for signal in signalsToPlot:
        hSignal     = 0
        for year in ["16","17","18"]:
            sigFile = tplDir+"20{0}/{1}.root".format(year,signal)
            if not (os.path.isfile(sigFile)):
                sigFile = tplDir+"2017/{0}.root".format(signal)
            sigFile = r.TFile.Open(sigFile)
            hTemp   = sigFile.Get("{0}_mJY_mJJ_{1}_nom".format(signal,region))
            if hSignal:
                hSignal.Add(hTemp)
            else:
                hSignal = hTemp.Clone("{0}_{1}".format(signal,region))
                hSignal.SetDirectory(0)
        histos.append(hSignal)
    return histos


testFile    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/RunII_SR_data_11_CR_zeroFail/postfitshapes_b.root"
#testFile    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/RunII_SR_toy_11_CR_zeroFail/postfitshapes_b.root"
TTprocesses = ["16_TTbar_bqq","17_TTbar_bqq","18_TTbar_bqq","16_TTbar_bq","17_TTbar_bq","18_TTbar_bq","16_TTbar_Other","17_TTbar_Other","18_TTbar_Other"]

ymax = {"LL":320.,"TT":45.,"NAL_L":420.,"NAL_T":200.,"NAL_AL":5000,"T_AL":300,"L_AL":1000}

#for region in ["NAL_L","NAL_T","NAL_AL"]:
for region in ["TT","LL","L_AL","T_AL"]:
    if(region=="NAL_AL"):
        taggingCat = "fail"
        dirRegion  = "NAL_T"
    elif(region=="T_AL"):
        taggingCat = "fail"
        dirRegion  = "TT"  
    elif(region=="L_AL"):
        taggingCat = "fail"
        dirRegion  = "LL"            
    else:
        taggingCat = "pass"
        dirRegion  = region

    TTshapes    = []
    for process in TTprocesses:
        TTshapes.append(get2DPostfitPlot(testFile,process,dirRegion,taggingCat))
    TTshape     = TTshapes[0].Clone("TTbar")
    TTshape.Reset()
    for TTcategory in TTshapes:
        TTshape.Add(TTcategory)
    dataShape   = get2DPostfitPlot(testFile,"data_obs",dirRegion,taggingCat)
    qcdShape    = get2DPostfitPlot(testFile,"qcd",dirRegion,taggingCat)
    totalBkg    = get2DPostfitPlot(testFile,"TotalBkg".format(region),dirRegion,taggingCat)
    print("Total bkg in {0}: {1}".format(region,totalBkg.Integral()))

    tempRoot = r.TFile.Open("postfit_bkg.root","UPDATE")
    tempRoot.cd()
    totalBkg.Write()
    tempRoot.Close()

    massPointsToPlot = ["MX1600_MY125","MX2000_MY300","MX3000_MY400"]
    labelsSignal     = ["$M_{X}$=1600 GeV\n$M_{Y}$=125 GeV","$M_{X}$=2000 GeV\n$M_{Y}$=300 GeV","$M_{X}$=3000 GeV\n$M_{Y}$=400 GeV"]


    data_proj    = dataShape.ProjectionX("data_projx")
    qcd_proj     = qcdShape.ProjectionX("qcd_projx")
    ttbar_proj   = TTshape.ProjectionX("ttbar_projx")
    totalBkg_proj= totalBkg.ProjectionX("totalbkg_projx")
    data_proj    = dataShape.ProjectionX("data_projx")
    uncBand_proj = getUncBand(totalBkg_proj)


    signalHistos     = getSignals(massPointsToPlot,dirRegion)
    rebinnedSignal   = []
    for i in range(len(massPointsToPlot)):
        rebinnedSignal.append(rebinHisto(dataShape,signalHistos[i],"{0}_{1}_rebinned".format(massPointsToPlot[i],region),scale=0.1).ProjectionX("{0}_{1}_projx".format(massPointsToPlot[i],region)))

    if("NAL" in region):
        rebinnedSignal = []
    plotShapes(data_proj,qcd_proj,ttbar_proj,totalBkg_proj,uncBand_proj,rebinnedSignal,labelsSignal,["red","blue","magenta"],"$M_{JY}$ [GeV]","{0}_MJY.png".format(region),xRange=[60.,640.],yRange=[0.,ymax[region]])


    data_proj    = dataShape.ProjectionY("data_projx")
    qcd_proj     = qcdShape.ProjectionY("qcd_projx")
    ttbar_proj   = TTshape.ProjectionY("ttbar_projx")
    totalBkg_proj= totalBkg.ProjectionY("totalbkg_projx")
    data_proj    = dataShape.ProjectionY("data_projx")
    uncBand_proj = getUncBand(totalBkg_proj)


    signalHistos     = getSignals(massPointsToPlot,dirRegion)
    rebinnedSignal   = []
    for i in range(len(massPointsToPlot)):
        rebinnedSignal.append(rebinHisto(dataShape,signalHistos[i],"{0}_{1}_rebinned".format(massPointsToPlot[i],region),scale=0.1).ProjectionY("{0}_{1}_projx".format(massPointsToPlot[i],region)))
    if("NAL" in region):
        rebinnedSignal = []
    plotShapes(data_proj,qcd_proj,ttbar_proj,totalBkg_proj,uncBand_proj,rebinnedSignal,labelsSignal,["red","blue","magenta"],"$M_{JJ}$ [GeV]","{0}_MJJ.png".format(region),xRange=[800.,4000.],yRange=[0.,ymax[region]])
