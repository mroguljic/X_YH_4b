import ROOT as r
import numpy as np
from root_numpy import hist2array

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.figure import figaspect
import mplhep as hep
from itertools import cycle
import os

r.gROOT.SetBatch(True)

def rebinHisto(h2,name):
    binsMJJ = np.array([800,900,1000,1100,1200,1300,1400,1600,2000,3000,4000],dtype="float64")
    binsMJY = np.array([60,80,100,120,140,160,180,200,220,240,260,280,320,360,400,480,640],dtype="float64")

    h2_rebinned = r.TH2F(name,"",len(binsMJY)-1,binsMJY,len(binsMJJ)-1,binsMJJ)

    xaxis = h2.GetXaxis()
    yaxis = h2.GetYaxis()
    xaxis_re = h2_rebinned.GetXaxis()
    yaxis_re = h2_rebinned.GetYaxis()

    for i in range(1,h2.GetNbinsX()+1):
        for j in range(1,h2.GetNbinsY()+1):
            x = xaxis.GetBinCenter(i)
            y = yaxis.GetBinCenter(j)
            i_re = xaxis_re.FindBin(x)
            j_re = yaxis_re.FindBin(y)
            value = h2.GetBinContent(i,j)
            if(value<0.):
                value = 0.
            err = h2.GetBinError(i,j)
            err_re = np.sqrt(h2_rebinned.GetBinError(i_re,j_re)*h2_rebinned.GetBinError(i_re,j_re)+err*err)
            h2_rebinned.Fill(x,y,value)
            h2_rebinned.SetBinError(i_re,j_re,err_re)
    h2_rebinned.SetDirectory(0)

    return h2_rebinned

def plotHistos(histos,edges,output,labels,x_range,y_range,x_title,legend_title):
    # linesstyles = [(0,()),#Full line
    # (0, (1, 6)),(0, (1,3)),(0, (1,1)),#Dotted
    # (0, (2, 6)),(0, (2,3)),(0, (2,1)),#2-dash
    # (0, (3,6)),(0, (3,3)),(0, (3,1)),#3-dashed
    # (0, (3,1,1,1)),(0, (3,3,1,3)),(0, (3,6,1,6)),#Dash-dot
    # (0, (3,1,3,1,1,1)),(0,(3,3,3,3,1,3)),(0, (3,6,3,6,1,6)),#Dash-dash-dot
    # (0, (1,1,1,1,3,1)),(0, (1,3,1,3,3,3)),(0, (1,6,1,6,3,6)),#dot-dot-dash
    # ]
    linestyles = ["-","--","-.",":"]
    linecycler = cycle(linestyles)


    colormap = plt.cm.tab20 #colormaps https://matplotlib.org/stable/gallery/color/colormap_reference.html
    colors = [colormap(i) for i in np.linspace(0, 1,len(histos))]

    plt.style.use([hep.style.CMS])
    if("MX" in output):
        w, h = figaspect(1/1.20)
        f, ax = plt.subplots(figsize=(w,h))
    else:
        f, ax = plt.subplots()
    ax.set_prop_cycle('color', colors)
    for i,h in enumerate(histos):
        hep.histplot(h,edges[i],stack=False,ax=ax,label = labels[i],linewidth=3,linestyle=next(linecycler))

    ax.legend()
    plt.xlabel(x_title, horizontalalignment='right', x=1.0)
    plt.ylabel("Event fraction / bin",horizontalalignment='right', y=1.0)

    ax.set_ylim(y_range)
    ax.set_xlim(x_range)
    hep.cms.text("Simulation Preliminary",loc=0)
    if("MX" in output):
        plt.legend(loc=2,ncol=3,title=legend_title)
    else:
        plt.legend(loc='best',ncol=2,title=legend_title)

    print("Saving {0}".format(output))
    plt.savefig(output)
    plt.savefig(output.replace("png","pdf"))
    plt.clf()

tplDir = "../CMSSW_10_6_14/src/2DAlphabet/templates/WP_0.94_0.98/2016/"

MX = [900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
MY = [60,70,80,90,100,125,150,200,250,300,350,400,450,500,600]

#Fixed MX
for mx in [1200,1400,2000,2400]:
    histos = []
    edges  = []
    labels = []
    x_range = [60.,640.]
    y_range = [0.,1.5]
    for my in MY:
        massPoint = "MX{0}_MY{1}".format(mx,my)
        if not os.path.exists(tplDir+massPoint+".root"):
            continue
        f = r.TFile.Open(tplDir+massPoint+".root")
        h_TT = f.Get("{0}_mJY_mJJ_TT_nom".format(massPoint))
        h_TT_re = rebinHisto(h_TT,h_TT.GetName()+"_rebinned")
        h_TT_re.Scale(1./h_TT_re.Integral())

        h_proj = h_TT_re.ProjectionX()

        hist, h_edges = hist2array(h_proj,return_edges=True)
        histos.append(hist)
        edges.append(h_edges[0])
        labels.append("$M_{Y}$="+"{0} GeV".format(my))
        f.Close()

    plotHistos(histos,edges,"massResolutionPlots/MY_projections_MX_{0}.png".format(mx),labels,x_range,y_range,"$M_{JY}$ [GeV]","$M_{X}$="+"{0} GeV".format(mx))


#Fixed MY
for my in [100,450,500]:
    histos = []
    edges  = []
    labels = []
    x_range = [800.,4000.]
    y_range = [0.,2.0]
    for mx in MX:
        massPoint = "MX{0}_MY{1}".format(mx,my)
        if not os.path.exists(tplDir+massPoint+".root"):
            continue    
        f = r.TFile.Open(tplDir+massPoint+".root")
        h_TT = f.Get("{0}_mJY_mJJ_TT_nom".format(massPoint))
        h_TT_re = rebinHisto(h_TT,h_TT.GetName()+"_rebinned")
        h_TT_re.Scale(1./h_TT_re.Integral())

        h_proj = h_TT_re.ProjectionY()

        hist, h_edges = hist2array(h_proj,return_edges=True)
        histos.append(hist)
        edges.append(h_edges[0])
        mx_label = mx/1000.
        labels.append("$M_{X}$="+"{0} TeV".format(mx_label))
        f.Close()

    plotHistos(histos,edges,"massResolutionPlots/MX_projections_MY_{0}.png".format(my),labels,x_range,y_range,"$M_{JJ}$ [GeV]","$M_{Y}$="+"{0} GeV".format(my))
