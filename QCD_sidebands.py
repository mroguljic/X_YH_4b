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

def plotSidebandsMJJ_mpl(h_3d,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=False):
    nBinsX = h_3d.GetNbinsX()
    nBinsY = h_3d.GetNbinsY()
    nBinsZ = h_3d.GetNbinsZ()
    wp = 0.88
    point = 0.0
    taggerLowBin = h_3d.GetXaxis().FindBin(point)
    taggerHighBin = h_3d.GetXaxis().FindBin(wp) - 1
    print(point)
    print(taggerLowBin,taggerHighBin)
    h_mjj_fail = h_3d.ProjectionY("mjj_failProjection",taggerLowBin,taggerHighBin,1,nBinsZ)
    h_mjj_pass = h_3d.ProjectionY("mjj_passProjection",taggerHighBin,nBinsX,1,nBinsZ)

    h_mjj_fail.Scale(1/h_mjj_fail.Integral())
    h_mjj_pass.Scale(1/h_mjj_pass.Integral())

    h_mjj_pass.Rebin(10)
    h_mjj_fail.Rebin(10)
    hRpf_mjj = createRatio(h_mjj_pass,h_mjj_fail)
    hRatio = []
    hRatioErrors = []
    for i in range(1,hRpf_mjj.GetNbinsX()+1):
        hRatio.append(hRpf_mjj.GetBinContent(i))
        hRatioErrors.append(hRpf_mjj.GetBinError(i))
    #numpy histograms
    hMJJFail, hMJJFailEdges = hist2array(h_mjj_fail,return_edges=True)
    hMJJPass, hMJJPassEdges = hist2array(h_mjj_pass,return_edges=True)
    hRatio = np.asarray(hRatio)
    hRatioErrors = np.asarray(hRatioErrors)
    centresRatio = (hMJJPassEdges[0][:-1] + hMJJPassEdges[0][1:])/2.

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    if(log):
        axs[0].set_yscale("log")
    hep.histplot(hMJJPass,hMJJPassEdges[0],stack=False,ax=axs[0],label = "Pass", histtype="step",color="r")
    hep.histplot(hMJJFail,hMJJFailEdges[0],stack=False,ax=axs[0],label = "Fail", histtype="step",color="b")
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    axs[0].set_ylabel(yTitle)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    axs[1].set_ylabel("Data/MC")
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    hep.cms.lumitext(text='59.8 $fb^{-1} (13 TeV)$', ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc="best")#loc = (0.4,0.2))

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.0,2.0])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    plt.errorbar(centresRatio,hRatio, yerr=hRatioErrors, fmt='o',color="k")    

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)

def plotSidebandsMJY_mpl(h_3d,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=False):
    nBinsX = h_3d.GetNbinsX()
    nBinsY = h_3d.GetNbinsY()
    nBinsZ = h_3d.GetNbinsZ()
    wp = 0.88
    point = 0.0
    taggerLowBin = h_3d.GetXaxis().FindBin(point)
    taggerHighBin = h_3d.GetXaxis().FindBin(wp) - 1

    h_mj_fail  = h_3d.ProjectionZ("mj_failProjection" ,taggerLowBin,taggerHighBin,1,nBinsY)
    h_mj_pass  = h_3d.ProjectionZ("mj_passProjection" ,taggerHighBin,nBinsX,1,nBinsY)
    h_mj_fail.Scale(1/h_mj_fail.Integral())
    h_mj_pass.Scale(1/h_mj_pass.Integral())
    h_mj_pass.Rebin(2)
    h_mj_fail.Rebin(2)
    hRpf_mj = createRatio(h_mj_pass,h_mj_fail)
    hRatio = []
    hRatioErrors = []
    for i in range(1,hRpf_mj.GetNbinsX()+1):
        hRatio.append(hRpf_mj.GetBinContent(i))
        hRatioErrors.append(hRpf_mj.GetBinError(i))
    #numpy histograms
    hMJYFail, hMJYFailEdges = hist2array(h_mj_fail,return_edges=True)
    hMJYPass, hMJYPassEdges = hist2array(h_mj_pass,return_edges=True)
    hRatio = np.asarray(hRatio)
    hRatioErrors = np.asarray(hRatioErrors)
    centresRatio = (hMJYPassEdges[0][:-1] + hMJYPassEdges[0][1:])/2.

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    if(log):
        axs[0].set_yscale("log")
    hep.histplot(hMJYPass,hMJYPassEdges[0],stack=False,ax=axs[0],label = "Pass", histtype="step",color="r")
    hep.histplot(hMJYFail,hMJYFailEdges[0],stack=False,ax=axs[0],label = "Fail", histtype="step",color="b")
    axs[0].legend()
    axs[1].set_xlabel(xTitle)
    axs[0].set_ylabel(yTitle)
    axs[1].set_ylabel("Data/MC")
    plt.ylabel(yTitle, horizontalalignment='right', x=1.0)
    if(yRange):
        axs[0].set_ylim(yRange)
    if(xRange):
        axs[0].set_xlim(xRange)
    hep.cms.lumitext(text='59.8 $fb^{-1} (13 TeV)$', ax=axs[0], fontname=None, fontsize=None)
    hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc="best")#loc = (0.4,0.2))

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.0,2.0])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    plt.errorbar(centresRatio,hRatio, yerr=hRatioErrors, fmt='o',color="k")    

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)

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


