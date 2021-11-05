#!/usr/bin/env python
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib
from matplotlib import colors as mcolors
import ROOT as r
import os
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from plot2Dlims import readXsecs
from scipy.interpolate import interp1d

matplotlib.use('Agg')

def getLimits(rootFile,signalNorm=1.0):
    f = r.TFile.Open(rootFile)
    limitTree = f.Get("limit")
    limits = []
    for limit in limitTree:
        limits.append(limit.limit*signalNorm)#signal is normalized to 1.0fb xsec

    return limits

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
        print("Missing file: {0}".format(file))
        return False

def getTheoryLine(fixedVar,mass,xsecs):
    #fixedVar should be "my" or "mx"
    line = []
    for massPoint in xsecs:
        mx = massPoint[0]
        my = massPoint[1]
        if(fixedVar=="my" and my!=mass):
            continue
        if(fixedVar=="mx" and mx!=mass):
            continue
        xsec = xsecs[massPoint]

        if(fixedVar=="my"):
            line.append((mx,xsec))
        if(fixedVar=="mx"):
            line.append((my,xsec))
    return line

def mxLimits(my=125,obs=False):
    MX = [900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
    #MX = [1000,1200,1400,1600,1800,2000,2200,2800,3000]
    limits = []
    goodMX = []
    for mx in MX:
        #file_limits = "limits/obsLimits_snapshot/MX{0}_MY{1}.root".format(int(mx),int(my))
        #file_limits = "limits/obsLimits/MX{0}_MY{1}.root".format(int(mx),int(my))
        file_limits = "limits/obsLimits_1fb_signal_new_skims/MX{0}_MY{1}.root".format(int(mx),int(my))
        if not (checkLimitFile(file_limits)):
            continue
        goodMX.append(mx)
        limits.append(getLimits(file_limits))

    #transpose so that:
    #limitsDEta[0][:] corresponds to exp 95% limits low
    #limitsDEta[1][:] corresponds to exp 68% limits low
    #limitsDEta[2][:] corresponds to exp limits
    #limitsDEta[3][:] corresponds to exp 68% limits up
    #limitsDEta[4][:] corresponds to exp 95% limits up
    limits = np.array(limits)
    limits = limits.T.tolist() 

    plt.style.use(hep.style.CMS)
    hep.cms.label(loc=1, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')

    plt.fill_between(goodMX, limits[1], limits[3], color='forestgreen', label='68% expected')
    plt.fill_between(goodMX, limits[0], limits[4], color='darkorange', label='95% expected')
    plt.fill_between(goodMX, limits[1], limits[3], color='forestgreen', label='_nolegend_')
    plt.plot(goodMX, limits[2], color='black', linewidth='2.4', linestyle='--', label=r'Median expected')
    if(obs):
        plt.plot(goodMX, limits[5], color='black', linewidth='2.4', linestyle='-', label=r'Observed')
    plt.xlabel("$M_{X} [GeV]$")
    plt.ylabel(r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$',horizontalalignment='right', y=1.0)
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
    plt.text(3000, 250, r'$M_{Y} = '+str(my)+r'\,GeV$')
    plt.yscale('log')
    plt.ylim(0.01, 10**3)
    plt.legend(loc=(0.10,0.60)
      , title='95% CL upper limits'
      ,ncol=2
      ,title_fontsize=17
      ,fontsize=17
      )


    #plt.tight_layout()

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(4*2.5, 3*2.5, forward=True)

    if(obs):
        fig.savefig('obslim_MX_MY{0}.pdf'.format(my))
        fig.savefig('obslim_MX_MY{0}.png'.format(my))
    else:
        fig.savefig('explim_MX_MY{0}.pdf'.format(my))
        fig.savefig('explim_MX_MY{0}.png'.format(my))
    plt.clf()


def theoryCutoff(lastMY,theory_my):
    #Returns the index at which the theory curve should stop to match the available limits
    lastIdx = -1
    for i in range(len(theory_my)):
        if(theory_my[i]>lastMY):
            lastIdx = i
            return lastIdx
    return lastIdx

def multipleMY(MY,obs=False,xsecs="",smooth=False,outputFile="limitPlots/obslim_2D_slices"):
    MX = [900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
    limits = []#MY,significance,MX
    theoryLines = []
    goodMX = []#MY, good MX
    for my in MY:
        if(xsecs):
            theoryLine = getTheoryLine("my",my,xsecs)
            theoryLines.append(theoryLine)
        tempLimits = []
        tempMX     = []
        for mx in MX:
            file_limits = "limits/obsLimits_1fb_signal_new_skims/MX{0}_MY{1}.root".format(int(mx),int(my))                
            if not (checkLimitFile(file_limits)):
                continue
            expLimits = getLimits(file_limits)
            if not expLimits:
                continue
            tempMX.append(mx)
            tempLimits.append(expLimits)
        limits.append(tempLimits)
        goodMX.append(tempMX)

    #transpose so that:
    #limits[][0][:] corresponds to exp 95% limits low
    #limits[][1][:] corresponds to exp 68% limits low
    #limits[][2][:] corresponds to exp limits
    #limits[][3][:] corresponds to exp 68% limits up
    #limits[][4][:] corresponds to exp 95% limits up
    #limits[][5][:] corresponds to observed limit
    for i in range(len(limits)):
        limits[i] = np.array(limits[i])
        limits[i] = limits[i].T.tolist() 


    plt.style.use(hep.style.CMS)
    matplotlib.rcParams.update({'font.size': 40})
    f, axs = plt.subplots(len(MY),1, sharex=True, sharey=False,gridspec_kw={'hspace': 0.03})
    plt.subplots_adjust(top=0.95, bottom=0.05)
    for i in range(len(MY)):
        plt.sca(axs[i])
        if(i==0):
            hep.cms.label(loc=1, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')

        mxPts   = goodMX[i]
        m2sigma = limits[i][0]
        m1sigma = limits[i][1]
        median  = limits[i][2]
        p1sigma = limits[i][3]
        p2sigma = limits[i][4]
        obsLim  = limits[i][5]

        splineType = "quadratic"

        mxPtsSmooth    = np.linspace(mxPts[0],mxPts[-1],100,dtype="float64")
        m2sigmaSmooth  = interp1d(mxPts, np.log(m2sigma), kind=splineType)
        m1sigmaSmooth  = interp1d(mxPts, np.log(m1sigma), kind=splineType)
        medianSmooth   = interp1d(mxPts, np.log(median), kind=splineType)
        p1sigmaSmooth  = interp1d(mxPts, np.log(p1sigma), kind=splineType)
        p2sigmaSmooth  = interp1d(mxPts, np.log(p2sigma), kind=splineType)
        obsLimSmooth   = interp1d(mxPts, np.log(obsLim), kind=splineType)

        if(smooth):
            plt.fill_between(mxPtsSmooth, np.exp(m1sigmaSmooth(mxPtsSmooth)), np.exp(p1sigmaSmooth(mxPtsSmooth)), color='forestgreen', label='_nolegend_')
            plt.fill_between(mxPtsSmooth, np.exp(m2sigmaSmooth(mxPtsSmooth)), np.exp(p2sigmaSmooth(mxPtsSmooth)), color='darkorange',  label='_nolegend_')
            plt.fill_between(mxPtsSmooth, np.exp(m1sigmaSmooth(mxPtsSmooth)), np.exp(p1sigmaSmooth(mxPtsSmooth)), color='forestgreen', label='_nolegend_')
            plt.plot(mxPtsSmooth, np.exp(medianSmooth(mxPtsSmooth)), color='black', linewidth='2.4', linestyle='--', label='_nolegend_')
            if(obs):
                plt.plot(mxPtsSmooth, np.exp(obsLimSmooth(mxPtsSmooth)), color='black', linewidth='2.4', linestyle='-', label='_nolegend_')            
        else:
            plt.fill_between(mxPts, m1sigma, p1sigma, color='forestgreen', label='_nolegend_')
            plt.fill_between(mxPts, m2sigma, p2sigma, color='darkorange',  label='_nolegend_')
            plt.fill_between(mxPts, m1sigma, p1sigma, color='forestgreen', label='_nolegend_')
            plt.plot(mxPts, median, color='black', linewidth='2.4', linestyle='--', label='_nolegend_')
            if(obs):
                plt.plot(mxPts, obsLim, color='black', linewidth='2.4', linestyle='-', label='_nolegend_')
        if(xsecs):
            theory_mx, theory_my = list(zip(*theoryLines[i]))
            plt.plot(theory_mx, theory_my, color='red', linewidth='2.4', linestyle='-', label=r'NMSSM maximum cross-section')


        plt.text(3000, 10, r'$M_{Y} = '+str(MY[i])+r'\,GeV$')
        plt.yscale('log')
        axs[i].set_ylim(0.03,500)
        axs[i].tick_params(axis='y', which='minor', direction='in')
        axs[i].yaxis.set_minor_locator(AutoMinorLocator())
        axs[i].minorticks_on()

        if(i==0):
            plt.legend(loc=4)

    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)




    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(6*2.5, (2*len(MY))*2.0, forward=True)
    #fig.text(0.03, 0.5, r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$', va="center", rotation='vertical',fontsize=50)
    fig.text(0.03, 0.5, r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$', va="center", rotation='vertical')
    
    fig.savefig(outputFile+".png")
    fig.savefig(outputFile+".pdf")
    plt.clf()

def multipleMX(MX,obs=False,xsecs="",smooth=False,outputFile="limitPlots/obslim_2D_slices_MX"):
    MY = [60,70,80,90,100,125,150,200,250,300,350,400,450,500,600]
    limits = []#MX,limit at CL,MY
    theoryLines = []
    goodMY = []#MX, good MY
    for mx in MX:
        if(xsecs):
            theoryLine = getTheoryLine("mx",mx,xsecs)
            theoryLines.append(theoryLine)
        tempLimits = []
        tempMY     = []
        for my in MY:
            file_limits = "limits/obsLimits_1fb_signal_new_skims/MX{0}_MY{1}.root".format(int(mx),int(my))                
            if not (checkLimitFile(file_limits)):
                continue
            expLimits = getLimits(file_limits)
            if not expLimits:
                continue
            tempMY.append(my)
            tempLimits.append(expLimits)
        limits.append(tempLimits)
        goodMY.append(tempMY)

    #transpose so that:
    #limits[][0][:] corresponds to exp 95% limits low
    #limits[][1][:] corresponds to exp 68% limits low
    #limits[][2][:] corresponds to exp limits
    #limits[][3][:] corresponds to exp 68% limits up
    #limits[][4][:] corresponds to exp 95% limits up
    #limits[][5][:] corresponds to observed limit
    for i in range(len(limits)):
        limits[i] = np.array(limits[i])
        limits[i] = limits[i].T.tolist() 


    plt.style.use(hep.style.CMS)
    matplotlib.rcParams.update({'font.size': 40})
    f, axs = plt.subplots(len(MX),1, sharex=True, sharey=False,gridspec_kw={'hspace': 0.03})
    plt.subplots_adjust(top=0.95, bottom=0.05)
    for i in range(len(MX)):
        plt.sca(axs[i])
        if(i==0):
            hep.cms.label(loc=1, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')

        myPts   = goodMY[i]
        m2sigma = limits[i][0]
        m1sigma = limits[i][1]
        median  = limits[i][2]
        p1sigma = limits[i][3]
        p2sigma = limits[i][4]
        obsLim  = limits[i][5]


        #Interpolation
        splineType     = "quadratic"
        myPtsSmooth    = np.linspace(myPts[0],myPts[-1],1000,dtype="float64")
        m2sigmaSmooth  = interp1d(myPts, np.log(m2sigma), kind=splineType)
        m1sigmaSmooth  = interp1d(myPts, np.log(m1sigma), kind=splineType)
        medianSmooth   = interp1d(myPts, np.log(median), kind=splineType)
        p1sigmaSmooth  = interp1d(myPts, np.log(p1sigma), kind=splineType)
        p2sigmaSmooth  = interp1d(myPts, np.log(p2sigma), kind=splineType)
        obsLimSmooth   = interp1d(myPts, np.log(obsLim), kind=splineType)


        if(smooth):
            plt.fill_between(myPtsSmooth, np.exp(m1sigmaSmooth(myPtsSmooth)), np.exp(p1sigmaSmooth(myPtsSmooth)), color='forestgreen', label='_nolegend_')
            plt.fill_between(myPtsSmooth, np.exp(m2sigmaSmooth(myPtsSmooth)), np.exp(p2sigmaSmooth(myPtsSmooth)), color='darkorange',  label='_nolegend_')
            plt.fill_between(myPtsSmooth, np.exp(m1sigmaSmooth(myPtsSmooth)), np.exp(p1sigmaSmooth(myPtsSmooth)), color='forestgreen', label='_nolegend_')
            plt.plot(myPtsSmooth, np.exp(medianSmooth(myPtsSmooth)), color='black', linewidth='2.4', linestyle='--', label='_nolegend_')
            
            #Point original (unsmoothed) points
            plt.scatter(myPts, median, color='black', linewidth='2.4', marker='o', label='_nolegend_')
            plt.scatter(myPts, obsLim, color='black', linewidth='2.4', marker='o', label='_nolegend_')

            minMedianIdx = np.argmin(medianSmooth(myPtsSmooth))
            minMY = myPtsSmooth[minMedianIdx]

            print("Minimum of ", MX[i],minMY)
            if(obs):
                plt.plot(myPtsSmooth, np.exp(obsLimSmooth(myPtsSmooth)), color='black', linewidth='2.4', linestyle='-', label='_nolegend_')            
        else:
            plt.fill_between(myPts, m1sigma, p1sigma, color='forestgreen', label='_nolegend_')
            plt.fill_between(myPts, m2sigma, p2sigma, color='darkorange',  label='_nolegend_')
            plt.fill_between(myPts, m1sigma, p1sigma, color='forestgreen', label='_nolegend_')
            plt.plot(myPts, median, color='black', linewidth='2.4', linestyle='--', label='_nolegend_')
            if(obs):
                plt.plot(myPts, obsLim, color='black', linewidth='2.4', linestyle='-', label='_nolegend_')

        if(xsecs):
            lastMY = goodMY[i][-1]
            theory_x, theory_y = list(zip(*theoryLines[i]))
            theory_cutoffIdx = theoryCutoff(lastMY,theory_x)
            plt.plot(theory_x[:theory_cutoffIdx], theory_y[:theory_cutoffIdx], color='red', linewidth='2.4', linestyle='-', label=r'NMSSM maximum cross-section')


        plt.text(420, 0.15, r'$M_{X} = '+str(MX[i])+r'\,GeV$')
        plt.yscale('log')
        axs[i].set_ylim(0.02,500)
        axs[i].tick_params(axis='y', which='minor', direction='in')
        axs[i].yaxis.set_minor_locator(AutoMinorLocator())
        axs[i].minorticks_on()

        if(i==0):
            plt.legend(loc=4)

    plt.xlabel("$M_{Y} [GeV]$", horizontalalignment='right', x=1.0)




    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(6*2.5, (2*len(MY))*1.5, forward=True)
    #fig.text(0.03, 0.5, r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$', va="center", rotation='vertical',fontsize=50)
    fig.text(0.03, 0.5, r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$', va="center", rotation='vertical')
    
    fig.savefig(outputFile+".png")
    fig.savefig(outputFile+".pdf")
    plt.clf()


#mxLimits(my=125,obs=True)

xsecs = readXsecs("NMSSM_xsecs.csv",scale=1)
#multipleMY([60,90,125,200,300,450,600],obs=True,xsecs=xsecs,outputFile="limitPlots/obslim_2D_slices")
multipleMY([60,90,125,200,300,450,600],obs=True,xsecs=xsecs,outputFile="limitPlots/obslim_2D_slices_smooth",smooth=True)

#multipleMX([900,1200,1600,2000,2600,3000],obs=True,xsecs=xsecs)
multipleMX([900,1200,1600,2000,2600,3000],obs=True,xsecs=xsecs,smooth=True,outputFile="limitPlots/obslim_2D_slices_MX_smooth")
