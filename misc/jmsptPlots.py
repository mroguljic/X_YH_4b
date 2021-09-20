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


def plotShapes(hData,hTTbar,hTT_nom,hTT_jmsptUp,hTT_jmsUp,xlabel,outputFile,xRange=[],yRange=[],projectionText=""):

    print(outputFile)

    hData, edges    = hist2array(hData,return_edges=True)
    centresData     = (edges[0][:-1] + edges[0][1:])/2.#Bin centres
    errorsData      = np.sqrt(hData)
    xerrorsData     = []

    for i in range(len(edges[0])-1):
        xerror = (edges[0][i+1]-edges[0][i])/2.
        xerrorsData.append(xerror)

    hTTbar, edges   = hist2array(hTTbar,return_edges=True)
    histosBkg       = [hTTbar]
    labelsBkg       = [r"t$\bar{t}$ postfit"]
    colorsBkg       = ["firebrick"]

    hTT_nom         = hist2array(hTT_nom,return_edges=False)
    hTT_jmsUp       = hist2array(hTT_jmsUp,return_edges=False)
    hTT_jmsptUp     = hist2array(hTT_jmsptUp,return_edges=False)

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    plt.sca(ax)
    hep.histplot(histosBkg,edges[0],stack=True,ax=ax,label = labelsBkg, histtype="fill",facecolor=colorsBkg,edgecolor='black')
    plt.errorbar(centresData,hData, yerr=errorsData, xerr=xerrorsData, fmt='o',color="k",label = "Data-QCD")    
    

    hep.histplot(hTT_nom,edges[0],stack=False,ax=ax,label = r"t$\bar{t}$ prefit",linestyle="--",linewidth=2,zorder=2,color="blue")
    hep.histplot(hTT_jmsUp,edges[0],stack=False,ax=ax,label = r"t$\bar{t}$ JMS up",linestyle="--",linewidth=2,zorder=2,color="limegreen")
    hep.histplot(hTT_jmsptUp,edges[0],stack=False,ax=ax,label = r"t$\bar{t}$ JMS($p_{T}$) up",linestyle="--",linewidth=2,zorder=2,color="goldenrod")

    if(projectionText):
        plt.text(0.65, 0.40,projectionText, horizontalalignment='center',verticalalignment='center',transform=ax.transAxes, fontsize=22)


    ax.legend()
    plt.ylabel("Events/bin",horizontalalignment='right', y=1.0)
    plt.xlabel(xlabel,horizontalalignment='right', x=1.0)

    if(xRange):
        ax.set_xlim(xRange)
    if(yRange):
        ax.set_ylim(yRange)
    else:
        ax.set_ylim([0,max(hData)*2.0])

    lumiText = "138$fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    hep.cms.text("WiP",loc=1)
    plt.legend(loc='best',ncol=2)

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

def scalePrefitTT(inputFile,variation,region,year,modelHisto,histoName):
    rateParams16 = {"LL":{"bq":0.91,"bqq":0.79},"TT":{"bq":1.02,"bqq":0.79}}
    rateParams17 = {"LL":{"bq":1.29,"bqq":0.80},"TT":{"bq":1.17,"bqq":0.82}}
    rateParams18 = {"LL":{"bq":1.13,"bqq":0.90},"TT":{"bq":1.32,"bqq":0.84}}

    rateParams  = {16:rateParams16,17:rateParams17,18:rateParams18}

    histOut      = modelHisto.Clone(histoName)
    histOut.Reset()

    ttFile       = r.TFile.Open(inputFile)
    bqq          = ttFile.Get("TTbar_bqq_mJY_mJJ_{0}_{1}".format(region,variation))
    bq           = ttFile.Get("TTbar_bq_mJY_mJJ_{0}_{1}".format(region,variation))
    unm          = ttFile.Get("TTbar_unm_mJY_mJJ_{0}_{1}".format(region,variation))
    qq           = ttFile.Get("TTbar_qq_mJY_mJJ_{0}_{1}".format(region,variation))

    bqq          = rebinHisto(histOut,bqq,"TT_bqq_{0}_{1}".format(year,variation))
    bq           = rebinHisto(histOut,bq,"TT_bq_{0}_{1}".format(year,variation))
    qq           = rebinHisto(histOut,qq,"TT_qq_{0}_{1}".format(year,variation))
    unm          = rebinHisto(histOut,unm,"TT_unm_{0}_{1}".format(year,variation))

    histOut.Add(bqq,rateParams[year][region]["bqq"])
    histOut.Add(bq,rateParams[year][region]["bq"])
    histOut.Add(qq,1.0)
    histOut.Add(unm,1.0)

    return histOut