def compareShapes(hFail,hPass,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=False,label1="",label2="",labelR="Data/MC",data=False,text=""):
    hRpf_mj = createRatio(hPass,hFail)
    hRatioCentres, hRatio, hRatioErrors = histToScatter(hRpf_mj)
    hPassCentres, hPass, hPassErrors = histToScatter(hPass)

    #numpy histograms
    hFail, hFailEdges = hist2array(hFail,return_edges=True)

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    if(log):
        axs[0].set_yscale("log")
    hep.histplot(hFail,hFailEdges[0],stack=False,ax=axs[0],label = label1, histtype="step",color="r")
    plt.errorbar(hPassCentres,hPass, yerr=hPassErrors, fmt='o',color="k",label = label2)
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
    if data:
        hep.cms.text("WiP",loc=1)
        hep.cms.lumitext(text='35.9 $fb^{-1} (13 TeV)$', ax=axs[0], fontname=None, fontsize=None)
    else:
        hep.cms.lumitext(text='2016', ax=axs[0], fontname=None, fontsize=None)
        hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc="best")#loc = (0.4,0.2))

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.0,2.0])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    plt.errorbar(hRatioCentres,hRatio, yerr=hRatioErrors, fmt='o',color="k")    

    print("Saving {0}".format(outFile))
    plt.savefig(outFile)

