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

matplotlib.use('Agg')

def getLimits(rootFile):
    f = r.TFile.Open(rootFile)
    limitTree = f.Get("limit")
    limits = []
    for limit in limitTree:
        #limits.append(limit.limit*0.5)#signal is normalized to 0.5fb xsec
        limits.append(limit.limit*1.0)#signal is normalized to 1.0fb xsec

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


def deltaEtaLimits():
    colors = ["blue","orange","black","green","red","purple"]
    for i,my in enumerate([100,125,200]):
        MX = [1000,1200,1400,1600,1800,2000]
        limitsDEta = []
        limitsNoDEta = []
        goodMX = []
        for mx in MX:
            fileDEta = "limits/noDeltaEta/limits_MX{0}_MY{1}.AsymptoticLimits.mH125.root".format(mx,my)
            fileNoDEta = "limits/DeltaEta/limits_MX{0}_MY{1}.AsymptoticLimits.mH125.root".format(mx,my)
            if not (checkLimitFile(fileDEta) and checkLimitFile(fileNoDEta)):
                continue
            goodMX.append(mx)
            limitsDEta.append(getLimits(fileDEta))
            limitsNoDEta.append(getLimits(fileNoDEta))


        limitsDEta = np.array(limitsDEta)*(10.**i)#Multiplying by 10. so we can show multiple limits on same canvas
        limitsNoDEta = np.array(limitsNoDEta)*(10.**i)#Multiplying by 10. so we can show multiple limits on same canvas
        #transpose so that:
        #limitsDEta[2][:] corresponds to exp limits
        #limitsDEta[1][:] corresponds to exp 68% limits low
        #limitsDEta[0][:] corresponds to exp 95% limits low
        #limitsDEta[3][:] corresponds to exp 68% limits up
        #limitsDEta[4][:] corresponds to exp 95% limits up
        limitsDEta = limitsDEta.T.tolist() 
        limitsNoDEta = limitsNoDEta.T.tolist()

        plt.style.use(hep.style.CMS)
        hep.cms.label(loc=1, year='138 $fb^{-1}$', paper=True, llabel='Simulation WiP')
        plt.plot(goodMX, limitsDEta[2], color=colors[i], linewidth='2.4', linestyle='--', label=r'MY{0}: $\Delta\eta$ cut (x$10^{1})$'.format(my,i))
        plt.plot(goodMX, limitsNoDEta[2], color=colors[-1-i], linewidth='2.4', linestyle='--', label=r'MY{0}: No $\Delta\eta$ cut (x$10^{1})$'.format(my,i))

        #plt.text(800, 100, r'$M_{Y} = 125\,GeV$')
    plt.yscale('log')
    plt.ylim(0.01, 1000000)
    plt.legend(loc=(0.10,0.55)
      , title='95% CL upper limits'
      ,ncol=2
      ,title_fontsize=17
      ,fontsize=17
      )
    plt.ylabel(r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$',horizontalalignment='right', y=1.0)
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
    plt.tight_layout()

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(4*2.5, 3*2.5, forward=True)

    fig.savefig('DeltaEta_limits.pdf')


def wpStudyLimits():
    colors_p9_p94 = ["lightcoral","indianred","brown","firebrick","red"]
    colors_p9_p98 = ["forestgreen","limegreen","darkgreen","green","lime"]
    colors_p94_p98 = ["blue","skyblue","dodgerblue","royalblue","navy"]
    for i,my in enumerate([100,125,200,300,400]):
        MX = [1000,1200,1400,1600,1800,2000]
        limits_p9_p94  = []
        limits_p9_p98  = []
        limits_p94_p98 = []
        goodMX         = []
        for mx in MX:
            file_p9_p94 =  "limits/WP_study/limits_0.9_0.94_MX{0}_MY{1}.AsymptoticLimits.mH125.root".format(mx,my)
            file_p9_p98 =  "limits/WP_study/limits_0.9_0.98_MX{0}_MY{1}.AsymptoticLimits.mH125.root".format(mx,my)
            file_p94_p98 = "limits/WP_study/limits_0.94_0.98_MX{0}_MY{1}.AsymptoticLimits.mH125.root".format(mx,my)
            if not (checkLimitFile(file_p9_p94) and checkLimitFile(file_p9_p98) and checkLimitFile(file_p94_p98)):
                continue
            goodMX.append(mx)
            limits_p9_p94.append(getLimits(file_p9_p94))
            limits_p9_p98.append(getLimits(file_p9_p98))
            limits_p94_p98.append(getLimits(file_p94_p98))


        limits_p9_p94 = np.array(limits_p9_p94)*(10.**i)#Multiplying by 10. so we can show multiple limits on same canvas
        limits_p9_p98 = np.array(limits_p9_p98)*(10.**i)#Multiplying by 10. so we can show multiple limits on same canvas
        limits_p94_p98 = np.array(limits_p94_p98)*(10.**i)#Multiplying by 10. so we can show multiple limits on same canvas
        #transpose so that:
        #limitsDEta[2][:] corresponds to exp limits
        #limitsDEta[1][:] corresponds to exp 68% limits low
        #limitsDEta[0][:] corresponds to exp 95% limits low
        #limitsDEta[3][:] corresponds to exp 68% limits up
        #limitsDEta[4][:] corresponds to exp 95% limits up
        limits_p9_p94 = limits_p9_p94.T.tolist() 
        limits_p9_p98 = limits_p9_p98.T.tolist()    
        limits_p94_p98 = limits_p94_p98.T.tolist()

        plt.style.use(hep.style.CMS)
        hep.cms.label(loc=1, year='35.9 $fb^{-1}$', paper=True, llabel='Simulation WiP')
        plt.plot(goodMX, limits_p9_p94[2], color=colors_p9_p94[i], linewidth='2.4', linestyle='--', label=r'Y{0}:0.9 0.94(x$10^{1})$'.format(my,i))
        plt.plot(goodMX, limits_p9_p98[2], color=colors_p9_p98[i], linewidth='2.4', linestyle='--', label=r'Y{0}:0.9 0.98(x$10^{1})$'.format(my,i))
        plt.plot(goodMX, limits_p94_p98[2], color=colors_p94_p98[i], linewidth='2.4', linestyle='--', label=r'Y{0}:0.94 0.98(x$10^{1})$'.format(my,i))
    
    plt.ylabel(r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$',horizontalalignment='right', y=1.0)
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)
      
        #plt.text(800, 100, r'$M_{Y} = 125\,GeV$')
    plt.yscale('log')
    plt.ylim(0.01, 10**16)
    plt.legend(loc=(0.05,0.50)
      , title='95% CL upper limits'
      ,ncol=3
      ,title_fontsize=15
      ,fontsize=13
      )


    plt.tight_layout()

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(4*2.5, 3*2.5, forward=True)

    fig.savefig('wp_study.pdf')

def mxLimits(my=125,obs=False):
    MX = [900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
    #MX = [1000,1200,1400,1600,1800,2000,2200,2800,3000]
    limits = []
    goodMX = []
    for mx in MX:
        #file_limits = "limits/obsLimits_snapshot/MX{0}_MY{1}.root".format(int(mx),int(my))
        #file_limits = "limits/obsLimits/MX{0}_MY{1}.root".format(int(mx),int(my))
        file_limits = "limits/obsLimits_1fb_signal/MX{0}_MY{1}.root".format(int(mx),int(my))
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
    #print(limits)
    limits = limits.T.tolist() 

    plt.style.use(hep.style.CMS)
    hep.cms.label(loc=1, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')

    plt.fill_between(goodMX, limits[1], limits[3], color='forestgreen', label='68% expected')
    plt.fill_between(goodMX, limits[0], limits[4], color='darkorange', label='95% expected')
    plt.fill_between(goodMX, limits[1], limits[3], color='forestgreen', label='_nolegend_')
    print(goodMX,limits[5])
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
        fig.savefig('obslim_MX_MY{0}_1.0.pdf'.format(my))
        fig.savefig('obslim_MX_MY{0}_1.0.png'.format(my))
    else:
        fig.savefig('explim_MX_MY{0}_1.0.pdf'.format(my))
        fig.savefig('explim_MX_MY{0}_1.0.png'.format(my))
    plt.clf()


def multipleMY(MY,obs=False):
    MX = [900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
    limits = []#MY,significance,MX
    goodMX = []#MY, good MX
    for my in MY:
        tempLimits = []
        tempMX     = []
        for mx in MX:
            if(obs):
                file_limits = "limits/obsLimits//MX{0}_MY{1}.root".format(int(mx),int(my))
            else:
                file_limits = "limits/toyLimits//MX{0}_MY{1}.root".format(int(mx),int(my))                
            if not (checkLimitFile(file_limits)):
                continue
            expLimits = getLimits(file_limits)
            if not expLimits:
                print("rm -f {0}".format(file_limits))
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
    f, axs = plt.subplots(len(MY),1, sharex=True, sharey=False,gridspec_kw={'hspace': 0.03})
    plt.subplots_adjust(top=0.95, bottom=0.05)
    for i in range(len(MY)):
        plt.sca(axs[i])
        if(i==0):
            hep.cms.label(loc=1, year='138 $fb^{-1}$', paper=True, llabel='Preliminary')
        plt.fill_between(goodMX[i], limits[i][1], limits[i][3], color='forestgreen', label='68% expected')
        plt.fill_between(goodMX[i], limits[i][0], limits[i][4], color='darkorange',  label='95% expected')
        plt.fill_between(goodMX[i], limits[i][1], limits[i][3], color='forestgreen', label='_nolegend_')
        plt.plot(goodMX[i], limits[i][2], color='black', linewidth='2.4', linestyle='--', label=r'Median expected')
        if(obs):
            plt.plot(goodMX[i], limits[i][5], color='black', linewidth='2.4', linestyle='-', label=r'Observed')
        plt.text(3000, 10, r'$M_{Y} = '+str(MY[i])+r'\,GeV$')
        plt.yscale('log')
        axs[i].set_ylim(0.03,100)
        axs[i].tick_params(axis='y', which='minor', direction='in')
        axs[i].yaxis.set_minor_locator(AutoMinorLocator())
        axs[i].minorticks_on()
    plt.xlabel("$M_{X} [GeV]$", horizontalalignment='right', x=1.0)


    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(6*2.5, (2*len(MY))*2.0, forward=True)
    fig.text(0.03, 0.5, r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$', va="center", rotation='vertical',fontsize=50)
    if(obs):
        fig.savefig('obslim_2D_slices.png')
        fig.savefig('obslim_2D_slices.pdf')
    else:
        fig.savefig('explim_2D_slices.png')
        fig.savefig('explim_2D_slices.pdf')
    plt.clf()




#deltaEtaLimits()
#wpStudyLimits()

#multipleMY([60,90,125,200,300,450,600])
mxLimits(obs=True)
#mxLimits(my=90,obs=True)
#mxLimits(my=80,obs=True)
#multipleMY([60,90,125,200,300,450,600],obs=True)
