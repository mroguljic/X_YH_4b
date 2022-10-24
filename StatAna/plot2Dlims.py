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
import matplotlib.ticker as ticker
import matplotlib.collections as mcol
from matplotlib.legend_handler import HandlerLineCollection
from matplotlib.lines import Line2D
import interpolateLimits as interp
from scipy.spatial import ConvexHull
import string

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0)

def limsToText(output,cat):
    signalNorm = 1.0 #fb
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')

    if(cat==0):
        hName = "m1_limits"
    elif(cat==1):
        hName = "m2_limits"
    elif(cat==2):
        hName = "exp_limits"
    elif(cat==3):
        hName = "p1_limits"
    elif(cat==4):
        hName = "p2_limits"
    elif(cat==5):
        hName = "obs_limits"

    print(hName)

    lines = ""

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
            limTree.GetEntry(cat)
            limit = limTree.limit*signalNorm
            line  = "{0},{1},{2:.3f}\n".format(mx,my,limit)
            lines+=line

    with open(output, 'w') as f:
        f.write(lines)



#For legend handling
class HandlerDashedLines(HandlerLineCollection):
    """
    Custom Handler for LineCollection instances.
    """
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        # figure out how many lines there are
        numlines = len(orig_handle.get_segments())
        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,
                                             width, height, fontsize)
        leglines = []
        # divide the vertical space where the lines will go
        # into equal parts based on the number of lines
        ydata = ((height) / (numlines + 1)) * np.ones(xdata.shape, float)
        # for each line, create the line at the proper location
        # and set the dash pattern
        for i in range(numlines):
            legline = Line2D(xdata, ydata * (numlines - i) - ydescent)
            self.update_prop(legline, orig_handle, legend)
            # set color, dash pattern, and linewidth to that
            # of the lines in linecollection
            try:
                color = orig_handle.get_colors()[i]
            except IndexError:
                color = orig_handle.get_colors()[0]
            try:
                dashes = orig_handle.get_dashes()[i]
            except IndexError:
                dashes = orig_handle.get_dashes()[0]
            try:
                lw = orig_handle.get_linewidths()[i]
            except IndexError:
                lw = orig_handle.get_linewidths()[0]
            if dashes[0] is not None:
                legline.set_dashes(dashes[1])
            legline.set_color(color)
            legline.set_transform(trans)
            legline.set_linewidth(lw)
            leglines.append(legline)
        return leglines


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

def limsToHisto(output,cat):
    signalNorm = 1.0 #fb
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')

    granulatedMX = np.arange(900,4020,10,dtype='float64')
    granulatedMY = np.arange(60,602,1,dtype='float64')

    if(cat==0):
        hName = "m1_limits"
    elif(cat==1):
        hName = "m2_limits"
    elif(cat==2):
        hName = "exp_limits"
    elif(cat==3):
        hName = "p1_limits"
    elif(cat==4):
        hName = "p2_limits"
    elif(cat==5):
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
            limTree.GetEntry(cat)
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
            if massPoint[0]>0.950:
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
        cluster2.append((0.900,76.5))
        cluster2.append((0.900,70.5))
        cluster2.append((0.910,76.5))
        cluster2.append((0.910,70.5))
    return cluster1,cluster2

def plot2Dlims(h2,MX,MY,outputFile,obs=False,excludedMasses="",xRange=[],yRange=[]):
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


    if(excludedMasses):
        x, y = list(zip(*excludedMasses))
        plt.scatter(x,y,s=0.8, color='red')
        #For NMSSM
        # cluster1, cluster2 = splitExcludedIntoClusters(excludedMasses,obs=obs)
        # hull = ConvexHull(cluster1)
        # if obs:
        #     excl_label = "Observed limits below\n maximum NMSSM cross section"
        # else:
        #     excl_label = "Expected limits below\n maximum NMSSM cross section"
        # polygonPts = np.array(cluster1)[hull.vertices]
        # if(obs):
        #     polygonPts = np.insert(polygonPts,1,[ 1000.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore
        # exp_excluded_patch = patches.Polygon(polygonPts,closed=True,hatch='//',edgecolor="red",facecolor="none",label=excl_label)
        # ax.add_patch(exp_excluded_patch)

        # if(cluster2):
        #     hull = ConvexHull(cluster2)
        #     exp_excluded_patch = patches.Polygon(np.array(cluster2)[hull.vertices],closed=True,hatch='//',edgecolor="red",facecolor="none")
        #     ax.add_patch(exp_excluded_patch)

        #For TRSSM
        # hull = ConvexHull(excludedMasses)
        # if obs:
        #     excl_label = "Observed limits below\n maximum TRSM cross section"
        # else:
        #     excl_label = "Expected limits below\n maximum TRSM cross section"
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

    fig.savefig(outputFile,dpi=500)
    plt.close('all')

