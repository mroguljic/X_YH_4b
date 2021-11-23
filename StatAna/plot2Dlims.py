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
from scipy.spatial import ConvexHull

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

    granulatedMX = np.arange(900,4020,10,dtype='float64')
    granulatedMY = np.arange(60,602,1,dtype='float64')

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

def pvalHistToSig(h2_pval):
    NX = h2_pval.GetNbinsX()
    NY = h2_pval.GetNbinsY()
    hName = h2_pval.GetName().replace("pval","z")
    h2_z = h2_pval.Clone(hName)
    h2_z.Reset()
    for i in range(1,NX+1):
        for j in range(1,NY+1):
            sig = h2_pval.GetBinContent(i,j)
            if(sig==0):
                continue
            zscore  = r.RooStats.PValueToSignificance(sig)
            if(zscore<0.001):
                zscore = 0.001
            h2_z.SetBinContent(i,j,zscore)

    h2_z.SetDirectory(0)
    return h2_z

def sigToHisto(output):
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')

    granulatedMX = np.arange(900,4020,10,dtype='float64')
    granulatedMY = np.arange(60,602,1,dtype='float64')

    hName = "obs_sig"
    h2D   = r.TH2D(hName+"_pval","",len(granulatedMX)-1,granulatedMX,len(granulatedMY)-1,granulatedMY)

    for mx in MX:
        for my in MY:
            if not (mx>(6*min(my, 125) + max(my, 125))):
                continue
            tempFileName = "limits/significances_1fb_signal_new_skims/MX{0}_MY{1}.root".format(int(mx),int(my))
            if not os.path.exists(tempFileName):
                continue
            fTemp = r.TFile.Open(tempFileName)
            limTree = fTemp.Get("limit")
            limTree.GetEntry(0)
            sig  = limTree.limit
            binx = h2D.GetXaxis().FindBin(mx)
            biny = h2D.GetYaxis().FindBin(my)
            h2D.SetBinContent(binx,biny,sig)
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


def xsecsToHisto(output,NMSSM=True):
    xsecNorm = 1.0 #in fb
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')
    granulatedMX = np.arange(900,4020,10,dtype='float64')
    granulatedMY = np.arange(60,602,1,dtype='float64')

    if(NMSSM):
        h2D   = r.TH2D("NMSSM_orig","",len(granulatedMX)-1,granulatedMX,len(granulatedMY)-1,granulatedMY)
        xsecs = readXsecs("NMSSM_xsecs_ORIG.csv",scale=xsecNorm)
    else:
        h2D   = r.TH2D("TRSSE_orig","",len(granulatedMX)-1,granulatedMX,len(granulatedMY)-1,granulatedMY)
        xsecs = readXsecs("Tania_XSECS.csv",scale=xsecNorm)

    for massPoint,xsec in xsecs.items():
        mx = int(massPoint[0])
        my = int(massPoint[1])
        binx = h2D.GetXaxis().FindBin(mx)
        biny = h2D.GetYaxis().FindBin(my)
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

def splitExcludedIntoClusters(excludedMasses,obs=True):
    cluster1 = []
    cluster2 = []
    for massPoint in excludedMasses:
        if(obs):
            if massPoint[0]>950:
                cluster1.append(massPoint)
            else:
                cluster2.append(massPoint)
        else:
            if massPoint[1]>100:
                cluster1.append(massPoint)
            else:
                cluster2.append(massPoint)

    #Fix to draw correct boundary
    if obs:
        cluster2.append((900.,76.5))
        cluster2.append((900.,70.5))
        cluster2.append((910.,76.5))
        cluster2.append((910.,70.5))
    return cluster1,cluster2