def plotSidebands(h_3d,taggerName):
    lowEdges = np.linspace(0,0.4,5)
    print(lowEdges)
    print(h_3d.Integral())
    nBinsX = h_3d.GetNbinsX()
    print(nBinsX)
    nBinsY = h_3d.GetNbinsY()
    nBinsZ = h_3d.GetNbinsZ()

    wp = 0.88
    for point in lowEdges:
        taggerLowBin = h_3d.GetXaxis().FindBin(point)
        taggerHighBin = h_3d.GetXaxis().FindBin(wp) - 1
        print(point)
        print(taggerLowBin,taggerHighBin)
        h_mjj_fail = h_3d.ProjectionY("mjj_failProjection",taggerLowBin,taggerHighBin,1,nBinsZ)
        h_mjj_pass = h_3d.ProjectionY("mjj_passProjection",taggerHighBin,nBinsX,1,nBinsZ)
        h_mj_fail  = h_3d.ProjectionZ("mj_failProjection" ,taggerLowBin,taggerHighBin,1,nBinsY)
        h_mj_pass  = h_3d.ProjectionZ("mj_passProjection" ,taggerHighBin,nBinsX,1,nBinsY)
        #print(h_mjj_fail.Integral(),h_mjj_pass.Integral())
        #print(h_mj_fail.Integral(),h_mj_pass.Integral())
        h_mjj_fail.Scale(1/h_mjj_fail.Integral())
        h_mjj_pass.Scale(1/h_mjj_pass.Integral())
        h_mj_fail.Scale(1/h_mj_fail.Integral())
        h_mj_pass.Scale(1/h_mj_pass.Integral())
        h_mjj_pass.Rebin(10)
        h_mjj_fail.Rebin(10)
        h_mj_pass.Rebin(2)
        h_mj_fail.Rebin(2)
        h_mj_pass.GetXaxis().SetRangeUser(50, 300);
        h_mjj_pass.GetXaxis().SetRangeUser(400, 2000);


        h_mj_pass.SetLineColor(r.kRed)
        h_mj_pass.SetLineWidth(2)
        h_mj_pass.SetMarkerStyle(20)
        h_mj_fail.SetLineWidth(2)
        h_mj_fail.SetMarkerStyle(21)


        h_mjj_pass.SetLineColor(r.kRed)
        h_mjj_pass.SetLineWidth(2)
        h_mjj_pass.SetMarkerStyle(20)
        h_mjj_fail.SetLineWidth(2)
        h_mjj_fail.SetMarkerStyle(21)

        hRpf_mj = createRatio(h_mj_pass,h_mj_fail)
        hRpf_mjj = createRatio(h_mjj_pass,h_mjj_fail)


        c, pad1, pad2, pad3, pad4 = createCanvasPads()
        pad1.cd()
        h_mj_pass.Draw("l")
        h_mj_fail.Draw("same")
        pad2.cd()
        hRpf_mj.Draw("ep")
        pad3.cd()
        h_mjj_pass.Draw("l")
        h_mjj_fail.Draw("same")
        pad4.cd()
        hRpf_mjj.Draw("ep")


        legend_mj = r.TLegend(0.45,0.40,0.950,0.950)
        legend_mj.SetHeader("","")
        legend_mj.AddEntry(h_mj_pass,"Normalized QCD pass, {1} > {0:.1f}".format(wp,taggerName),"l")
        legend_mj.AddEntry(h_mj_fail,"Normalized QCD fail, {0:.1f} < {2} < {1:.1f}".format(point,wp,taggerName),"l")
        legend_mj.AddEntry(hRpf_mj,"Normalized Rpf","ep")
        legend_mj.SetFillStyle(0);
        legend_mj.SetBorderSize(0);
        pad1.cd()
        legend_mj.Draw()

        legend_mjj = r.TLegend(0.45,0.40,0.950,0.950)
        legend_mjj.SetHeader("","")
        legend_mjj.AddEntry(h_mjj_pass,"Normalized QCD pass, {1} > {0:.1f}".format(wp,taggerName),"l")
        legend_mjj.AddEntry(h_mjj_fail,"Normalized QCD fail, {0:.1f} < {2} < {1:.1f}".format(point,wp,taggerName),"l")
        legend_mjj.AddEntry(hRpf_mjj,"Normalized Rpf","ep")
        legend_mjj.SetFillStyle(0);
        legend_mjj.SetBorderSize(0);
        pad3.cd()
        legend_mjj.Draw()
        c.SaveAs("results/sidebands/{0}_{1:.1f}_{2:.1f}.png".format(taggerName,point,wp))


wps = [0.8,0.9]

#f   = r.TFile.Open("results/templates/WP_0.88_0.95/prevar/2018/scaled/QCD18.root")
f   = r.TFile.Open("results/templates/WP_{0}_{1}/2016/scaled/JetHT16.root".format(wps[0],wps[1]))
h2d_TT = f.Get("JetHT_mJY_mJJ_TT_nom")
h2d_LL = f.Get("JetHT_mJY_mJJ_LL_nom")
h2d_AT = f.Get("JetHT_mJY_mJJ_AT_nom")
h2d_VRP = f.Get("JetHT_mJY_mJJ_VRP_nom")
h2d_VRF = f.Get("JetHT_mJY_mJJ_VRF_nom")

#delta eta sideband
h2d_SB_TT = f.Get("JetHT_mJY_mJJ_SB_TT_nom")
h2d_SB_LL = f.Get("JetHT_mJY_mJJ_SB_LL_nom")
h2d_SB_AT = f.Get("JetHT_mJY_mJJ_SB_AT_nom")
h2d_SB_VRP = f.Get("JetHT_mJY_mJJ_SB_VRP_nom")
h2d_SB_VRF = f.Get("JetHT_mJY_mJJ_SB_VRF_nom")

# h2d_TT = f.Get("QCD_mJY_mJJ_TT")
# h2d_LL = f.Get("QCD_mJY_mJJ_LL")
# h2d_AT = f.Get("QCD_mJY_mJJ_AT")
# h2d_VRP = f.Get("QCD_mJY_mJJ_VRP")
# h2d_VRF = f.Get("QCD_mJY_mJJ_VRF")

