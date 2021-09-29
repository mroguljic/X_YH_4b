import matplotlib
matplotlib.use('Agg')

import ROOT as r
import numpy as np
#r.gStyle.SetErrorX(0)
r.gStyle.SetOptStat(0000)
from root_numpy import hist2array
import matplotlib.pyplot as plt
import mplhep as hep


def createCanvasPads():
    c = r.TCanvas("c", "canvas", 4000, 1500)
    # Upper histogram plot is pad1
    pad1 = r.TPad("pad1", "pad1", 0, 0.4, 0.5, 1.0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    pad1.SetGridx()
    pad1.Draw()
    # Lower ratio plot is pad2
    c.cd()  # returns to main canvas before defining pad2
    pad2 = r.TPad("pad2", "pad2", 0, 0.1, 0.5, 0.4)
    pad2.SetTopMargin(0)  # joins upper and lower plot
    pad2.SetBottomMargin(0.3)
    pad2.SetGridx()
    pad2.Draw()

    c.cd()
    pad3 = r.TPad("pad3", "pad3", 0.5, 0.4, 1, 1.0)
    pad3.SetBottomMargin(0)  # joins upper and lower plot
    pad3.SetGridx()
    pad3.Draw()

    c.cd() 
    pad4 = r.TPad("pad4", "pad4", 0.5, 0.1, 1, 0.4)
    pad4.SetTopMargin(0)  # joins upper and lower plot
    pad4.SetBottomMargin(0.3)
    pad4.SetGridx()
    pad4.Draw() 
    return c, pad1, pad2, pad3, pad4

def createRatio(h1, h2):
    h3 = h1.Clone("h3")
    h3.SetLineColor(r.kBlack)
    h3.SetMarkerStyle(21)
    h3.SetTitle("")
    h3.SetMinimum(0.45)
    h3.SetMaximum(1.55)
    # Set up plot for markers and errors
    h3.Sumw2()
    h3.SetStats(0)
    h3.Divide(h2)
 
    # Adjust y-axis settings
    y = h3.GetYaxis()
    y.SetTitle("Ratio pass / fail ")
    y.SetNdivisions(10)
    y.SetTitleSize(30)
    y.SetTitleFont(43)
    y.SetTitleOffset(1.55)
    y.SetLabelFont(43)
    y.SetLabelSize(30)
 
    # Adjust x-axis settings
    x = h3.GetXaxis()
    x.SetTitleSize(0.11)
    #x.SetTitleFont(62)
    x.SetTitleOffset(1.2)
    x.SetLabelFont(48)
    x.SetLabelSize(54)
 
    return h3


def histToScatter(h):
    xVals  = []
    yVals  = []
    errors = []

    for i in range(1,h.GetNbinsX()+1):
        yVals.append(h.GetBinContent(i))
        xVals.append(h.GetBinCenter(i))
        errors.append(h.GetBinError(i))

    xVals=np.asarray(xVals)
    yVals=np.asarray(yVals)
    errors=np.asarray(errors)

    return xVals,yVals,errors   


def compareShapes(hFail,hPass,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=False,label1="",label2="",labelR="Data/MC",data=False,text="",year=""):
    hRpf_mj = createRatio(hPass,hFail)
    hRatioCentres, hRatio, hRatioErrors = histToScatter(hRpf_mj)


    #numpy histograms
    hPassErrs         = histToScatter(hPass)[2]
    hFailErrs         = histToScatter(hFail)[2]
    hFail, hFailEdges = hist2array(hFail,return_edges=True)
    hPass, hPassEdges = hist2array(hPass,return_edges=True)

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    if(log):
        axs[0].set_yscale("log")
    hep.histplot(hFail,hFailEdges[0],stack=False,ax=axs[0],label = label1, histtype="step",color="r",yerr=hFailErrs)
    hep.histplot(hPass,hFailEdges[0],stack=False,ax=axs[0],label = label2, histtype="step",color="g",yerr=hPassErrs)
    if(text):
        plt.text(0.75, 0.75, text, horizontalalignment='center',verticalalignment='center',transform=axs[0].transAxes, fontsize=18)

    plt.ylabel(yTitle, horizontalalignment='right', y=1.0)
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    #axs[0].set_ylabel(yTitle)
    axs[1].set_ylabel(labelR)
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)

    hep.cms.lumitext(text=year, ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc="best")#loc = (0.4,0.2))

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.0,2.0])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    plt.errorbar(hRatioCentres,hRatio, yerr=hRatioErrors, fmt='o',color="k")    

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)