def plot2Dlims(h2,MX,MY,outputFile,obs=False,excludedMasses="",xRange=[],yRange=[]):
    plt.style.use(hep.style.CMS)
    h2 = np.array(h2)
    hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='')
    hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.01,norm=mcolors.LogNorm(vmin=0.01, vmax=100.))
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
    plt.ylabel("$M_{Y} [GeV]$", horizontalalignment='right', y=1.0)

    ax = plt.gca()
    clb=ax.collections[-1].colorbar

    if(obs):
        clb.set_label('Observed exclusion limits [fb]')
    else:
        clb.set_label('Expected exclusion limits [fb]')


    if(excludedMasses):
        x, y = list(zip(*excludedMasses))
        #plt.scatter(x,y,s=0.8, color='red')
        #For NMSSM
        cluster1, cluster2 = splitExcludedIntoClusters(excludedMasses,obs=obs)
        hull = ConvexHull(cluster1)
        if obs:
            excl_label = "Observed limits below\n maximum NMMSM cross section"
        else:
            excl_label = "Expected limits below\n maximum NMMSM cross section"
        polygonPts = np.array(cluster1)[hull.vertices]
        if(obs):
            polygonPts = np.insert(polygonPts,1,[ 1000.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore
        exp_excluded_patch = patches.Polygon(polygonPts,closed=True,hatch='//',edgecolor="red",facecolor="none",label=excl_label)
        ax.add_patch(exp_excluded_patch)

        if(cluster2):
            hull = ConvexHull(cluster2)
            exp_excluded_patch = patches.Polygon(np.array(cluster2)[hull.vertices],closed=True,hatch='//',edgecolor="red",facecolor="none")
            ax.add_patch(exp_excluded_patch)

        #For TRSSM
        # hull = ConvexHull(excludedMasses)
        # if obs:
        #     excl_label = "Observed limits below\n maximum TRSSM cross section"
        # else:
        #     excl_label = "Expected limits below\n maximum TRSSM cross section"
        # polygonPts = np.array(excludedMasses)[hull.vertices]

        # exp_excluded_patch = patches.Polygon(polygonPts,closed=True,hatch='//',edgecolor="red",facecolor="none",label=excl_label)
        # ax.add_patch(exp_excluded_patch)

        plt.legend(loc=1)



    if(xRange):
        ax.set_xlim(xRange)
    if(yRange):
        ax.set_ylim(yRange)

    fig  = matplotlib.pyplot.gcf()
    #plt.tight_layout()
    fig.set_size_inches(4.5*2.5, 3*2.5, forward=True)

    fig.savefig(outputFile)
    plt.close('all')

def plot2Dsig(h2,MX,MY,outputFile,pval=True):
    plt.style.use(hep.style.CMS)
    h2 = np.array(h2)
    hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='')
    if(pval):
        hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.0001,norm=mcolors.LogNorm(vmin=0.001, vmax=0.5))
    else:
        hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.0001,cmax=3.05)

    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
    plt.ylabel("$M_{Y} [GeV]$", horizontalalignment='right', y=1.0)

    ax = plt.gca()
    clb=ax.collections[-1].colorbar

    if(pval):
        clb.set_label('Observed significance (p-value)')
    else:
        clb.set_label('Observed significance (z-score)')

    fig  = matplotlib.pyplot.gcf()
    #plt.tight_layout()
    fig.set_size_inches(4.5*2.5, 3*2.5, forward=True)

    fig.savefig(outputFile)
    plt.close('all')

def getExcludedMasses(h2_limits,h2_xsecs):
    NX = h2_limits.GetNbinsX()
    NY = h2_limits.GetNbinsY()
    masses = []
    for i in range(1,NX+1):
        for j in range(1,NY+1):
            limit = h2_limits.GetBinContent(i,j)
            if(limit==0):
                continue
            xsec  = h2_xsecs.GetBinContent(i,j)
            if(limit<xsec):
                mx = h2_limits.GetXaxis().GetBinCenter(i)
                my = h2_limits.GetYaxis().GetBinCenter(j)
                masses.append((mx,my))
    return masses

