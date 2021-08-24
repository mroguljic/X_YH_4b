#
# Simple script to produce the performance plots
#

from array import array
from ROOT import *
import numpy as np

import matplotlib.pyplot as plt

import mplhep as hep
import matplotlib
matplotlib.use('Agg')

#---------------------------------------------------------------------
# to run in the batch mode (to prevent canvases from popping up)
gROOT.SetBatch()

# set plot style
gROOT.SetStyle("Plain")

# suppress the statistics box
gStyle.SetOptStat(0)

# suppress the histogram title
gStyle.SetOptTitle(0)

# adjust margins
gStyle.SetPadLeftMargin(0.14)
gStyle.SetPadRightMargin(0.06)

# set grid color to gray
gStyle.SetGridColor(kGray)

gStyle.SetPadTickX(1)  # to get the tick marks on the opposite side of the frame
gStyle.SetPadTickY(1)  # to get the tick marks on the opposite side of the frame

# set nicer fonts
gStyle.SetTitleFont(42, "XYZ")
gStyle.SetLabelFont(42, "XYZ")
#---------------------------------------------------------------------

def makeEffVsMistagTGraph(histo_b,histo_nonb,allowNegative):

    firstbin = histo_b.GetXaxis().FindBin(0.) - 1
    if allowNegative: firstbin = -1
    lastbin = histo_b.GetXaxis().GetNbins() + 1 # '+ 1' to also include any entries in the overflow bin

    b_eff = array('f')
    nonb_eff = array('f')
    tot_b= histo_b.Integral(firstbin,lastbin)
    tot_nonb= histo_nonb.Integral(firstbin,lastbin)

    print("Total number of jets:")
    print(tot_b,"b jets")
    print(tot_nonb,"non-b jets")

    b_abovecut = 0
    nonb_abovecut = 0

    wpT = (0.,0.)
    wpM = (0.,0.)
    wpL = (0.,0.)

    for i in range(lastbin,firstbin,-1) : # from 'overflow' bin to 0, in steps of "-1"
        b_abovecut += histo_b.GetBinContent(i)
        nonb_abovecut += histo_nonb.GetBinContent(i)
        b_eff.append(b_abovecut/tot_b)
        nonb_eff.append(nonb_abovecut/tot_nonb)
        if(histo_b.GetBinCenter(i)<0.99 and histo_b.GetBinCenter(i)>0.97):
            wpT = b_eff[-1],nonb_eff[-1]
        if(histo_b.GetBinCenter(i)<0.95 and histo_b.GetBinCenter(i)>0.93):
            wpM = b_eff[-1],nonb_eff[-1]
        if(histo_b.GetBinCenter(i)<0.91 and histo_b.GetBinCenter(i)>0.89):
            wpL = b_eff[-1],nonb_eff[-1]
        #print(b_eff[-1],nonb_eff[-1],histo_b.GetBinCenter(i),histo_nonb.GetBinCenter(i))

    return TGraph(len(b_eff), b_eff, nonb_eff), b_eff, nonb_eff, wpT, wpM, wpL

def effVsPt(histo,outputFile):
    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots()
    signalFlag = False  
    if("MX" in histo.GetName()):
        signalFlag = True
    if(signalFlag):
        axs.set_ylim([0.0,1])
        yTitle = "Signal efficiency"
    else:
        yTitle = "Mistag rate"

    effsT = []
    effsL = []
    pTs   = np.arange(450,1550,100)
    for i in range(46,156,10):
        passT = histo.Integral(99,100,i,i+9)
        passL = histo.Integral(95,98,i,i+9)
        total = histo.Integral(1,100,i,i+9)
        effT  = passT/total
        effL  = passL/total
        effsT.append(effT)
        effsL.append(effL)

    plt.xlabel("Y-jet $p_{T}$", horizontalalignment='right', x=1.0)
    plt.ylabel("Signal efficiency",horizontalalignment='right', y=1.0)
    plt.grid(which='both')
    plt.plot(pTs,effsT,color="red",label="Tight (PNet>0.98)")
    plt.plot(pTs,effsL,color="blue",label="Loose (0.94<PNet<0.98)")

    axs.legend()

    plt.grid(b=True,which='both',axis="both")

    plt.savefig(outputFile,bbox_inches='tight')