hMJJ_TT = h2d_TT.ProjectionY("hMJJ_TT",1,-1)#avoid underflow
hMJJ_LL = h2d_LL.ProjectionY("hMJJ_LL",1,-1)#avoid underflow
hMJJ_AT = h2d_AT.ProjectionY("hMJJ_AT",1,-1)#avoid underflow
hMJJ_VRP = h2d_VRP.ProjectionY("hMJJ_VRP",1,-1)#avoid underflow
hMJJ_VRF = h2d_VRF.ProjectionY("hMJJ_VRF",1,-1)#avoid underflow
hMJY_TT = h2d_TT.ProjectionX("hMJY_TT",1,-1)#avoid underflow
hMJY_LL = h2d_LL.ProjectionX("hMJY_LL",1,-1)#avoid underflow
hMJY_AT = h2d_AT.ProjectionX("hMJY_AT",1,-1)#avoid underflow
hMJY_VRP = h2d_VRP.ProjectionX("hMJY_VRP",1,-1)#avoid underflow
hMJY_VRF = h2d_VRF.ProjectionX("hMJY_VRF",1,-1)#avoid underflow

#delta eta sideband
hMJJ_SB_TT = h2d_SB_TT.ProjectionY("hMJJ_SB_TT",1,-1)#avoid underflow
hMJJ_SB_LL = h2d_SB_LL.ProjectionY("hMJJ_SB_LL",1,-1)#avoid underflow
hMJJ_SB_AT = h2d_SB_AT.ProjectionY("hMJJ_SB_AT",1,-1)#avoid underflow
hMJJ_SB_VRP = h2d_SB_VRP.ProjectionY("hMJJ_SB_VRP",1,-1)#avoid underflow
hMJJ_SB_VRF = h2d_SB_VRF.ProjectionY("hMJJ_SB_VRF",1,-1)#avoid underflow
hMJY_SB_TT = h2d_SB_TT.ProjectionX("hMJY_SB_TT",1,-1)#avoid underflow
hMJY_SB_LL = h2d_SB_LL.ProjectionX("hMJY_SB_LL",1,-1)#avoid underflow
hMJY_SB_AT = h2d_SB_AT.ProjectionX("hMJY_SB_AT",1,-1)#avoid underflow
hMJY_SB_VRP = h2d_SB_VRP.ProjectionX("hMJY_SB_VRP",1,-1)#avoid underflow
hMJY_SB_VRF = h2d_SB_VRF.ProjectionX("hMJY_SB_VRF",1,-1)#avoid underflow

hMJJ_TT.Scale(1/hMJJ_TT.Integral())
hMJJ_LL.Scale(1/hMJJ_LL.Integral())
hMJJ_AT.Scale(1/hMJJ_AT.Integral())
hMJJ_VRP.Scale(1/hMJJ_VRP.Integral())
hMJJ_VRF.Scale(1/hMJJ_VRF.Integral())
hMJY_TT.Scale(1/hMJY_TT.Integral())
hMJY_LL.Scale(1/hMJY_LL.Integral())
hMJY_AT.Scale(1/hMJY_AT.Integral())
hMJY_VRP.Scale(1/hMJY_VRP.Integral())
hMJY_VRF.Scale(1/hMJY_VRF.Integral())

hMJJ_SB_TT.Scale(1/hMJJ_SB_TT.Integral())
hMJJ_SB_LL.Scale(1/hMJJ_SB_LL.Integral())
hMJJ_SB_AT.Scale(1/hMJJ_SB_AT.Integral())
hMJJ_SB_VRP.Scale(1/hMJJ_SB_VRP.Integral())
hMJJ_SB_VRF.Scale(1/hMJJ_SB_VRF.Integral())
hMJY_SB_TT.Scale(1/hMJY_SB_TT.Integral())
hMJY_SB_LL.Scale(1/hMJY_SB_LL.Integral())
hMJY_SB_AT.Scale(1/hMJY_SB_AT.Integral())
hMJY_SB_VRP.Scale(1/hMJY_SB_VRP.Integral())
hMJY_SB_VRF.Scale(1/hMJY_SB_VRF.Integral())

# compareShapes(hMJJ_AT,hMJJ_TT,"MJJ_TT_0.88_0.95.png",xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="Anti-tag",label2="Tight-tight",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="WPs = 0.88, 0.95")
# compareShapes(hMJJ_AT,hMJJ_LL,"MJJ_LL_0.88_0.95.png",xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="Anti-tag",label2="Loose-loose",labelR="LL/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="WPs = 0.88, 0.95")
# compareShapes(hMJJ_VRF,hMJJ_VRP,"MJJ_VR_0.88_0.95.png",xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=False,text="WPs = 0.88, 0.95")