testFile    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/RunII_SR_data_11_CR_zeroFail/postfitshapes_b.root"
#testFile    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/RunII_SR_toy_11_CR_zeroFail/postfitshapes_b.root"
TTprocesses = ["16_TTbar_bqq","17_TTbar_bqq","18_TTbar_bqq","16_TTbar_bq","17_TTbar_bq","18_TTbar_bq","16_TTbar_Other","17_TTbar_Other","18_TTbar_Other"]

ymax = {"LL":320.,"TT":45.,"NAL_L":420.,"NAL_T":200.,"NAL_AL":5000,"T_AL":300,"L_AL":1000}

projections = [(1,3),(4,6),(7,10),(1,10)]
projectionTexts = ["800<$M_{JJ}$<1100 GeV","1100<$M_{JJ}$<1400 GeV","1400<$M_{JJ}$<4000 GeV","800<$M_{JJ}$<4000 GeV"]

#for region in ["NAL_L","NAL_T","NAL_AL"]:
for i,projection in enumerate(projections):
    binLow  = projection[0]
    binHigh = projection[1]

    for region in ["LL"]:
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

        # tempRoot = r.TFile.Open("postfit_bkg.root","UPDATE")
        # tempRoot.cd()
        # totalBkg.Write()
        # tempRoot.Close()

        data_proj    = dataShape.ProjectionX("data_projx",binLow,binHigh)
        qcd_proj     = qcdShape.ProjectionX("qcd_projx",binLow,binHigh)
        ttbar_proj   = TTshape.ProjectionX("ttbar_projx",binLow,binHigh)
        totalBkg_proj= totalBkg.ProjectionX("totalbkg_projx",binLow,binHigh)
        uncBand_proj = getUncBand(totalBkg_proj)


        TT_16_nom = scalePrefitTT("../results/templates_hadronic/2016/scaled/TTbar16.root","nom",region,16,TTshape,"TT_16_nom")
        TT_17_nom = scalePrefitTT("../results/templates_hadronic/2017/scaled/TTbar17.root","nom",region,17,TTshape,"TT_17_nom")
        TT_18_nom = scalePrefitTT("../results/templates_hadronic/2018/scaled/TTbar18.root","nom",region,18,TTshape,"TT_18_nom")

        TT_nom    = TT_16_nom.Clone("TT_nom")
        TT_nom.Add(TT_17_nom)
        TT_nom.Add(TT_18_nom)

        TT_16_jmsptUp = scalePrefitTT("../results/templates_hadronic/2016/scaled/TTbar16.root","jmsptUp",region,16,TTshape,"TT_16_jmsptUp")
        TT_17_jmsptUp = scalePrefitTT("../results/templates_hadronic/2017/scaled/TTbar17.root","jmsptUp",region,17,TTshape,"TT_17_jmsptUp")
        TT_18_jmsptUp = scalePrefitTT("../results/templates_hadronic/2018/scaled/TTbar18.root","jmsptUp",region,18,TTshape,"TT_18_jmsptUp")

        TT_jmsptUp    = TT_16_jmsptUp.Clone("TT_jmsptUp")
        TT_jmsptUp.Add(TT_17_jmsptUp)
        TT_jmsptUp.Add(TT_18_jmsptUp)

        TT_16_jmsUp = scalePrefitTT("../results/templates_hadronic/2016/scaled/TTbar16.root","jmsUp",region,16,TTshape,"TT_16_jmsUp")
        TT_17_jmsUp = scalePrefitTT("../results/templates_hadronic/2017/scaled/TTbar17.root","jmsUp",region,17,TTshape,"TT_17_jmsUp")
        TT_18_jmsUp = scalePrefitTT("../results/templates_hadronic/2018/scaled/TTbar18.root","jmsUp",region,18,TTshape,"TT_18_jmsUp")

        TT_jmsUp    = TT_16_jmsUp.Clone("TT_jmsUp")
        TT_jmsUp.Add(TT_17_jmsUp)
        TT_jmsUp.Add(TT_18_jmsUp)

        TT_jmsptUp  = TT_jmsptUp.ProjectionX("TT_jmsptUp_projx",binLow,binHigh)
        TT_jmsUp    = TT_jmsUp.ProjectionX("TT_jmsUp_projx",binLow,binHigh)
        TT_nom      = TT_nom.ProjectionX("TT_nom_projx",binLow,binHigh)

        data_proj.Add(qcd_proj,-1.0)
        plotShapes(data_proj,ttbar_proj,TT_nom,TT_jmsptUp,TT_jmsUp,"$M_{JY}$ [GeV]","jmsplots/jmsplot_{0}_{1}.png".format(region,i),xRange=[60.,640.],projectionText=projectionTexts[i])


