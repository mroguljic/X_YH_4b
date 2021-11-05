import matplotlib
matplotlib.use('Agg')

import ROOT as r
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
from root_numpy import hist2array
from root_numpy import tree2array
import matplotlib.patches as patches
from math import log10
from matplotlib.ticker import FuncFormatter

def transformPnet(x):
    res = -log10(1-x/1.02)
    return res
 
def revertPnet(x):
    res = 1.02*(1.-10**(-x))
    return res


def tickFunc(x,pos):
    newtickLabel = revertPnet(x)
    return "{0}".format(newtickLabel)

def pnetCornersToArguments(x1,y1,x2,y2):
    #returns arguments for patches.Rectangle in transformed axis
        corner = (transformPnet(x1),transformPnet(y1))
        width = transformPnet(x2) - transformPnet(x1)
        height  = transformPnet(y2) - transformPnet(y1)
        return corner,width,height

def makePlot(outputFile,plotTTbar=False,plotFast=False,multipleSignal=False):

    qcdStop   = [43285,150319,25219,5274]#Stop after how many selected events (scaling to include all selected QCDHT700 events)
    ttbarStop = [307,236,1559]#Stop after how many selected events (TTbar hadronic,Mtt700,Mtt1000)

    if plotFast:
        qcdStop   = [1000,1000,1000,1000]
        ttbarStop = [1000,1000,1000]



    for i,HT in enumerate([700,1000,1500,2000]):
        g = r.TFile.Open("/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2017/QCD{0}_nom.root".format(HT))
        qcdTree = g.Get("Events")
        tempH = tree2array(qcdTree,branches=['-log10(1-(pnetH/1.02))'],stop=qcdStop[i])
        tempY = tree2array(qcdTree,branches=['-log10(1-(pnetY/1.02))'],stop=qcdStop[i])
        tempH = tempH.astype(np.float)
        tempY = tempY.astype(np.float)
        if HT==700:
            qcdH = tempH
            qcdY = tempY
        else:
            qcdH = np.concatenate((qcdH,tempH))
            qcdY = np.concatenate((qcdY,tempY))

    ttCategories = ["TTbar","TTbarMtt700","TTbarMtt1000"]
    for i,ttCat in enumerate(ttCategories):
        g = r.TFile.Open("/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2017/{0}_nom.root".format(ttCat))
        ttree = g.Get("Events")
        tempH = tree2array(ttree,branches=['-log10(1-(pnetH/1.02))'],stop=ttbarStop[i])
        tempY = tree2array(ttree,branches=['-log10(1-(pnetY/1.02))'],stop=ttbarStop[i])
        tempH = tempH.astype(np.float)
        tempY = tempY.astype(np.float)
        if i==0:
            ttbarH = tempH
            ttbarY = tempY
        else:
            ttbarH = np.concatenate((ttbarH,tempH))
            ttbarY = np.concatenate((ttbarY,tempY))    

    signals     = ["MX1600_MY90"]#uncomment if only one signal
    if multipleSignal:
        signals     = ["MX1600_MY90","MX1000_MY90","MX3000_MY300"]

    sigLabels   = ["$M_{X}$=1600 GeV\n$M_{Y}$=90 GeV","$M_{X}$=1000 GeV\n$M_{Y}$=90 GeV","$M_{X}$=3000 GeV\n$M_{Y}$=300 GeV"]
    sigMarkers  = ["s","d","*"]
    sigColors   = ["darkslategray","thistle","lightsalmon"]
    sigHs       = []
    sigYs       = []

    plt.style.use([hep.style.CMS])
    matplotlib.rcParams.update({'font.size': 28})
    f, ax = plt.subplots()
    hep.cms.text("Simulation Preliminary",loc=0)

    plt.sca(ax)

    #Colored ParticleNet region rectangles
    # colSR = (152./255,251./255,152./255)
    # colNAL = (255./255,211./255,155./255)
    # colWAL = (152./255,245./255,255./255)

    # alphaPass = 0.2
    # alphaFail = 0.1

    # colSR_LL = (*colSR, alphaPass)
    # colSR_TT = (*colSR, alphaPass)
    # colSR_AL = (*colSR, alphaFail)
    # colSR_AT = (*colSR, alphaFail)

    # colNAL_L = (*colNAL, alphaPass)
    # colNAL_T = (*colNAL, alphaPass)
    # colNAL_AL = (*colNAL, alphaFail)

    # colWAL_L = (*colWAL, alphaPass)
    # colWAL_T = (*colWAL, alphaPass)
    # colWAL_AL = (*colWAL, alphaFail)


    # LL = patches.Rectangle((-log10(0.06), -log10(0.06)), 2.0+log10(0.06), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor=colSR_LL,zorder=0)
    # TT = patches.Rectangle((-log10(0.02), -log10(0.02)), 2.0+log10(0.02), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor=colSR_TT,zorder=0,label="Signal regions")
    # L_AL = patches.Rectangle((-log10(0.06), 0.0), 2.0+log10(0.06), -log10(0.06), linewidth=3, edgecolor='black', facecolor=colSR_AL,zorder=0)
    # T_AL = patches.Rectangle((-log10(0.02), 0.0), 2.0+log10(0.02), -log10(0.06), linewidth=3, linestyle='--', edgecolor='black', facecolor=colSR_AT,zorder=0)

    # NAL_T = patches.Rectangle((-log10(0.2), -log10(0.02)), -log10(0.06)+log10(0.2), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor=colNAL_T,zorder=0,label="Validation regions")
    # NAL_L = patches.Rectangle((-log10(0.2), -log10(0.06)), -log10(0.06)+log10(0.2), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor=colNAL_L,zorder=0)
    # NAL_AL = patches.Rectangle((-log10(0.2), 0.), -log10(0.06)+log10(0.2), -log10(0.06), linewidth=3, edgecolor='black', facecolor=colNAL_AL,zorder=0)

    # WAL_T = patches.Rectangle((-log10(0.4), -log10(0.02)), -log10(0.2)+log10(0.4), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor=colWAL_T,zorder=0)
    # WAL_L = patches.Rectangle((-log10(0.4), -log10(0.06)), -log10(0.2)+log10(0.4), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor=colWAL_L,zorder=0)
    # WAL_AL = patches.Rectangle((-log10(0.4), 0.), -log10(0.2)+log10(0.4), -log10(0.06), linewidth=3, edgecolor='black', facecolor=colWAL_AL,zorder=0)


    # ax.add_patch(WAL_AL)
    # ax.add_patch(WAL_L)
    # ax.add_patch(WAL_T)
    # ax.add_patch(NAL_AL)
    # ax.add_patch(NAL_L)
    # ax.add_patch(NAL_T)
    # ax.add_patch(L_AL)
    # ax.add_patch(T_AL)
    # ax.add_patch(TT)
    # ax.add_patch(LL)
    # End of Colored ParticleNet region rectangles


    # print("QCD correlation\n: ", np.corrcoef(qcdH,qcdY))
    # print("TT correlation\n: ", np.corrcoef(ttbarH,ttbarY))


    for i,signal in enumerate(signals):
        f = r.TFile.Open("/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2017/{0}_nom.root".format(signal))
        sigTree = f.Get("Events")
        sigStop = 50

        sigH = tree2array(sigTree,branches=['-log10(1-pnetH/1.02)'],stop=sigStop)#2500 events is 1pb xsec
        sigY = tree2array(sigTree,branches=['-log10(1-pnetY/1.02)'],stop=sigStop)
        sigH = sigH.astype(np.float)
        sigY = sigY.astype(np.float)
        #print("Signal correlation\n: ", np.corrcoef(sigH,sigY))

        plt.scatter(sigH,sigY,marker=sigMarkers[i],facecolors=sigColors[i],edgecolors=sigColors[i],label=sigLabels[i])

    if plotTTbar:
        plt.scatter(ttbarH,ttbarY,marker="v",facecolors="none",edgecolors="dimgrey",label=r"t$\bar{t}$") #Draw ttbar
    plt.scatter(qcdH,qcdY,marker="o",facecolors="none",edgecolors="saddlebrown",label="Multijet") #Draw QCD
    plt.xlabel("H-candidate ParticleNet score",horizontalalignment='right', x=1.0)
    plt.ylabel("Y-candidate ParticleNet score",horizontalalignment='right', y=1.0)


    pnetMax = 1.0
    ax.set_ylim([0,transformPnet(pnetMax)])
    ax.set_xlim([0,transformPnet(pnetMax)])


    #Region labels
    # plt.text(transformPnet(0.983), transformPnet(0.983), 'TT',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.96), transformPnet(0.96), 'LL',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.85), transformPnet(0.96), 'NAL_L',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.85), transformPnet(0.983), 'NAL_T',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.62), transformPnet(0.96), 'WAL_L',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.62), transformPnet(0.983), 'WAL_T',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.983), transformPnet(0.65), 'L_AL',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.96), transformPnet(0.65), 'T_AL',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.85), transformPnet(0.65), 'NAL_AL',alpha=0.7,fontsize=22)
    # plt.text(transformPnet(0.62), transformPnet(0.65), 'WAL_AL',alpha=0.7,fontsize=22)


    #Region numbering
    plt.text(transformPnet(0.985), transformPnet(0.99), 'SR1',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.95), transformPnet(0.96), 'SR2',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.87), transformPnet(0.96), 'VS2',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.87), transformPnet(0.99), 'VS1',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.66), transformPnet(0.96), 'VS4',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.66), transformPnet(0.99), 'VS3',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.985), transformPnet(0.7), 'SB1',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.95), transformPnet(0.7), 'SB2',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.87), transformPnet(0.7), 'VB1',alpha=0.7,backgroundcolor="white")
    plt.text(transformPnet(0.66), transformPnet(0.7), 'VB2',alpha=0.7,backgroundcolor="white")



    #Repeat rectangles showing ParticleNet regions to have edges on top
    #patches.Rectangle((xy),width,height), xy is the lower left corner
    LL_coords    =  pnetCornersToArguments(0.94,0.94,pnetMax,pnetMax)
    TT_coords    =  pnetCornersToArguments(0.98,0.98,pnetMax,pnetMax)
    L_AL_coords  =  pnetCornersToArguments(0.94,0.,pnetMax,0.94)
    T_AL_coords  =  pnetCornersToArguments(0.98,0.,pnetMax,0.94)

    NAL_T_coords =  pnetCornersToArguments(0.8,0.98,0.94,pnetMax)
    NAL_L_coords =  pnetCornersToArguments(0.8,0.94,0.94,0.98)
    NAL_AL_coords=  pnetCornersToArguments(0.8,0.,0.94,0.94)

    WAL_T_coords =  pnetCornersToArguments(0.6,0.98,0.8,pnetMax)
    WAL_L_coords =  pnetCornersToArguments(0.6,0.94,0.8,0.98)
    WAL_AL_coords=  pnetCornersToArguments(0.6,0.,0.8,0.94)

    LL_edge = patches.Rectangle(LL_coords[0],LL_coords[1],LL_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    TT_edge = patches.Rectangle(TT_coords[0],TT_coords[1],TT_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    L_AL_edge = patches.Rectangle(L_AL_coords[0],L_AL_coords[1],L_AL_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    T_AL_edge = patches.Rectangle(T_AL_coords[0],T_AL_coords[1],T_AL_coords[2], linewidth=3, linestyle='--', edgecolor='black', facecolor='none')

    NAL_T_edge = patches.Rectangle(NAL_T_coords[0],NAL_T_coords[1],NAL_T_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    NAL_L_edge = patches.Rectangle(NAL_L_coords[0],NAL_L_coords[1],NAL_L_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    NAL_AL_edge = patches.Rectangle(NAL_AL_coords[0],NAL_AL_coords[1],NAL_AL_coords[2], linewidth=3, edgecolor='black', facecolor='none')

    WAL_T_edge = patches.Rectangle(WAL_T_coords[0],WAL_T_coords[1],WAL_T_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    WAL_L_edge = patches.Rectangle(WAL_L_coords[0],WAL_L_coords[1],WAL_L_coords[2], linewidth=3, edgecolor='black', facecolor='none')
    WAL_AL_edge = patches.Rectangle(WAL_AL_coords[0],WAL_AL_coords[1],WAL_AL_coords[2], linewidth=3, edgecolor='black', facecolor='none')

    ax.add_patch(WAL_AL_edge)
    ax.add_patch(WAL_L_edge)
    ax.add_patch(WAL_T_edge)
    ax.add_patch(NAL_AL_edge)
    ax.add_patch(NAL_L_edge)
    ax.add_patch(NAL_T_edge)
    ax.add_patch(L_AL_edge)
    ax.add_patch(T_AL_edge)
    ax.add_patch(TT_edge)
    ax.add_patch(LL_edge)

    ncol = 2
    legY = 1.25
    legX = 0.0

    if plotTTbar:
        ncol = 3
        legX = -0.05
    if multipleSignal:
        legY = 1.4
    ax.legend(loc='upper left', bbox_to_anchor=(legX, legY),ncol=ncol, fancybox=True, shadow=True,fontsize=28)


    pnetTicks = [0.6, 0.8, 0.94, 0.98, pnetMax]
    transfTicks = []
    for pnet in pnetTicks:
        transfTicks.append(transformPnet(pnet))
    transfTicks = np.array(transfTicks)

    plt.xticks(ticks=transfTicks)
    plt.yticks(ticks=transfTicks)

    formatter = FuncFormatter(tickFunc)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.minorticks_off()


    plt.savefig("{0}.png".format(outputFile),bbox_inches="tight")
    #plt.savefig("{0}.pdf".format(outputFile),bbox_inches="tight")



plotFast = False

makePlot("scatterPlots/QCD_1sig",plotTTbar=False,plotFast=plotFast,multipleSignal=False)
#makePlot("scatterPlots/QCD_3sig",plotTTbar=False,plotFast=plotFast,multipleSignal=True)
#makePlot("scatterPlots/QCD_TT_1sig",plotTTbar=True,plotFast=plotFast,multipleSignal=False)