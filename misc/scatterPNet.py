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
    res = -log10(1-x)
    return res
 
def revertPnet(x):
    res = 1.-10**(-x) 
    return res


def tickFunc(x,pos):
    newtickLabel = revertPnet(x)
    return "{0}".format(newtickLabel)


def makePlot(outputFile,plotTTbar=False,plotFast=False,multipleSignal=False):

    qcdStop   = [43285,150319,25219,5274]#Stop after how many selected events (scaling to include all selected QCDHT700 events)
    ttbarStop = [307,236,1559]#Stop after how many selected events (TTbar hadronic,Mtt700,Mtt1000)

    if plotFast:
        qcdStop   = [1000,1000,1000,1000]
        ttbarStop = [1000,1000,1000]



    for i,HT in enumerate([700,1000,1500,2000]):
        g = r.TFile.Open("/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2017/QCD{0}_nom.root".format(HT))
        qcdTree = g.Get("Events")
        tempH = tree2array(qcdTree,selection="pnetH<0.999 && pnetY<0.999",branches=['-log10(1-(pnetH))'],stop=qcdStop[i])
        tempY = tree2array(qcdTree,selection="pnetH<0.999 && pnetY<0.999",branches=['-log10(1-(pnetY))'],stop=qcdStop[i])
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
        tempH = tree2array(ttree,selection="pnetH<0.999 && pnetY<0.999",branches=['-log10(1-(pnetH))'],stop=ttbarStop[i])
        tempY = tree2array(ttree,selection="pnetH<0.999 && pnetY<0.999",branches=['-log10(1-(pnetY))'],stop=ttbarStop[i])
        tempH = tempH.astype(np.float)
        tempY = tempY.astype(np.float)
        if i==0:
            ttbarH = tempH
            ttbarY = tempY
        else:
            ttbarH = np.concatenate((ttbarH,tempH))
            ttbarY = np.concatenate((ttbarY,tempY))    

    signals     = ["MX1600_MY125"]#uncomment if only one signal
    if multipleSignal:
        signals     = ["MX1600_MY125","MX1000_MY90","MX3000_MY300"]

    sigLabels   = ["$M_{X}$=1600 GeV\n$M_{Y}$=125 GeV","$M_{X}$=1000 GeV\n$M_{Y}$=90 GeV","$M_{X}$=3000 GeV\n$M_{Y}$=300 GeV"]
    sigMarkers  = ["s","d","*"]
    sigColors   = ["cadetblue","thistle","lightsalmon"]
    sigHs       = []
    sigYs       = []



    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()
    hep.cms.text("Simulation Preliminary",loc=0)

    plt.sca(ax)



    #Rectangles showing ParticleNet regions
    #coordinates are in transformed variable, TODO: rewrite to real ParticleNet score variables
    LL = patches.Rectangle((-log10(0.06), -log10(0.06)), 2.0+log10(0.06), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor='lightgreen',zorder=0)
    TT = patches.Rectangle((-log10(0.02), -log10(0.02)), 2.0+log10(0.02), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor='lightgreen',zorder=0)
    L_AL = patches.Rectangle((-log10(0.06), 0.0), 2.0+log10(0.06), -log10(0.06), linewidth=3, edgecolor='black', facecolor='palegreen',zorder=0)
    T_AL = patches.Rectangle((-log10(0.02), 0.0), 2.0+log10(0.02), -log10(0.06), linewidth=3, linestyle='--', edgecolor='black', facecolor='palegreen',zorder=0)

    NAL_T = patches.Rectangle((-log10(0.2), -log10(0.02)), -log10(0.06)+log10(0.2), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor='bisque',zorder=0)
    NAL_L = patches.Rectangle((-log10(0.2), -log10(0.06)), -log10(0.06)+log10(0.2), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor='bisque',zorder=0)
    NAL_AL = patches.Rectangle((-log10(0.2), 0.), -log10(0.06)+log10(0.2), -log10(0.06), linewidth=3, edgecolor='black', facecolor='antiquewhite',zorder=0)

    WAL_T = patches.Rectangle((-log10(0.4), -log10(0.02)), -log10(0.2)+log10(0.4), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor='paleturquoise',zorder=0)
    WAL_L = patches.Rectangle((-log10(0.4), -log10(0.06)), -log10(0.2)+log10(0.4), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor='paleturquoise',zorder=0)
    WAL_AL = patches.Rectangle((-log10(0.4), 0.), -log10(0.2)+log10(0.4), -log10(0.06), linewidth=3, edgecolor='black', facecolor='lightcyan',zorder=0)


    ax.add_patch(WAL_AL)
    ax.add_patch(WAL_L)
    ax.add_patch(WAL_T)
    ax.add_patch(NAL_AL)
    ax.add_patch(NAL_L)
    ax.add_patch(NAL_T)
    ax.add_patch(L_AL)
    ax.add_patch(T_AL)
    ax.add_patch(TT)
    ax.add_patch(LL)



    for i,signal in enumerate(signals):
        f = r.TFile.Open("/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2017/{0}_nom.root".format(signal))
        sigTree = f.Get("Events")

        sigH = tree2array(sigTree,selection="pnetH<0.999 && pnetY<0.999",branches=['-log10(1-pnetH)'],stop=500)#2500 events is 1pb xsec
        sigY = tree2array(sigTree,selection="pnetH<0.999 && pnetY<0.999",branches=['-log10(1-pnetY)'],stop=500)
        sigH = sigH.astype(np.float)
        sigY = sigY.astype(np.float)

        plt.scatter(sigH,sigY,marker=sigMarkers[i],facecolors=sigColors[i],edgecolors=sigColors[i],label=sigLabels[i])

    if plotTTbar:
        plt.scatter(ttbarH,ttbarY,marker="v",facecolors="none",edgecolors="dimgrey",label=r"t$\bar{t}$") #Draw ttbar
    plt.scatter(qcdH,qcdY,marker="o",facecolors="none",edgecolors="tan",label="QCD") #Draw QCD
    plt.xlabel("H-candidate ParticleNet score",horizontalalignment='right', x=1.0)
    plt.ylabel("Y-candidate ParticleNet score",horizontalalignment='right', y=1.0)

    ax.set_ylim([0,2.0])
    ax.set_xlim([0,2.0])



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
    # plt.text(transformPnet(0.984), transformPnet(0.984), '1)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.96), transformPnet(0.96), '2)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.87), transformPnet(0.96), '6)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.87), transformPnet(0.983), '5)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.68), transformPnet(0.96), '9)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.68), transformPnet(0.983), '8)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.984), transformPnet(0.7), '3)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.96), transformPnet(0.7), '4)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.87), transformPnet(0.7), '7)',alpha=0.7,fontsize=26)
    # plt.text(transformPnet(0.66), transformPnet(0.7), '10)',alpha=0.7,fontsize=26)



    #Repeat rectangles showing ParticleNet regions to have edges on top
    LL_edge = patches.Rectangle((-log10(0.06), -log10(0.06)), 2.0+log10(0.06), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor='none')
    TT_edge = patches.Rectangle((-log10(0.02), -log10(0.02)), 2.0+log10(0.02), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor='none')
    L_AL_edge = patches.Rectangle((-log10(0.06), 0.0), 2.0+log10(0.06), -log10(0.06), linewidth=3, edgecolor='black', facecolor='none')
    T_AL_edge = patches.Rectangle((-log10(0.02), 0.0), 2.0+log10(0.02), -log10(0.06), linewidth=3, linestyle='--', edgecolor='black', facecolor='none')

    NAL_T_edge = patches.Rectangle((-log10(0.2), -log10(0.02)), -log10(0.06)+log10(0.2), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor='none')
    NAL_L_edge = patches.Rectangle((-log10(0.2), -log10(0.06)), -log10(0.06)+log10(0.2), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor='none')
    NAL_AL_edge = patches.Rectangle((-log10(0.2), 0.), -log10(0.06)+log10(0.2), -log10(0.06), linewidth=3, edgecolor='black', facecolor='none')

    WAL_T_edge = patches.Rectangle((-log10(0.4), -log10(0.02)), -log10(0.2)+log10(0.4), 2.0+log10(0.02), linewidth=3, edgecolor='black', facecolor='none')
    WAL_L_edge = patches.Rectangle((-log10(0.4), -log10(0.06)), -log10(0.2)+log10(0.4), 2.0+log10(0.06), linewidth=3, edgecolor='black', facecolor='none')
    WAL_AL_edge = patches.Rectangle((-log10(0.4), 0.), -log10(0.2)+log10(0.4), -log10(0.06), linewidth=3, edgecolor='black', facecolor='none')

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
    legY = 1.2

    if plotTTbar:
        ncol = 3
    if multipleSignal:
        legY = 1.3
    ax.legend(loc='upper left', bbox_to_anchor=(0.05, legY),ncol=ncol, fancybox=True, shadow=True)


    pnetTicks = [0.6, 0.8, 0.94, 0.98]
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
    plt.savefig("{0}.pdf".format(outputFile),bbox_inches="tight")



plotFast = False

makePlot("scatterPlots/QCD_1sig",plotTTbar=False,plotFast=plotFast,multipleSignal=False)
makePlot("scatterPlots/QCD_3sig",plotTTbar=False,plotFast=plotFast,multipleSignal=True)
makePlot("scatterPlots/QCD_TT_1sig",plotTTbar=True,plotFast=plotFast,multipleSignal=False)
