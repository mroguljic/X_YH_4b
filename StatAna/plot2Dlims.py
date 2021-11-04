#!/usr/bin/env python

import os, sys
import uproot4 as rt
import numpy as np
import ROOT as r

import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib
from matplotlib import colors as mcolors
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import matplotlib.patches as patches

import interpolateLimits as interp

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

def limsToHisto(output,obs=False):
    signalNorm = 1.0 #fb
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')

    granulatedMX = np.arange(850,4150,100,dtype='float64')
    granulatedMY = np.arange(55,615,10,dtype='float64')

    if not obs:
        hName = "exp_limits"
    else:
        hName = "obs_limits"
    h2D = r.TH2D(hName,"",len(granulatedMX)-1,granulatedMX,len(granulatedMY)-1,granulatedMY)

    for mx in MX:
        for my in MY:
            if not (mx>(6*min(my, 125) + max(my, 125))):
                continue
            tempFileName = "limits/obsLimits_1fb_signal_new_skims/MX{0}_MY{1}.root".format(int(mx),int(my))
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
            limit = limTree.limit*signalNorm  
            binx = h2D.GetXaxis().FindBin(mx)
            biny = h2D.GetYaxis().FindBin(my)
            h2D.SetBinContent(binx,biny,limit)
            fTemp.Close()

    f = r.TFile.Open(output,"UPDATE")
    f.cd()
    h2D.Write()
    f.Close()

def readXsecs(xsecFile,scale=1.):
    f = open(xsecFile)
    xsecs = {}
    for line in f:
        if("MX" in line):#Title line
            continue
        content = line.split(",")
        xsecs[(int(float(content[0])),int(float(content[1])))] = float(content[2].replace("\n",""))*scale

    return xsecs


def xsecsToHisto(output):
    xsecNorm = 1.0 #in fb
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')
    granulatedMX = np.arange(850,4150,100,dtype='float64')
    granulatedMY = np.arange(55,615,10,dtype='float64')

    h2D   = r.TH2D("NMSSM_orig","",len(granulatedMX)-1,granulatedMX,len(granulatedMY)-1,granulatedMY)
    xsecs = readXsecs("NMSSM_xsecs_ORIG.csv",scale=xsecNorm)
    for mx in MX:
        for my in MY:
            if not (mx>(6*min(my, 125) + max(my, 125))):
                continue
            binx = h2D.GetXaxis().FindBin(mx)
            biny = h2D.GetYaxis().FindBin(my)
            if((int(mx),int(my)) in xsecs):
                h2D.SetBinContent(binx,biny,xsecs[(int(mx),int(my))])

    f = r.TFile.Open(output,"UPDATE")
    f.cd()
    h2D.Write()
    f.Close()


def h2ToArray(h2): 
    MX = np.array(h2.GetXaxis().GetXbins())
    MY = np.array(h2.GetYaxis().GetXbins())
    limit_vals_2d = [ [0.]*np.shape(MY)[0] for _ in range(np.shape(MX)[0]) ] #limits_vals_2d[3][7] is the limit at MX point 4, MY point 8

    for i in range(0,len(MX)):
        for j in range(0,len(MY)):
            mx = MX[i]
            my = MY[j]
            limit = h2.GetBinContent(i+1,j+1)#ROOT counting starts from 1
            limit_vals_2d[i][j] = limit

    return limit_vals_2d,MX,MY


def plot2Dlims(h2,MX,MY,outputFile,obs=False, excluded=True):
    plt.style.use(hep.style.CMS)
    h2 = np.array(h2)
    hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')
    hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.01,norm=mcolors.LogNorm(vmin=0.01, vmax=100.))
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
    plt.ylabel("$M_{Y} [GeV]$", horizontalalignment='right', y=1.0)

    ax = plt.gca()
    clb=ax.collections[-1].colorbar

    if(obs):
        clb.set_label('Observed exclusion limits [fb]')
    else:
        clb.set_label('Expected exclusion limits [fb]')

    if(obs and excluded):
        excluded_obs_points = [(1050,95),(1150,95),(1150,155),(1050,155),(1050,135),(950,135),(950,125),(1050,125)]
        obs_excluded_patch = patches.Polygon(excluded_obs_points,closed=True,hatch='//',edgecolor="red",facecolor="none")
        ax.add_patch(obs_excluded_patch)

        extra_obs_points = [(850,65),(950,65),(950,75),(850,75)]
        extra_obs_patch = patches.Polygon(extra_obs_points,closed=True,hatch='//',edgecolor="red",facecolor="none")
        ax.add_patch(extra_obs_patch)
    if(obs==False and excluded):
        excluded_exp_points = [(850,65),(950,65),(950,135),(850,135)]
        exp_excluded_patch = patches.Polygon(excluded_exp_points,closed=True,hatch='//',edgecolor="red",facecolor="none")
        ax.add_patch(exp_excluded_patch)

        extra_exp_points = [(1050,125),(1150,125),(1150,135),(1050,135)]
        extra_exp_patch = patches.Polygon(extra_exp_points,closed=True,hatch='//',edgecolor="red",facecolor="none")
        ax.add_patch(extra_exp_patch)

    fig  = matplotlib.pyplot.gcf()
    #plt.tight_layout()
    fig.set_size_inches(4.5*2.5, 3*2.5, forward=True)

    fig.savefig(outputFile)
    plt.close('all')