# compareShapes(hMJY_AT,hMJY_TT,"MJY_TT_0.88_0.95.png",xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="Anti-tag",label2="Tight-tight",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="WPs = 0.88, 0.95")
# compareShapes(hMJY_AT,hMJY_LL,"MJY_LL_0.88_0.95.png",xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="Anti-tag",label2="Loose-loose",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="WPs = 0.88, 0.95")
# compareShapes(hMJY_VRF,hMJY_VRP,"MJY_VR_0.88_0.95.png",xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=False,text="WPs = 0.88, 0.95")


# compareShapes(hMJJ_SB_AT,hMJJ_SB_TT,"MJJ_SB_TT_0.88_0.95.png",xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="Anti-tag",label2="Tight-tight",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="$\Delta \eta$ sideband\nWPs = 0.88, 0.95")
# compareShapes(hMJJ_SB_AT,hMJJ_SB_LL,"MJJ_SB_LL_0.88_0.95.png",xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="Anti-tag",label2="Loose-loose",labelR="LL/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="$\Delta \eta$ sideband\nWPs = 0.88, 0.95")
# compareShapes(hMJJ_SB_VRF,hMJJ_SB_VRP,"MJJ_SB_VR_0.88_0.95.png",xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=False,text="$\Delta \eta$ sideband\nWPs = 0.88, 0.95")

# compareShapes(hMJY_SB_AT,hMJY_SB_TT,"MJY_SB_TT_0.88_0.95.png",xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="Anti-tag",label2="Tight-tight",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="$\Delta \eta$ sideband\nWPs = 0.88, 0.95")
# compareShapes(hMJY_SB_AT,hMJY_SB_LL,"MJY_SB_LL_0.88_0.95.png",xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="Anti-tag",label2="Loose-loose",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=False,text="$\Delta \eta$ sideband\nWPs = 0.88, 0.95")
# compareShapes(hMJY_SB_VRF,hMJY_SB_VRP,"MJY_SB_VR_0.88_0.95.png",xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=False,text="$\Delta \eta$ sideband\nWPs = 0.88, 0.95")

#Data
compareShapes(hMJJ_VRF,hMJJ_VRP,"MJJ_VR_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=True,text="WPs = {0} {1}".format(wps[0],wps[1]))

compareShapes(hMJY_VRF,hMJY_VRP,"MJY_VR_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=True,text="WPs = {0} {1}".format(wps[0],wps[1]))


compareShapes(hMJJ_SB_AT,hMJJ_SB_TT,"MJJ_SB_TT_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="Anti-tag",label2="Tight-tight",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=True,text="$\Delta \eta$ sideband\nWPs = {0} {1}".format(wps[0],wps[1]))
compareShapes(hMJJ_SB_AT,hMJJ_SB_LL,"MJJ_SB_LL_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="Anti-tag",label2="Loose-loose",labelR="LL/AT",yRange=[0,1.0],xRange=[],log=False,data=True,text="$\Delta \eta$ sideband\nWPs = {0} {1}".format(wps[0],wps[1]))
compareShapes(hMJJ_SB_VRF,hMJJ_SB_VRP,"MJJ_SB_VR_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJJ [GeV]",yTitle="Event fraction/100GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=True,text="$\Delta \eta$ sideband\nWPs = {0} {1}".format(wps[0],wps[1]))

compareShapes(hMJY_SB_AT,hMJY_SB_TT,"MJY_SB_TT_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="Anti-tag",label2="Tight-tight",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=True,text="$\Delta \eta$ sideband\nWPs = {0} {1}".format(wps[0],wps[1]))
compareShapes(hMJY_SB_AT,hMJY_SB_LL,"MJY_SB_LL_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="Anti-tag",label2="Loose-loose",labelR="TT/AT",yRange=[0,1.0],xRange=[],log=False,data=True,text="$\Delta \eta$ sideband\nWPs = {0} {1}".format(wps[0],wps[1]))
compareShapes(hMJY_SB_VRF,hMJY_SB_VRP,"MJY_SB_VR_{0}_{1}.png".format(wps[0],wps[1]),xTitle="MJY [GeV]",yTitle="Event fraction/20GeV",label1="VRF",label2="VRP",labelR="VRP/VRF",yRange=[0,1.0],xRange=[],log=False,data=True,text="$\Delta \eta$ sideband\nWPs = {0} {1}".format(wps[0],wps[1]))