def plot2Dlims_bothExclusions(h2,MX,MY,outputFile,obs,excludedNMSSM,excludedTRSSM,xRange=[],yRange=[],colorTest="black",m1NMSSM=[],m1TRSM=[]):
    plt.style.use(hep.style.CMS)
    matplotlib.rcParams.update({'font.size': 30})
    matplotlib.rcParams.update({'lines.linewidth':2})
    h2 = np.array(h2)
    #hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='')
    #hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='')

    hep.cms.lumitext('138 $fb^{-1}$ (13 TeV)')
    #hep.cms.text("",loc=1)
    hep.cms.text("",loc=0)
    hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.01,norm=mcolors.LogNorm(vmin=0.1, vmax=200.))
    plt.xlabel("$M_{X} [TeV]$", horizontalalignment='right', x=1.0)
    plt.ylabel("$M_{Y} [GeV]$", horizontalalignment='right', y=1.0)

    if(m1TRSM!=[]):
        m1Flag = True
    else:
        m1Flag = False

    ax = plt.gca()
    clb=ax.collections[-1].colorbar

    if(obs):
        #clb.set_label('Observed exclusion limits [fb]')
        clb.set_label('Observed exclusion limits at 95% CL\n'+r'on $\sigma$(pp$\rightarrow$X$\rightarrow$YH$\rightarrow b\overline{b} b\overline{b}$) [fb]')
    else:
        #clb.set_label('Expected exclusion limits [fb]')
        clb.set_label('Expected exclusion limits at 95% CL\n'+r'on $\sigma$(pp$\rightarrow$X$\rightarrow$YH$\rightarrow b\overline{b} b\overline{b}$) [fb]')


    #NMSSM
    #cluster1, cluster2 = splitExcludedIntoClusters(excludedNMSSM,obs=obs)

    if obs:
        excl_label = "Observed for NMSSM"
    else:
        excl_label = "Expected for NMSSM"   
    if(len(excludedNMSSM)!=0):
        #x, y = list(zip(*excludedNMSSM))
        #plt.scatter(x,y,s=0.8, color='red')

        hull = ConvexHull(excludedNMSSM)

        polygonPts = np.array(excludedNMSSM)[hull.vertices]
        print("NMSSM pts")
        print(polygonPts)
        exp_excluded_patch = patches.Polygon(polygonPts,closed=True,edgecolor="red",facecolor="none",label=excl_label,linewidth=2,linestyle="--")
        ax.add_patch(exp_excluded_patch)
    #if(obs):
        #polygonPts = np.insert(polygonPts,1,[ 1000.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore
        #polygonPts = np.insert(polygonPts,1,[ 1.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore

    # if(cluster2):
    #     hull = ConvexHull(cluster2)
    #     exp_excluded_patch = patches.Polygon(np.array(cluster2)[hull.vertices],closed=True,edgecolor="red",facecolor="none")
    #     ax.add_patch(exp_excluded_patch)

    #     print("NMSSM 1")
    #     print(polygonPts)
    #     print("NMSSM 2")
    #     print(np.array(cluster2)[hull.vertices])

    #For TRSSM
    hull = ConvexHull(excludedTRSSM)
    if obs:
        excl_label = "Observed for TRSM"
    else:
        excl_label = "Expected for TRSM"
    polygonPts = np.array(excludedTRSSM)[hull.vertices]
    if(obs):
        #polygonPts = np.insert(polygonPts,6,[ 1000.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore
        polygonPts = np.insert(polygonPts,6,[ 1.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore
    print("TRSM pts")
    print(polygonPts)

    exp_excluded_patch = patches.Polygon(polygonPts,closed=True,edgecolor=colorTest,facecolor="none",label=excl_label,linewidth=2)
    ax.add_patch(exp_excluded_patch)


    if(m1Flag):
        exp_m1_patch = patches.Polygon(m1NMSSM,closed=True,edgecolor="red",facecolor="none",linestyle="--",label=None,linewidth=2)
        ax.add_patch(exp_m1_patch)
        exp_m1_patch = patches.Polygon(m1TRSM,closed=True,edgecolor=colorTest,facecolor="none",linestyle=":",label=None,linewidth=3)
        ax.add_patch(exp_m1_patch)


        #Legend fiddling if plotting m1 limits
        # make proxy artists
        line = [[(0, 0)]]
        # set up the proxy artist
        lcNMSSM_med = mcol.LineCollection(1 * line, linestyles=["-"], colors=["red"])
        lcNMSSM_m1 = mcol.LineCollection(1 * line, linestyles=["--"], colors=["red"],linewidths=[2])
        lcTRSM_med  = mcol.LineCollection(1 * line, linestyles=["-"], colors=[colorTest],linewidths=[2])
        lcTRSM_m1  = mcol.LineCollection(1 * line, linestyles=[":"], colors=[colorTest],linewidths=[3])
        labelNMSSM_med = "Median expected for NMSSM"
        labelNMSSM_m1 = "-1$\sigma$ for NMSSM"
        labelTRSM_med = "Median expected for TRSM"
        labelTRSM_m1 = "-1$\sigma$ for TRSM"
        # create the legend
        #leg = plt.legend([lcNMSSM_m1,lcTRSM_med,lcTRSM_m1], [labelNMSSM_m1,labelTRSM_med,labelTRSM_m1], handler_map={type(labelNMSSM_m1): HandlerDashedLines()},handlelength=2, handleheight=0.5)
        leg = plt.legend([lcNMSSM_m1,lcTRSM_med,lcTRSM_m1], [labelNMSSM_m1,labelTRSM_med,labelTRSM_m1])

    else:
        line = [[(0, 0)]]
        # set up the proxy artist
        lcNMSSM = mcol.LineCollection(1 * line, linestyles=["--"], colors=["red"])
        lcTRSM  = mcol.LineCollection(1 * line, linestyles=["-"], colors=[colorTest])
        labelNMSSM = "Observed for NMSSM"
        labelTRSM = "Observed for TRSM"
        # create the legend
        leg = plt.legend([lcNMSSM,lcTRSM], [labelNMSSM,labelTRSM], handler_map={type(lcNMSSM): HandlerDashedLines()},
                   handlelength=2, handleheight=1)        

        #leg = plt.legend(loc=1)
    
    for text in leg.get_texts():
        text.set_color("black")



    if(xRange):
        ax.set_xlim(xRange)
    if(yRange):
        ax.set_ylim(yRange)

    ax.set_yscale("log")
    ax.set_xscale("log")
    #Axis editing here
    ax.xaxis.set_ticks(np.arange(1.0, 4.01, 0.5))
    ax.xaxis.set_ticks(np.arange(0.9, 4.01, 0.1),minor=True)

    #ax.xaxis.set_major_formatter(ticker.StrMethodFormatter(('{x:{c}}').format(x=x, c='.1f' if num%1!=0 else c='.0f')))
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:g}'))

    #ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
    
    ax.yaxis.set_ticks(np.arange(100, 601, 100))
    ax.yaxis.set_ticks(np.arange(60, 600, 20),minor=True)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%i'))

    plt.setp(ax.get_xminorticklabels(), visible=False)
    plt.setp(ax.get_yminorticklabels(), visible=False)


    fig  = matplotlib.pyplot.gcf()
    #plt.tight_layout()
    fig.set_size_inches(4.8*2.5, 3.2*2.5, forward=True)

    fig.savefig(outputFile.replace(".png","_"+colorTest+".png"),dpi=500)
    plt.close('all')

def plot2Dlims_m1(h2,MX,MY,outputFile,obs,excludedNMSSM,excludedTRSSM,xRange=[],yRange=[],colorTest="black"):
    plt.style.use(hep.style.CMS)
    matplotlib.rcParams.update({'font.size': 30})
    h2 = np.array(h2)
    hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='')
    hep.hist2dplot(h2,xbins=MX,ybins=MY,cmin=0.01,norm=mcolors.LogNorm(vmin=0.01, vmax=100.))
    plt.xlabel("$M_{X} [TeV]$", horizontalalignment='right', x=1.0)
    plt.ylabel("$M_{Y} [GeV]$", horizontalalignment='right', y=1.0)

    ax = plt.gca()
    clb=ax.collections[-1].colorbar
    clb.set_label('Expected - 1$\sigma$ exclusion limits at 95% CL\n'+r'on $\sigma$(pp$\rightarrow$X$\rightarrow$YH$\rightarrow b\overline{b} b\overline{b}$) [fb]')


    #NMSSM
    hull = ConvexHull(excludedNMSSM)
    x, y = list(zip(*excludedNMSSM))
    plt.scatter(x,y,s=0.8, color='red')

    excl_label = "Expected - 1$\sigma$ limits for NMSSM"
    polygonPts = np.array(excludedNMSSM)[hull.vertices]
    print("NMSSM pts")
    print(polygonPts)
    polygonPtsNMSSM = np.insert(polygonPts,7,[ 1.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore
    exp_excluded_patch = patches.Polygon(polygonPtsNMSSM,closed=True,edgecolor="red",facecolor="none",label=excl_label)
    ax.add_patch(exp_excluded_patch)


    #For TRSSM
    hull = ConvexHull(excludedTRSSM)
    excl_label = "Expected - 1$\sigma$ limits for TRSM"
    polygonPts = np.array(excludedTRSSM)[hull.vertices]
    print("TRSM pts")
    print(polygonPts)
    polygonPtsTRSM = np.insert(polygonPts,-1,[ 1.,125.5],0)#Hotfix to not go away into MX,MY space we didn't explore

    exp_excluded_patch = patches.Polygon(polygonPtsTRSM,closed=True,edgecolor=colorTest,facecolor="none",linestyle="--",label=excl_label)
    ax.add_patch(exp_excluded_patch)

    leg = plt.legend(loc=1)
    for text in leg.get_texts():
        text.set_color("black")



    if(xRange):
        ax.set_xlim(xRange)
    if(yRange):
        ax.set_ylim(yRange)

    ax.set_yscale("log")
    ax.set_xscale("log")
    #Axis editing here
    ax.xaxis.set_ticks(np.arange(1.0, 4.01, 0.5))
    ax.xaxis.set_ticks(np.arange(0.9, 4.01, 0.1),minor=True)

    #ax.xaxis.set_major_formatter(ticker.StrMethodFormatter(('{x:{c}}').format(x=x, c='.1f' if num%1!=0 else c='.0f')))
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:g}'))

    #ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
    
    ax.yaxis.set_ticks(np.arange(100, 601, 100))
    ax.yaxis.set_ticks(np.arange(60, 600, 20),minor=True)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%i'))

    plt.setp(ax.get_xminorticklabels(), visible=False)
    plt.setp(ax.get_yminorticklabels(), visible=False)


    fig  = matplotlib.pyplot.gcf()
    #plt.tight_layout()
    fig.set_size_inches(4.8*2.5, 3.2*2.5, forward=True)

    fig.savefig(outputFile.replace(".png","_"+colorTest+".png"),dpi=500)
    plt.close('all')
    return polygonPtsNMSSM,polygonPtsTRSM


def plot2Dsig(h2,MX,MY,outputFile,pval=True):
    plt.style.use(hep.style.CMS)
    h2 = np.array(h2)
    hep.cms.label(loc=0, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')
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

    fig.savefig(outputFile,dpi=500)
    plt.close('all')

def getExcludedMasses(h2_limits,h2_xsecs,mxScale=1.):
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
                masses.append((mx*mxScale,my))
    return masses

if __name__ == '__main__':

    #limsToText("test.csv",5)

    #Orig limits and xsecs
    # for i in range(0,6):
        # limsToHisto("limits_granulated.root",i)


    #print("Significances")
    #sigToHisto("limits_granulated.root")

    #print("NMSSM Cross-sections")
    #xsecsToHisto("limits_granulated.root")
    #print("TRSSE Cross-sections")
    #xsecsToHisto("limits_granulated.root",NMSSM=False)


    # #Smoothing

    #-1 and -2 sigma
    # f = r.TFile.Open("limits_granulated.root")

    # h2_m1 = f.Get("m1_limits")
    # h2_m1_first_pass     = interp.interpolateHisto(h2_m1,direction="horizontal",hName="m1_horizontal")
    # h2_m1_smooth         = interp.interpolateHisto(h2_m1_first_pass,direction="vert",hName="m1_horizontal_vertical")
    # print("Smoothed m1")

    # h2_m2 = f.Get("m2_limits")
    # h2_m2_first_pass     = interp.interpolateHisto(h2_m2,direction="horizontal",hName="m2_horizontal")
    # h2_m2_smooth         = interp.interpolateHisto(h2_m2_first_pass,direction="vert",hName="m2_horizontal_vertical")
    # print("Smoothed m2")

    # g = r.TFile.Open("additional.root","RECREATE")
    # g.cd()
    # h2_m1.Write()
    # h2_m1_first_pass.Write()
    # h2_m1_smooth.Write()
    # h2_m2.Write()
    # h2_m2_first_pass.Write()
    # h2_m2_smooth.Write()


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

    # g = r.TFile.Open("smooth_limits.root","UPDATE")
    # g.cd()
    # xsecs.Write()
    # xsecs_first_pass.Write()
    # xsecs_smooth.Write()
    # g.Close()

    #NMSSM -1/-2sigma
    # f = r.TFile.Open("smooth_limits.root")
    # h2_xsecs = f.Get("NMSSM_horizontal_vertical")

    # h2_smooth = f.Get("m2_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"NMSSM_m1.png",obs=False,excludedMasses=excludedMasses)

    #NMSSM exp
    # f = r.TFile.Open("smooth_limits.root")
    # h2_xsecs = f.Get("NMSSM_horizontal_vertical")

    # h2_smooth = f.Get("exp_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"NMSSM_exp.png",obs=False,excludedMasses=excludedMasses)

    # h2_smooth = f.Get("obs_horizontal_vertical")
    # limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    # excludedMasses = getExcludedMasses(h2_smooth,h2_xsecs)
    # plot2Dlims(limit_vals_2d,MX,MY,"NMSSM_obs.png",obs=True,excludedMasses=excludedMasses)

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


    #BOTH
    #Obs
    f = r.TFile.Open("smooth_limits.root")
    h2_TRSSM = f.Get("TRSSE_horizontal_vertical")
    h2_NMSSM = f.Get("NMSSM_horizontal_vertical")

    h2_smooth = f.Get("obs_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    excludedTRSSM = getExcludedMasses(h2_smooth,h2_TRSSM,mxScale=0.001)
    excludedNMSSM = getExcludedMasses(h2_smooth,h2_NMSSM,mxScale=0.001)
    MX = [float(mx)/1000. for mx in MX]

    #print("Excluded TRSM")
    #print(excludedTRSSM)

    #print("Excluded NMSSM")
    #print(excludedNMSSM)


    plot2Dlims_bothExclusions(limit_vals_2d,MX,MY,"2D_both_theories.png",True,excludedNMSSM,excludedTRSSM,xRange=[],yRange=[60,1600])
    
    # colors = ["black","white","darkorange","orange","peru","aqua"]
    # for color in colors:
    #    plot2Dlims_bothExclusions(limit_vals_2d,MX,MY,"2D_both_theories.png",True,excludedNMSSM,excludedTRSSM,xRange=[],yRange=[],colorTest=color)
    # plot2Dlims_bothExclusions(limit_vals_2d,MX,MY,"2D_both_theories_zoomed.png",True,excludedNMSSM,excludedTRSSM,xRange=[900,1500],yRange=[60,200])

    #Exp -1sigma
    f = r.TFile.Open("smooth_limits.root")
    h2_TRSSM = f.Get("TRSSE_horizontal_vertical")
    h2_NMSSM = f.Get("NMSSM_horizontal_vertical")
    h2_smooth = f.Get("m1_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    MX = [float(mx)/1000. for mx in MX]
    excludedTRSSM = getExcludedMasses(h2_smooth,h2_TRSSM,mxScale=0.001)
    excludedNMSSM = getExcludedMasses(h2_smooth,h2_NMSSM,mxScale=0.001)

    m1NMSSM, m1TRSM = plot2Dlims_m1(limit_vals_2d,MX,MY,"test.png",False,excludedNMSSM,excludedTRSSM,xRange=[],yRange=[])

    # #Exp
    f = r.TFile.Open("smooth_limits.root")
    h2_TRSSM = f.Get("TRSSE_horizontal_vertical")
    h2_NMSSM = f.Get("NMSSM_horizontal_vertical")
    h2_smooth = f.Get("exp_horizontal_vertical")
    limit_vals_2d,MX,MY=h2ToArray(h2_smooth)
    MX = [float(mx)/1000. for mx in MX]
    excludedTRSSM = getExcludedMasses(h2_smooth,h2_TRSSM,mxScale=0.001)
    excludedNMSSM = getExcludedMasses(h2_smooth,h2_NMSSM,mxScale=0.001)

    #print("Excluded TRSM")
    #print(excludedTRSSM)

    #print("Excluded NMSSM")
    #print(excludedNMSSM)

    plot2Dlims_bothExclusions(limit_vals_2d,MX,MY,"2D_both_theories_exp.png",False,excludedNMSSM,excludedTRSSM,m1NMSSM=m1NMSSM,m1TRSM=m1TRSM,yRange=[60,1600])
    # #plot2Dlims_bothExclusions(limit_vals_2d,MX,MY,"2D_both_theories_zoomed_exp.png",False,excludedNMSSM,excludedTRSSM,xRange=[900,1500],yRange=[60,200])