def main():
    # input file
    #for year in ["16","17","18"]:
    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots()
    axs.set_ylim([3*10e-4,1])
    colors = [["b","k"],["r","g"],["orange","gold"]]
    for i,year in enumerate(["16","17"]):
        sigFile = TFile.Open("results/templates_hadronic/20{0}/scaled/MX1600_MY125.root".format(year))
        bkgFile = TFile.Open("results/templates_hadronic/20{0}/scaled/QCD{0}.root".format(year))
        ttbarFile = TFile.Open("results/templates_hadronic/20{0}/scaled/TTbar{0}.root".format(year))

        # if(i==1):#plot EOY ROC 
        #     sigFile = TFile.Open("~/X_YH_4b/results/templates/WP_0.8_0.95/20{0}/scaled/MX1600_MY125.root".format(year))
        #     bkgFile = TFile.Open("~/X_YH_4b/results/templates/WP_0.8_0.95/20{0}/scaled/QCD{0}.root".format(year))
        #     ttbarFile = TFile.Open("~/X_YH_4b/results/templates/WP_0.8_0.95/20{0}/scaled/TTbar{0}.root".format(year))


        legend = ["Signal vs QCD {0}".format(year), "Signal vs ttbar {0}".format(year)]
        graphs = []

        h_sig_pnet = sigFile.Get("MX1600_MY125_pnet_pT_Y_nom").ProjectionX()
        h_sig_pnet.SetDirectory(0)
        h_bkg_pnet = bkgFile.Get("QCD_pnet_pT_Y_nom").ProjectionX()
        h_tt_pnet = ttbarFile.Get("TTbar_pnet_pT_Y_nom").ProjectionX()
        allowNegative = False
        # get eff vs mistag rate graph
        gVsQCD, effVsSig, mistagVsQCD, wpTVsQCD,wpMVsQCD,wpLVsQCD = makeEffVsMistagTGraph(h_sig_pnet,h_bkg_pnet,allowNegative)
        graphs.append(gVsQCD)
        gVsTT, effVsTT, mistagVsTT, wpTVsTT,wpMVsTT,wpLVsTT = makeEffVsMistagTGraph(h_sig_pnet,h_tt_pnet,allowNegative)
        graphs.append(gVsTT)
        # get eff vs mistag rate graph
        effVsSig = np.asarray(effVsSig)
        mistagVsQCD = np.asarray(mistagVsQCD)
        effVsTT = np.asarray(effVsTT)
        mistagVsTT = np.asarray(mistagVsTT)
         

        plt.yscale("log")
        plt.xlabel("Signal efficiency", horizontalalignment='right', x=1.0)
        plt.ylabel("Mistag rate",horizontalalignment='right', y=1.0)
        plt.grid(which='both')
        print([wpTVsQCD[0],wpTVsTT[0]], [wpTVsQCD[1],wpTVsTT[1]])
        print([wpLVsQCD[0],wpLVsTT[0]], [wpLVsQCD[1],wpLVsTT[1]])
        # if(i==1):
        #     plt.plot(effVsSig,mistagVsQCD,lineStyle="-" ,color=colors[i][0],label="EOY signal vs QCD 20{0}".format(year))
        #     plt.plot(effVsTT,mistagVsTT,lineStyle="-",color=colors[i][1], label=r"EOY signal vs $t\bar{t}$"+" 20{0}".format(year))          
        # else:
        #     plt.plot(effVsSig,mistagVsQCD,lineStyle="-" ,color=colors[i][0],label="UL signal vs QCD 20{0}".format(year))
        #     plt.plot(effVsTT,mistagVsTT,lineStyle="-",color=colors[i][1], label=r"UL signal vs $t\bar{t}$"+" 20{0}".format(year))
        plt.plot(effVsSig,mistagVsQCD,lineStyle="-" ,color=colors[i][0],label="Signal vs QCD 20{0}".format(year))
        plt.plot(effVsTT,mistagVsTT,lineStyle="-",color=colors[i][1], label=r"Signal vs $t\bar{t}$"+" 20{0}".format(year))
        if(i==0):
            labelT = "WP = 0.98"
            labelM = "WP = 0.94"
            labelL = "WP = 0.9"
        else:
            labelT = '_nolegend_'
            labelM = '_nolegend_'
            labelL = '_nolegend_'
        plt.plot([wpTVsQCD[0],wpTVsTT[0]], [wpTVsQCD[1],wpTVsTT[1]], marker='o', markersize=7, color="red",label=labelT,linewidth=0)
        plt.plot([wpMVsQCD[0],wpMVsTT[0]], [wpMVsQCD[1],wpMVsTT[1]], marker='o', markersize=7, color="gold",label=labelM,linewidth=0)
        plt.plot([wpLVsQCD[0],wpLVsTT[0]], [wpLVsQCD[1],wpLVsTT[1]], marker='o', markersize=7, color="green",label=labelL,linewidth=0)
    axs.legend()
    plt.grid(b=True,which='both',axis="both")
    plt.savefig("ROC.pdf")
    plt.savefig("ROC.png")
if __name__ == '__main__':
    #main()

    f = TFile.Open("results/templates_hadronic/2017/scaled/MX3000_MY125.root")
    h = f.Get("MX3000_MY125_pnet_pT_Y_nom")
    effVsPt(h,"eff_pt_MX3000_MY125.png")
    f.Close()
    f = TFile.Open("results/templates_hadronic/2017/scaled/QCD17.root")
    h = f.Get("QCD_pnet_pT_Y_nom")
    effVsPt(h,"eff_pt_QCD.png")
    f.Close()
    f = TFile.Open("results/templates_hadronic/2017/scaled/TTbar17.root")
    h = f.Get("TTbar_pnet_pT_Y_nom")
    effVsPt(h,"eff_pt_TTbar.png")
    f.Close()