# wps = [0.8,0.95]


# for year in ["16","17","18"]:
#     for sample in ["QCD","TTbar"]:
#         f           = r.TFile.Open("results/templates/WP_{0}_{1}//20{2}/scaled/{3}{2}.root".format(wps[0],wps[1],year,sample))
#         h2d_TT      = f.Get("{0}_mJY_mJJ_TT_nom".format(sample))
#         h2d_LL      = f.Get("{0}_mJY_mJJ_LL_nom".format(sample))
#         h2d_L_AL    = f.Get("{0}_mJY_mJJ_L_AL_nom".format(sample))
#         h2d_T_AL    = f.Get("{0}_mJY_mJJ_T_AL_nom".format(sample))

#         hMJJ_TT     = h2d_TT.ProjectionY("hMJJ_TT",1,-1)#avoid underflow
#         hMJJ_LL     = h2d_LL.ProjectionY("hMJJ_LL",1,-1)#avoid underflow
#         hMJJ_L_AL   = h2d_L_AL.ProjectionY("hMJJ_L_AL",1,-1)#avoid underflow
#         hMJJ_T_AL   = h2d_T_AL.ProjectionY("hMJJ_T_AL",1,-1)#avoid underflow
#         hMJY_TT     = h2d_TT.ProjectionX("hMJY_TT",1,-1)#avoid underflow
#         hMJY_LL     = h2d_LL.ProjectionX("hMJY_LL",1,-1)#avoid underflow
#         hMJY_L_AL   = h2d_L_AL.ProjectionX("hMJY_L_AL",1,-1)#avoid underflow
#         hMJY_T_AL   = h2d_L_AL.ProjectionX("hMJY_T_AL",1,-1)#avoid underflow


#         hMJJ_TT.Scale(1/hMJJ_TT.Integral())
#         hMJJ_LL.Scale(1/hMJJ_LL.Integral())
#         hMJJ_L_AL.Scale(1/hMJJ_L_AL.Integral())
#         hMJJ_T_AL.Scale(1/hMJJ_T_AL.Integral())
#         hMJY_TT.Scale(1/hMJY_TT.Integral())
#         hMJY_LL.Scale(1/hMJY_LL.Integral())
#         hMJY_L_AL.Scale(1/hMJY_L_AL.Integral())
#         hMJY_T_AL.Scale(1/hMJY_T_AL.Integral())

#         compareShapes(hMJJ_T_AL,hMJJ_TT,"MJJ_TT_{0}_{1}.pdf".format(year,sample),xTitle="$M_{JJ}$ [GeV]",yTitle="Event fraction/100GeV",label1="T_AL",label2="TT",labelR="TT/T_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="{0}\nWPs = {1}, {2}".format(sample, wps[0],wps[1]),year="20{0}".format(year))
#         compareShapes(hMJJ_L_AL,hMJJ_LL,"MJJ_LL_{0}_{1}.pdf".format(year,sample),xTitle="$M_{JJ}$ [GeV]",yTitle="Event fraction/100GeV",label1="L_AL",label2="LL",labelR="LL/L_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="{0}\nWPs = {1}, {2}".format(sample, wps[0],wps[1]),year="20{0}".format(year))

#         compareShapes(hMJY_T_AL,hMJY_TT,"MJY_TT_{0}_{1}.pdf".format(year,sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="T_AL",label2="TT",labelR="TT/T_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="{0}\nWPs = {1}, {2}".format(sample, wps[0],wps[1]),year="20{0}".format(year))
#         compareShapes(hMJY_L_AL,hMJY_LL,"MJY_LL_{0}_{1}.pdf".format(year,sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="L_AL",label2="LL",labelR="LL/L_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="{0}\nWPs = {1}, {2}".format(sample, wps[0],wps[1]),year="20{0}".format(year))