def printExcludedMasses(h2_limits,h2_xsecs):
    NX = h2_limits.GetNbinsX()
    NY = h2_limits.GetNbinsY()

    for i in range(1,NX+1):
        for j in range(1,NY+1):
            limit = h2_limits.GetBinContent(i,j)
            xsec  = h2_xsecs.GetBinContent(i,j)
            if(limit<xsec):
                mx = h2_limits.GetXaxis().GetBinCenter(i)
                my = h2_limits.GetYaxis().GetBinCenter(j)
                print("Excluded: {0},{1}".format(mx,my))
                print("Limit: {0}".format(limit))
                print("Xsec: {0}".format(xsec))
                print("-----")


if __name__ == '__main__':
    #Orig limits and xsecs
    limsToHisto("limits_granulated.root")
    limsToHisto("limits_granulated.root",obs=True)
    xsecsToHisto("limits_granulated.root")
    #Smoothing
    f = r.TFile.Open("limits_granulated.root")

    xsecs = f.Get("NMSSM_orig")
    xsecs_first_pass  = interp.interpolateHisto(xsecs,direction="horizontal",hName="NMSSM_horizontal")
    xsecs_smooth      = interp.interpolateHisto(xsecs_first_pass,direction="vert",hName="NMSSM_horizontal_vertical")

    h2_exp = f.Get("exp_limits")
    h2_exp_first_pass     = interp.interpolateHisto(h2_exp,direction="horizontal",hName="exp_horizontal")
    h2_exp_smooth         = interp.interpolateHisto(h2_exp_first_pass,direction="vert",hName="exp_horizontal_vertical")

    h2_obs = f.Get("obs_limits")
    h2_obs_first_pass     = interp.interpolateHisto(h2_obs,direction="horizontal",hName="obs_horizontal")
    h2_obs_smooth         = interp.interpolateHisto(h2_obs_first_pass,direction="vert",hName="obs_horizontal_vertical")

    g = r.TFile.Open("smooth_limits.root","RECREATE")
    g.cd()
    xsecs.Write()
    xsecs_first_pass.Write()
    xsecs_smooth.Write()
    h2_exp.Write()
    h2_exp_first_pass.Write()
    h2_exp_smooth.Write()
    h2_obs.Write()
    h2_obs_first_pass.Write()
    h2_obs_smooth.Write()
    g.Close()



    #Plotting
    f = r.TFile.Open("smooth_limits.root")
    h2 = f.Get("exp_limits")
    h2_xsecs = f.Get("NMSSM_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2)
    # plot2Dlims(limit_vals_2d,MX,MY,"exp_orig.png",obs=False)

    # h2_first_pass  = f.Get("exp_horizontal")
    # limit_vals_2d,MX,MY=h2ToArray(h2_first_pass)
    # plot2Dlims(limit_vals_2d,MX,MY,"exp_horizontal.png",obs=False)

    h2_smooth = f.Get("exp_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    plot2Dlims(limit_vals_2d,MX,MY,"exp_horizontal_vertical.png",obs=False)
    printExcludedMasses(h2_smooth,h2_xsecs)

    h2 = f.Get("obs_limits")
    # limit_vals_2d,MX,MY=h2ToArray(h2)
    # plot2Dlims(limit_vals_2d,MX,MY,"obs_orig.png",obs=True)

    # h2_first_pass  = f.Get("obs_horizontal")
    # limit_vals_2d,MX,MY=h2ToArray(h2_first_pass)
    # plot2Dlims(limit_vals_2d,MX,MY,"obs_horizontal.png",obs=True)

    h2_smooth = f.Get("obs_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    plot2Dlims(limit_vals_2d,MX,MY,"obs_horizontal_vertical.png",obs=True)
    printExcludedMasses(h2_smooth,h2_xsecs)