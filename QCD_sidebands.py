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
    wp = 0.8
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
    wp = 0.8
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

def compareShapes(h1,h2,outFile,xTitle="",yTitle="",yRange=[],xRange=[],log=False,label1="",label2="",labelR="Data/MC",data=False):
    hRpf_mj = createRatio(h1,h2)
    hRatio = []
    hRatioErrors = []
    hDataErrors = []
    hData = []
    hDataCentres = []
    for i in range(1,hRpf_mj.GetNbinsX()+1):
        hRatio.append(hRpf_mj.GetBinContent(i))
        hRatioErrors.append(hRpf_mj.GetBinError(i))
    for i in range(1,h2.GetNbinsX()+1):
        hData.append(h2.GetBinContent(i))
        hDataCentres.append(h2.GetBinCenter(i))
        hDataErrors.append(h2.GetBinError(i))
    #numpy histograms
    h1, h1Edges = hist2array(h1,return_edges=True)
    h2, h2Edges = hist2array(h2,return_edges=True)
    hRatio = np.asarray(hRatio)
    hRatioErrors = np.asarray(hRatioErrors)
    centresRatio = (h1Edges[0][:-1] + h1Edges[0][1:])/2.

    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots(2,1, sharex=True, sharey=False,gridspec_kw={'height_ratios': [4, 1],'hspace': 0.05})
    axs = axs.flatten()
    plt.sca(axs[0])
    if(log):
        axs[0].set_yscale("log")
    hep.histplot(h1,h1Edges[0],stack=False,ax=axs[0],label = label1, histtype="step",color="r")

    if(label2=="data_obs"):
        print("Plotting data")
        plt.errorbar(hDataCentres,hData, yerr=hDataErrors, fmt='o',color="k",label = label2)
    else:
        hep.histplot(h2,h2Edges[0],stack=False,ax=axs[0],label = label2, histtype="step",color="k")
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
        hep.cms.lumitext(text='59.8 $fb^{-1} (13 TeV)$', ax=axs[0], fontname=None, fontsize=None)
    else:
        hep.cms.lumitext(text='2018', ax=axs[0], fontname=None, fontsize=None)
        hep.cms.text("Simulation WiP",loc=1)
    plt.legend(loc="best")#loc = (0.4,0.2))

    plt.sca(axs[1])#switch to lower pad
    axs[1].axhline(y=1.0, xmin=0, xmax=1, color="r")
    axs[1].set_ylim([0.0,2.0])
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)

    plt.errorbar(centresRatio,hRatio, yerr=hRatioErrors, fmt='o',color="k")    

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

    wp = 0.8
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


        legend_mj = r.TLegend(0.45,0.40,0.90,0.90)
        legend_mj.SetHeader("","")
        legend_mj.AddEntry(h_mj_pass,"Normalized QCD pass, {1} > {0:.1f}".format(wp,taggerName),"l")
        legend_mj.AddEntry(h_mj_fail,"Normalized QCD fail, {0:.1f} < {2} < {1:.1f}".format(point,wp,taggerName),"l")
        legend_mj.AddEntry(hRpf_mj,"Normalized Rpf","ep")
        legend_mj.SetFillStyle(0);
        legend_mj.SetBorderSize(0);
        pad1.cd()
        legend_mj.Draw()

        legend_mjj = r.TLegend(0.45,0.40,0.90,0.90)
        legend_mjj.SetHeader("","")
        legend_mjj.AddEntry(h_mjj_pass,"Normalized QCD pass, {1} > {0:.1f}".format(wp,taggerName),"l")
        legend_mjj.AddEntry(h_mjj_fail,"Normalized QCD fail, {0:.1f} < {2} < {1:.1f}".format(point,wp,taggerName),"l")
        legend_mjj.AddEntry(hRpf_mjj,"Normalized Rpf","ep")
        legend_mjj.SetFillStyle(0);
        legend_mjj.SetBorderSize(0);
        pad3.cd()
        legend_mjj.Draw()
        c.SaveAs("results/sidebands/{0}_{1:.1f}_{2:.1f}.png".format(taggerName,point,wp))




f = r.TFile.Open("results/histograms/2018/lumiScaled/QCD_normalized.root")
g = r.TFile.Open("results/histograms/2018/lumiScaled/data_obs.root")

h_3d_pnet = f.Get("QCD_pnet_mjj_mjY")

#plotSidebands(h_3d_pnet,"ParticleNet")
# plotSidebandsMJJ_mpl(h_3d_pnet,"results/sidebands/MJJ_lin.png",xTitle="Dijet invariant mass [GeV]",yTitle="Normalized events/100GeV",yRange=[0,0.5],xRange=[700, 2000])
# plotSidebandsMJJ_mpl(h_3d_pnet,"results/sidebands/MJJ_log.png",xTitle="Dijet invariant mass [GeV]",yTitle="Normalized events/100GeV",yRange=[10e-4,1.0],xRange=[700, 2000],log=True)
# plotSidebandsMJY_mpl(h_3d_pnet,"results/sidebands/MJY_lin.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Normalized events/20GeV",yRange=[0,0.3],xRange=[50, 300])
# plotSidebandsMJY_mpl(h_3d_pnet,"results/sidebands/MJY_log.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Normalized events/20GeV",yRange=[10e-4,1.0],xRange=[50, 300],log=True)
hMJJ_QCD_AT = f.Get("QCD_mjjHY_pnet_AT")
hMJJ_data_AT = g.Get("data_obs_mjjHY_pnet_AT")
hMJY_QCD_AT = f.Get("QCD_mjY_pnet_AT")
hMJY_data_AT = g.Get("data_obs_mjY_pnet_AT")