if __name__ == '__main__':
    #Orig limits and xsecs
    # print("Expected")
    # limsToHisto("limits_granulated.root")
    # print("Observed")
    # limsToHisto("limits_granulated.root",obs=True)
    # print("Significances")
    # sigToHisto("limits_granulated.root")

    # print("NMSSM Cross-sections")
    # xsecsToHisto("limits_granulated.root")
    # print("TRSSE Cross-sections")
    # xsecsToHisto("limits_granulated.root",NMSSM=False)


    # #Smoothing
    # f = r.TFile.Open("limits_granulated.root")
    # print("Starting smoothing")
    # xsecs = f.Get("NMSSM_orig")
    # xsecs_first_pass  = interp.interpolateHisto(xsecs,direction="horizontal",hName="NMSSM_horizontal",boostedCond=False)
    # xsecs_smooth      = interp.interpolateHisto(xsecs_first_pass,direction="vert",hName="NMSSM_horizontal_vertical",boostedCond=False)
    # print("Smoothed NMSSM xsecs")

    # xsecs_TRSSE = f.Get("TRSSE_orig")
    # xsecs_TRSSE_first_pass  = interp.interpolateHisto(xsecs_TRSSE,direction="horizontal",hName="TRSSE_horizontal",boostedCond=False)
    # xsecs_TRSSE_smooth= interp.interpolateHisto(xsecs_TRSSE_first_pass,direction="vert",hName="TRSSE_horizontal_vertical",boostedCond=False)
    # print("Smoothed TRSSE xsecs")

    # h2_exp = f.Get("exp_limits")
    # h2_exp_first_pass     = interp.interpolateHisto(h2_exp,direction="horizontal",hName="exp_horizontal")
    # h2_exp_smooth         = interp.interpolateHisto(h2_exp_first_pass,direction="vert",hName="exp_horizontal_vertical")
    # print("Smoothed expected")

    # h2_obs = f.Get("obs_limits")
    # h2_obs_first_pass     = interp.interpolateHisto(h2_obs,direction="horizontal",hName="obs_horizontal")
    # h2_obs_smooth         = interp.interpolateHisto(h2_obs_first_pass,direction="vert",hName="obs_horizontal_vertical")
    # print("Smoothed observed")

    # h2_pval = f.Get("obs_sig_pval")
    # h2_pval_first_pass     = interp.interpolateHisto(h2_pval,direction="horizontal",hName="pval_horizontal")
    # h2_pval_smooth         = interp.interpolateHisto(h2_pval_first_pass,direction="vert",hName="pval_horizontal_vertical")
    # h2_z  = pvalHistToSig(h2_pval_smooth)
    # print("Smoothed p-val")


    # g = r.TFile.Open("smooth_limits.root","RECREATE")
    # g.cd()
    # xsecs.Write()
    # xsecs_first_pass.Write()
    # xsecs_smooth.Write()
    # xsecs_TRSSE.Write()
    # xsecs_TRSSE_first_pass.Write()
    # xsecs_TRSSE_smooth.Write()
    # h2_exp.Write()
    # h2_exp_first_pass.Write()
    # h2_exp_smooth.Write()
    # h2_obs.Write()
    # h2_obs_first_pass.Write()
    # h2_obs_smooth.Write()
    # h2_pval_first_pass
    # h2_pval_smooth.Write()
    # h2_z.Write()
    # g.Close()

    #NMSSM
    f = r.TFile.Open("smooth_limits.root")
    h2_xsecs = f.Get("NMSSM_horizontal_vertical")

    h2_smooth = f.Get("exp_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    plot2Dlims(limit_vals_2d,MX,MY,"NMSSM_exp.png",obs=False,excludedMasses=excludedMasses)

    h2_smooth = f.Get("obs_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    plot2Dlims(limit_vals_2d,MX,MY,"NMSSM_obs.png",obs=True,excludedMasses=excludedMasses)

    #Significances
    # h2 = f.Get("pval_horizontal_vertical")
    # p_val_2d,MX,MY=h2ToArray(h2)
    # plot2Dsig(p_val_2d,MX,MY,"p_val.png",pval=True)

    # h2 = f.Get("z_horizontal_vertical")
    # z_val_2d,MX,MY=h2ToArray(h2)
    # plot2Dsig(z_val_2d,MX,MY,"z_val.png",pval=False)

    #Zoomed in exclusion
    # xRange = [900,1200]
    # yRange = [60,200]
    # h2_smooth = f.Get("exp_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"exp_horizontal_vertical.png",obs=False,excludedMasses=excludedMasses,xRange=xRange,yRange=yRange)

    # h2_smooth = f.Get("obs_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"obs_horizontal_vertical.png",obs=True,excludedMasses=excludedMasses,xRange=xRange,yRange=yRange)


    #TRSSM
    # f = r.TFile.Open("smooth_limits.root")
    # h2_xsecs = f.Get("TRSSE_horizontal_vertical")

    # h2_smooth = f.Get("exp_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"TRSSM_exp.png",obs=False,excludedMasses=excludedMasses)


    # h2_smooth = f.Get("obs_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"TRSSM_obs.png",obs=True,excludedMasses=excludedMasses)