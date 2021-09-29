#!/usr/bin/env python

import os, sys
import uproot4 as rt
import numpy as np
import ROOT as r
#from tdrStyle import setTDRStyle
#setTDRStyle()
import CMS_lumi

import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib
from matplotlib import colors as mcolors
from matplotlib.ticker import AutoMinorLocator, MultipleLocator


r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0)

def checkLimitFile(file):
    if os.path.exists(file):
        f = r.TFile.Open(file)
        limitTree = f.Get("limit")
        if(limitTree.GetEntriesFast()>1):
            f.Close()
            return True
        else:
            f.Close()
            print("File with bad limit: {0}".format(file))
            return False
    else:
        print("Missing limit file: {0}".format(file))
        return False

def plot2Dlims(h2,MX,MY,outputFile):
    plt.style.use(hep.style.CMS)
    h2 = np.array(h2)

    hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')
    #hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.01,norm=mcolors.LogNorm(vmin=0.01, vmax=100.),cmap="jet")
    hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.01,norm=mcolors.LogNorm(vmin=0.01, vmax=100.))
    fig  = matplotlib.pyplot.gcf()
    fig.set_size_inches(6*2.5, 3*2.5, forward=True)
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
    plt.ylabel("$M_{Y} [GeV]$", horizontalalignment='right', y=1.0)
    plt.tight_layout()

    ax = plt.gca()
    clb=ax.collections[-1].colorbar
    #clb.ax.tick_params(labelsize=16) 
    clb.ax.set_label('Expected exclusion limits [fb]')

    fig.savefig(outputFile)

def lims2D(obs=False,outputFile="2DexpLims.png"):
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')
    MX = np.array([900,1000,1100],dtype='float64')

    limit_vals_2d = [ [0.]*np.shape(MY)[0] for _ in range(np.shape(MX)[0]) ] #limits_vals_2d[3][7] is the limit at MX point 4, MY point 8


    for i,mx in enumerate(MX):
        for j,my in enumerate(MY):
            if((mx<1200 and my>200)):
                continue
            if((mx<1300 and my>300)):
                continue
            tempFileName = "limits/obsLimits/MX{0}_MY{1}.root".format(int(mx),int(my))
            if not checkLimitFile(tempFileName):
                continue
            fTemp = r.TFile.Open(tempFileName)
            limTree = fTemp.Get("limit")
            if not limTree.GetEntry(2):
                continue
            if obs:
                limTree.GetEntry(5)
            else:
                limTree.GetEntry(2)
            limit = limTree.limit*0.5    
            limit_vals_2d[i][j] = limit

    #print(limit_vals_2d)
    plot2Dlims(limit_vals_2d,MX,MY,outputFile)



lims2D(obs=True,outputFile="test.png")