hMJJ_QCD_AT.Scale(hMJJ_data_AT.Integral()/hMJJ_QCD_AT.Integral())
hMJY_QCD_AT.Scale(hMJY_data_AT.Integral()/hMJY_QCD_AT.Integral())

hMJJ_data_AT.Rebin(10)
hMJJ_QCD_AT.Rebin(10)
hMJY_QCD_AT.Rebin(2)
hMJY_data_AT.Rebin(2)

compareShapes(hMJJ_QCD_AT,hMJJ_data_AT,"results/plots/2018/sidebands/lin/QCD_data_MJJ.png",xTitle="Dijet invariant mass [GeV]",yTitle="Events/100GeV",label1="Multijet",label2="data_obs",yRange=[0,60000],xRange=[750, 3050],log=False,data=True)
compareShapes(hMJJ_QCD_AT,hMJJ_data_AT,"results/plots/2018/sidebands/log/QCD_data_MJJ.png",xTitle="Dijet invariant mass [GeV]",yTitle="Events/100GeV",label1="Multijet",label2="data_obs",yRange=[None,10e5],xRange=[750, 3050],log=True,data=True)
compareShapes(hMJY_QCD_AT,hMJY_data_AT,"results/plots/2018/sidebands/lin/QCD_data_MJY.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20GeV",label1="Multijet",label2="data_obs",yRange=[0,35000],xRange=[50, 300],log=False,data=True)
compareShapes(hMJY_QCD_AT,hMJY_data_AT,"results/plots/2018/sidebands/log/QCD_data_MJY.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Events/20GeV",label1="Multijet",label2="data_obs",yRange=[None,10e5],xRange=[50, 300],log=True,data=True)


hMJJ_QCD_TT = f.Get("QCD_mjjHY_pnet_TT")
hMJJ_QCD_LL = f.Get("QCD_mjjHY_pnet_LL")
hMJY_QCD_TT = f.Get("QCD_mjY_pnet_TT")
hMJY_QCD_LL = f.Get("QCD_mjY_pnet_LL")

hMJJ_QCD_TT.Scale(1/hMJJ_QCD_TT.Integral())
hMJJ_QCD_LL.Scale(1/hMJJ_QCD_LL.Integral())
hMJJ_QCD_AT.Scale(1/hMJJ_QCD_AT.Integral())
hMJY_QCD_TT.Scale(1/hMJY_QCD_TT.Integral())
hMJY_QCD_LL.Scale(1/hMJY_QCD_LL.Integral())
hMJY_QCD_AT.Scale(1/hMJY_QCD_AT.Integral())

hMJJ_QCD_LL.Rebin(10)
hMJY_QCD_LL.Rebin(2)
hMJJ_QCD_TT.Rebin(10)
hMJY_QCD_TT.Rebin(2)


compareShapes(hMJJ_QCD_TT,hMJJ_QCD_AT,"results/plots/2018/sidebands/lin/QCD_TTAT_MJJ.png",xTitle="Dijet invariant mass [GeV]",yTitle="Event fraction/100GeV",label1="Tight-tight",label2="Anti-tag",labelR="TT/AT",yRange=[0,0.5],xRange=[750, 3050],log=False,data=False)
compareShapes(hMJJ_QCD_TT,hMJJ_QCD_AT,"results/plots/2018/sidebands/log/QCD_TTAT_MJJ.png",xTitle="Dijet invariant mass [GeV]",yTitle="Event fraction/100GeV",label1="Tight-tight",label2="Anti-tag",labelR="TT/AT",yRange=[None,10e1],xRange=[750, 3050],log=True,data=False)
compareShapes(hMJJ_QCD_LL,hMJJ_QCD_AT,"results/plots/2018/sidebands/lin/QCD_LLAT_MJJ.png",xTitle="Dijet invariant mass [GeV]",yTitle="Event fraction/100GeV",label1="Loose-loose",label2="Anti-tag",labelR="LL/AT",yRange=[0,0.5],xRange=[750, 3050],log=False,data=False)
compareShapes(hMJJ_QCD_LL,hMJJ_QCD_AT,"results/plots/2018/sidebands/log/QCD_LLAT_MJJ.png",xTitle="Dijet invariant mass [GeV]",yTitle="Event fraction/100GeV",label1="Loose-loose",label2="Anti-tag",labelR="LL/AT",yRange=[None,10e1],xRange=[750, 3050],log=True,data=False)
compareShapes(hMJY_QCD_TT,hMJY_QCD_AT,"results/plots/2018/sidebands/lin/QCD_TTAT_MJY.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Event fraction/20GeV",label1="Tight-tight",label2="Anti-tag",labelR="TT/AT",yRange=[0,0.5],xRange=[50, 300],log=False,data=False)
compareShapes(hMJY_QCD_TT,hMJY_QCD_AT,"results/plots/2018/sidebands/log/QCD_TTAT_MJY.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Event fraction/20GeV",label1="Tight-tight",label2="Anti-tag",labelR="TT/AT",yRange=[None,10e1],xRange=[50, 300],log=True,data=False)
compareShapes(hMJY_QCD_LL,hMJY_QCD_AT,"results/plots/2018/sidebands/lin/QCD_LLAT_MJY.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Event fraction/20GeV",label1="Loose-loose",label2="Anti-tag",labelR="LL/AT",yRange=[0,0.5],xRange=[50, 300],log=False,data=False)
compareShapes(hMJY_QCD_LL,hMJY_QCD_AT,"results/plots/2018/sidebands/log/QCD_LLAT_MJY.png",xTitle="Y-jet $m_{SD}$ [GeV]",yTitle="Event fraction/20GeV",label1="Loose-loose",label2="Anti-tag",labelR="LL/AT",yRange=[None,10e1],xRange=[50, 300],log=True,data=False)