#Requested by C.Mantilla
# wps = [0.94,0.98]
# for sample in ["QCD"]:
#     f           = r.TFile.Open("/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/RunII/QCD.root")
#     h2d_TT      = f.Get("{0}_mJY_mJJ_TT_nom".format(sample))
#     h2d_LL      = f.Get("{0}_mJY_mJJ_LL_nom".format(sample))
#     h2d_L_AL    = f.Get("{0}_mJY_mJJ_L_AL_nom".format(sample))
#     h2d_T_AL    = f.Get("{0}_mJY_mJJ_T_AL_nom".format(sample))
#     h2d_NAL_L    = f.Get("{0}_mJY_mJJ_NAL_L_nom".format(sample))
#     h2d_NAL_T    = f.Get("{0}_mJY_mJJ_NAL_T_nom".format(sample))
#     h2d_NAL_AL    = f.Get("{0}_mJY_mJJ_NAL_AL_nom".format(sample))
#     h2d_WAL_L    = f.Get("{0}_mJY_mJJ_NAL_L_nom".format(sample))
#     h2d_WAL_T    = f.Get("{0}_mJY_mJJ_NAL_T_nom".format(sample))
#     h2d_WAL_AL    = f.Get("{0}_mJY_mJJ_NAL_AL_nom".format(sample))


#     hMJY_TT     = h2d_TT.ProjectionX("hMJY_TT",1,-1)#avoid underflow
#     hMJY_LL     = h2d_LL.ProjectionX("hMJY_LL",1,-1)#avoid underflow
#     hMJY_L_AL   = h2d_L_AL.ProjectionX("hMJY_L_AL",1,-1)#avoid underflow
#     hMJY_T_AL   = h2d_L_AL.ProjectionX("hMJY_T_AL",1,-1)#avoid underflow
#     hMJY_NAL_L  = h2d_NAL_L.ProjectionX("hMJY_NAL_L",1,-1)#avoid underflow
#     hMJY_NAL_T  = h2d_NAL_T.ProjectionX("hMJY_NAL_T",1,-1)#avoid underflow
#     hMJY_NAL_AL = h2d_NAL_AL.ProjectionX("hMJY_NAL_AL",1,-1)#avoid underflow
#     hMJY_WAL_L  = h2d_WAL_L.ProjectionX("hMJY_WAL_L",1,-1)#avoid underflow
#     hMJY_WAL_T  = h2d_WAL_T.ProjectionX("hMJY_WAL_T",1,-1)#avoid underflow
#     hMJY_WAL_AL = h2d_WAL_AL.ProjectionX("hMJY_WAL_AL",1,-1)#avoid underflow

#     hMJY_TT.Scale(1/hMJY_TT.Integral())
#     hMJY_LL.Scale(1/hMJY_LL.Integral())
#     hMJY_L_AL.Scale(1/hMJY_L_AL.Integral())
#     hMJY_T_AL.Scale(1/hMJY_T_AL.Integral())
#     hMJY_NAL_L.Scale(1/hMJY_NAL_L.Integral())
#     hMJY_NAL_T.Scale(1/hMJY_NAL_T.Integral())
#     hMJY_NAL_AL.Scale(1/hMJY_NAL_AL.Integral())
#     hMJY_WAL_L.Scale(1/hMJY_WAL_L.Integral())
#     hMJY_WAL_T.Scale(1/hMJY_WAL_T.Integral())
#     hMJY_WAL_AL.Scale(1/hMJY_WAL_AL.Integral())

