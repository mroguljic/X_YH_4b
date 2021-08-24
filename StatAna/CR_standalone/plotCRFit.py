import ROOT as r
r.gROOT.SetBatch(True)
import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib
from root_numpy import hist2array
import sys
matplotlib.use('Agg')


def sumTGraphs(gList):
    X=[]
    Y=[]
    yup = []
    ydown = []
    xup = []
    xdown = []
    for i in range(gList[0].GetN()):
        X.append(gList[0].GetPointX(i))
        y       = 0.
        yUpSq   = 0.
        yDownSq = 0.
        for g in gList:
            y+=g.GetPointY(i)
            yUpSq+=g.GetErrorYhigh(i)*g.GetErrorYhigh(i)
            yDownSq+=g.GetErrorYlow(i)*g.GetErrorYlow(i)
        yup.append(np.sqrt(yUpSq))
        ydown.append(np.sqrt(yDownSq))
        Y.append(y)
        xup.append(0)
        xdown.append(0)

    X = np.array(X,dtype='double')
    Y = np.array(Y,dtype='double')
    yup = np.array(yup,dtype='double')
    ydown = np.array(ydown,dtype='double')
    xup = np.array(xup,dtype='double')
    xdown = np.array(xdown,dtype='double')
    res = r.TGraphAsymmErrors(gList[0].GetN(),X, Y, 0,0, ydown ,yup)
    return res

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


def getFitRes(iFile,fitDirName,regionDirName):
    print(iFile)
    iFile = r.TFile.Open(iFile)
    fitDir  = iFile.Get(fitDirName)
    hProcs= {}
    regionDir   = fitDir.Get(regionDirName)
    gData   = regionDir.Get("data")
    gData.SetLineWidth(3)
    hTotal  = regionDir.Get("total")
    fitKeys = regionDir.GetListOfKeys()
    for fitKey in fitKeys:
        procName = fitKey.GetName()
        if("total" in procName or "data" in procName):
            continue
        else:
            hProcs[procName] = regionDir.Get(procName)
    for hName in hProcs:
        hProcs[hName].SetDirectory(0)
    res = [gData,hProcs]

    return res


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

def calculatePull(gData,totalHistos):
    pulls = []
    for i in range(gData.GetN()):
        dataYield = gData.GetPointY(i)
        mcYield   = totalHistos.GetBinContent(i+1)#bin counting starts from 1 in TH1, 0 is underflow
        diff      = dataYield-mcYield
        if(dataYield>=mcYield):
            dataErr = gData.GetErrorYlow(i)
            mcErr   = totalHistos.GetBinError(i+1)
        else:
            dataErr = gData.GetErrorYhigh(i)
            mcErr   = totalHistos.GetBinError(i+1)
        sigma = np.sqrt(mcErr*mcErr+dataErr*dataErr)
        if(dataYield==0):
            pulls.append(0.0)
        else:
            pulls.append(diff/sigma)
    return np.array(pulls)


    sigma = 0.0
    FScont = 0.0
    BKGcont = 0.0
    for ibin in range(1,pull.GetNbinsX()+1):
        FScont = DATA.GetBinContent(ibin)
        BKGcont = BKG.GetBinContent(ibin)
        if FScont>=BKGcont:
            FSerr = DATA.GetBinErrorLow(ibin)
            BKGerr = abs(BKGUP.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FScont<BKGcont:
            FSerr = DATA.GetBinErrorUp(ibin)
            BKGerr = abs(BKGDOWN.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FSerr != None:
            sigma = sqrt(FSerr*FSerr + BKGerr*BKGerr)
        else:
            sigma = sqrt(BKGerr*BKGerr)
        if FScont == 0.0:
            pull.SetBinContent(ibin, 0.0 )  
        else:
            if sigma != 0 :
                pullcont = (pull.GetBinContent(ibin))/sigma
                pull.SetBinContent(ibin, pullcont)
            else :
                pull.SetBinContent(ibin, 0.0 )

def plotFitRes(gData,hProcs,output,scale=10.,offset=0.,colors=["limegreen","turquoise","firebrick"],xTitle="$M_{SD}$ [GeV]",yTitle="Jets/10 GeV",yRange="",xRange="",text=""):
    histos  = []
    labels  = []
    edges   = []
    totalHistos = False



    sortedProcs = sorted(hProcs.items(), key=lambda x: x[1].GetName())
    for proc in sortedProcs:
        if(proc[0]=="sig"):
            continue
        procName = proc[0]
        h        = proc[1]
        if not totalHistos:
            totalHistos = h.Clone("totalHistos")
        else:
            totalHistos.Add(h)
        print(procName)
        hist, edges = hist2array(h,return_edges=True)
        histos.append(hist)
        edges.append(edges[0])
        labels.append(procName)

    for i in range(len(edges[0])):
        edges[0][i]=edges[0][i]*scale + offset

    dataY = []
    dataX = []
    dataYErrlo = []
    dataYErrup = []
    for i in range(gData.GetN()):
        dataY.append(gData.GetPointY(i))
        dataX.append(gData.GetPointX(i)*scale+offset)
        dataYErrlo.append(gData.GetErrorYlow(i))
        dataYErrup.append(gData.GetErrorYhigh(i))

    pulls           = calculatePull(gData,totalHistos)

    for i in range(len(labels)):
        labels[i]=labels[i].replace("TTbar",r"t$\bar{t}$")
        labels[i]=labels[i].replace("_"," ")

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])

    hep.histplot(histos,edges[0],stack=True,ax=axs[0],label=labels,linewidth=1,histtype="fill",facecolor=colors,edgecolor='black')
    plt.errorbar(dataX, dataY, yerr=[dataYErrlo,dataYErrup], fmt='o',color="black",label="Data")

    uncLo, uncUp    = getUncBand(totalHistos)


    #------------------------------------#
    #Fix to extend error bar over whole first and last bin!
    for i in range(len(dataX)):
        dataX[i] = dataX[i] - 0.5*scale
    dataX.append(dataX[-1]+scale)
    uncLo= np.append(uncLo,[0])
    uncUp= np.append(uncUp,[0])
    #------------------------------------#
    
    plt.fill_between(dataX,uncLo,uncUp,facecolor="none", hatch="xxx", edgecolor="grey", linewidth=0.0,step="post")
    # if(log):
    #     axs[0].set_yscale("log")
    axs[0].legend()
    axs[0].set_ylabel(yTitle)
    axs[1].set_xlabel(xTitle)
    axs[1].set_ylabel("Pull")
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)


    if("16" in output):
        luminosity = "36.3 $fb^{-1}\ "
    elif("17" in output):
        luminosity = "41.5 $fb^{-1}\ "
    elif("18" in output):
        luminosity = "59.8 $fb^{-1}\ "
    else:
        luminosity = "138 $fb^{-1}\ "

    lumiText = luminosity + "(13 TeV)$"
    hep.cms.lumitext(text=lumiText, ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("Simulaton WiP",loc=1)
    if(text):
        plt.text(0.1, 0.85,text, horizontalalignment='left',verticalalignment='center',transform=axs[0].transAxes, fontsize=24)

    plt.legend(loc='upper right',ncol=1,fontsize=24)#loc = 'best'

    plt.sca(axs[1])#switch to lower pad
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    axs[1].axhline(y=0.0, xmin=0, xmax=1, color="r")
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="grey",linestyle="--",alpha=0.5)
    axs[1].axhline(y=-1.0, xmin=0, xmax=1, color="grey",linestyle="--",alpha=0.5)
    axs[1].axhline(y=2.0, xmin=0, xmax=1, color="grey",linestyle="-.",alpha=0.5)
    axs[1].axhline(y=-2.0, xmin=0, xmax=1, color="grey",linestyle="-.",alpha=0.5)
    axs[1].set_ylim([-3.0,3.0])
    hep.histplot(pulls,edges[0],ax=axs[1],linewidth=1,histtype="fill",facecolor="blue",edgecolor='black')



    plt.savefig(output)
    plt.savefig(output.replace(".png",".pdf"))
    plt.clf()