#     compareShapes(hMJY_T_AL,hMJY_TT,"MJY_TT_{0}.pdf".format(sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="T_AL",label2="TT",labelR="TT/T_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="",year="137 fb^{-1}")
#     compareShapes(hMJY_L_AL,hMJY_LL,"MJY_LL_{0}.pdf".format(sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="L_AL",label2="LL",labelR="LL/L_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="",year="137 fb^{-1}")
#     compareShapes(hMJY_NAL_AL,hMJY_NAL_L,"MJY_NAL_L_{0}.pdf".format(sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="NAL_AL",label2="NAL_L",labelR="NAL_L/NAL_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="",year="137 fb^{-1}")
#     compareShapes(hMJY_NAL_AL,hMJY_NAL_T,"MJY_NAL_T_{0}.pdf".format(sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="NAL_AL",label2="NAL_T",labelR="NAL_T/NAL_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="",year="137 fb^{-1}")
#     compareShapes(hMJY_WAL_AL,hMJY_WAL_L,"MJY_WAL_L_{0}.pdf".format(sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="WAL_AL",label2="WAL_L",labelR="WAL_L/WAL_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="",year="137 fb^{-1}")
#     compareShapes(hMJY_WAL_AL,hMJY_WAL_T,"MJY_WAL_T_{0}.pdf".format(sample),xTitle="$M_{JY}$ [GeV]",yTitle="Event fraction/20GeV",label1="WAL_AL",label2="WAL_T",labelR="WAL_T/WAL_AL",yRange=[0,0.7],xRange=[],log=False,data=False,text="",year="137 fb^{-1}")


#Semiresolved
wps = [0.94,0.98]
for sample in ["QCD"]:
    f           = r.TFile.Open("results/semiResolvedSelection/2017/scaled/{0}17.root".format(sample))
    h2d_TT      = f.Get("{0}_mJY_mJJ_TT".format(sample))
    h2d_LL      = f.Get("{0}_mJY_mJJ_LL".format(sample))
    h2d_L_AL    = f.Get("{0}_mJY_mJJ_L_AL".format(sample))

    hMJY_TT     = h2d_TT.ProjectionX("hMJY_TT",1,-1)#avoid underflow
    hMJY_LL     = h2d_LL.ProjectionX("hMJY_LL",1,-1)#avoid underflow
    hMJY_L_AL   = h2d_L_AL.ProjectionX("hMJY_L_AL",1,-1)#avoid underflow

    hMJJ_TT     = h2d_TT.ProjectionY("hMJJ_TT",1,-1)#avoid underflow
    hMJJ_LL     = h2d_LL.ProjectionY("hMJJ_LL",1,-1)#avoid underflow
    hMJJ_L_AL   = h2d_L_AL.ProjectionY("hMJJ_L_AL",1,-1)#avoid underflow

    hMJY_TT.Scale(1/hMJY_TT.Integral())
    hMJY_LL.Scale(1/hMJY_LL.Integral())
    hMJY_L_AL.Scale(1/hMJY_L_AL.Integral())

    hMJJ_TT.Scale(1/hMJJ_TT.Integral())
    hMJJ_LL.Scale(1/hMJJ_LL.Integral())
    hMJJ_L_AL.Scale(1/hMJJ_L_AL.Integral())


    compareShapes(hMJY_L_AL,hMJY_TT,"Mjj_TT_{0}.png".format(sample),xTitle="$M_{jj}$ [GeV]",yTitle="Event fraction/20GeV",label1="Fail",label2="Tight",labelR="Tight/Fail",yRange=[0,0.3],xRange=[],log=False,data=False,text="",year="41.5 $fb^{-1}$")
    compareShapes(hMJY_L_AL,hMJY_LL,"Mjj_LL_{0}.png".format(sample),xTitle="$M_{jj}$ [GeV]",yTitle="Event fraction/20GeV",label1="Fail",label2="Loose",labelR="Loose/Fail",yRange=[0,0.3],xRange=[],log=False,data=False,text="",year="41.5 $fb^{-1}$")

    compareShapes(hMJJ_L_AL,hMJJ_TT,"MJjj_TT_{0}.png".format(sample),xTitle="$M_{Jjj}$ [GeV]",yTitle="Event fraction/20GeV",label1="Fail",label2="Tight",labelR="Tight/Fail",yRange=[0,0.3],xRange=[],log=False,data=False,text="",year="41.5 $fb^{-1}$")
    compareShapes(hMJJ_L_AL,hMJJ_LL,"MJjj_LL_{0}.png".format(sample),xTitle="$M_{Jjj}$ [GeV]",yTitle="Event fraction/20GeV",label1="Fail",label2="Loose",labelR="Loose/Fail",yRange=[0,0.3],xRange=[],log=False,data=False,text="",year="41.5 $fb^{-1}$")