years   =["16","17","18"]
regions =["L","T"]
yRanges = {"L":350,"T":170}
# for year in years:
#     for region in regions:
#         yMax = yRanges[region]
#         gDataPost, hProcsPost = getFitRes("fitDiagnostics_{0}_{1}.root".format(region,year),"shapes_fit_b","{0}_CR".format(region))
#         plotFitRes(gDataPost,hProcsPost,"postfitPlots/{0}_CR_{1}.png".format(region,year),yRange=[0,yMax],text="20{0} CR {1} postfit".format(year,region),scale=10.,offset=60.)

#         plotFitRes(gDataPre,hProcsPre,"postfitPlots/{0}_CR_{1}_prefit.png".format(region,year),yRange=[0,yMax],text="20{0} CR {1} prefit".format(year,region),scale=10.,offset=60.)

for region in regions:
    for year in years:
        yMax = yRanges[region]
        fitDir = sys.argv[1]
        gDataPost, hProcsPost = getFitRes(fitDir+"/fitDiagnostics.root".format(region,year),"shapes_fit_b","CR_{0}_{1}".format(region,year))
        plotFitRes(gDataPost,hProcsPost,"CR_{0}_{1}.png".format(region,year),yRange=[0,yMax],text="20{0} CR {1} postfit".format(year,region),scale=10.,offset=60.)


        gDataPre, hProcsPre = getFitRes(fitDir+"/fitDiagnostics.root".format(region,year),"shapes_prefit","CR_{0}_{1}".format(region,year))
        plotFitRes(gDataPre,hProcsPre,"{0}_CR_{1}_prefit.png".format(region,year),yRange=[0,yMax],text="20{0} CR {1} prefit".format(year,region),scale=10.,offset=60.)



# for region in regions:
#     for year in years:
#         yMax = yRanges[region]
#         fitDir = sys.argv[1]
#         gDataPost, hProcsPost = getFitRes("fitDiagnostics.root".format(region,year),"shapes_fit_b","CR_{0}_{1}".format(region,year))
#         plotFitRes(gDataPost,hProcsPost,"CR_{0}_{1}.png".format(region,year),yRange=[0,yMax],text="20{0} CR {1} postfit".format(year,region),scale=10.,offset=60.)
