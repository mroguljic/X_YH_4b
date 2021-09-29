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
    wpL = (0.,0.)

    for i in range(lastbin,firstbin,-1) : # from 'overflow' bin to 0, in steps of "-1"
        b_abovecut += histo_b.GetBinContent(i)
        nonb_abovecut += histo_nonb.GetBinContent(i)
        b_eff.append(b_abovecut/tot_b)
        nonb_eff.append(nonb_abovecut/tot_nonb)
        if(histo_b.GetBinCenter(i)<0.96 and histo_b.GetBinCenter(i)>0.94):
            wpT = b_eff[-1],nonb_eff[-1]
        if(histo_b.GetBinCenter(i)==0.805):
            wpL = b_eff[-1],nonb_eff[-1]
        #print(b_eff[-1],nonb_eff[-1],histo_b.GetBinCenter(i),histo_nonb.GetBinCenter(i))

    return TGraph(len(b_eff), b_eff, nonb_eff), b_eff, nonb_eff, wpT,wpL

def higgsDependanceOnMassY():
        # input file
    inputFile = TFile.Open('efficiencies.root')


    color = [kOrange, kRed, kCyan, kGreen, kMagenta, kBlue, kBlack]
    legend = ['H_Y=100 GeV vs QCD','H_Y=125 GeV vs QCD','H_Y=200 GeV vs QCD','H_Y=300 GeV vs QCD','H_Y=400 GeV vs QCD']


    # create canvas
    c = TCanvas("c", "",1000,1000)
    c.cd()
    c.SetGridx()
    c.SetGridy()
    c.SetLogy()

    # empty 2D background historgram to simplify defining axis ranges to display
    bkg = TH2F('bkg','title',100,0.,1.,100,1e-4,1.)
    bkg.GetYaxis().SetTitleOffset(1.2)
    bkg.Draw()

    # create legend
    leg = TLegend(.20,.80-4*0.04,.40,.80)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.03)

    massPoints = [100,125,200,300,400]
    g = []
    for massPoint in massPoints:
        discrVsPt_H    = inputFile.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint))
        discrVsPt_Jet0 = inputFile.Get('FatJet[0]_pt_vs_tag_QCD')
        discrVsPt_Jet1 = inputFile.Get('FatJet[1]_pt_vs_tag_QCD')
        #print("Pt bin width in GeV: {0}".format(discrVsPt_H.ProjectionX().GetBinWidth(10)))
        # make y-axis projections to get 1D discriminator distributions
        discr_H    = discrVsPt_H.ProjectionY()
        discr_Jet0 = discrVsPt_Jet0.ProjectionY()
        discr_Jet1 = discrVsPt_Jet1.ProjectionY()
        discr_Jet0.Add(discr_Jet1)

        allowNegative = False
        # get eff vs mistag rate graph
        temp = makeEffVsMistagTGraph(discr_H,discr_Jet0,allowNegative)
        temp.SetLineWidth(2)
        temp.Draw('l')
        g.append(temp)
    for i in range(5):
        leg.AddEntry(g[i],legend[i],"l")
        g[i].SetLineColor(color[i])

    leg.Draw()

    gPad.RedrawAxis()

    # save the plot
    c.SaveAs('ROC_Hspread.png')


    c.Close()
        #bkg.Delete()

        # close the input file
    inputFile.Close()
def compareTaggers():
        # input file
    massPoints = [90,100,125,200,250,300,400]
    massPoints = [90,125,200]#,250,300]
    taggers = ['dak8','pnet']
    inputFile = TFile.Open('efficiencies.root')
    H_histos = {}
    Y_histos = {}
    QCD_histos = {}
    for tagger in taggers:
        H_histos[tagger] = {}
        Y_histos[tagger] = {}
        QCD_histos[tagger] = inputFile.Get("QCD_{0}".format(tagger))
        for massPoint in massPoints:
            H_histo = inputFile.Get("H_mx1600_Y{0}_{1}".format(massPoint,tagger))
            Y_histo = inputFile.Get("Y_mx1600_Y{0}_{1}".format(massPoint,tagger))
            H_histos[tagger][massPoint] = H_histo
            Y_histos[tagger][massPoint] = Y_histo


    for tagger in taggers:
        for i,massPoint in enumerate(massPoints):
            if i==0:
                H_histos[tagger]['sum'] = H_histos[tagger][massPoint]
            else:
                H_histos[tagger]['sum'].Add(H_histos[tagger][massPoint])


    color = [kOrange, kRed, kCyan, kGreen, kMagenta, kBlue, kBlack]
    lineStyle = [1,2,3,4,5,6]
    legend = []
    for tagger in taggers:
        legend.append("{0} H eff".format(tagger))
    
    for tagger in taggers:
        for massPoint in massPoints:
            legend.append("{0} Y eff at Y_M {1}".format(tagger,massPoint))

    # create canvas
    c = TCanvas("c", "",2000,2000)
    c.cd()
    c.SetGridx()
    c.SetGridy()
    c.SetLogy()

    # empty 2D background historgram to simplify defining axis ranges to display
    bkg = TH2F('bkg','title',100,0.,1.,100,1e-4,1.)
    bkg.GetYaxis().SetTitleOffset(1.2)
    bkg.Draw()

    # create legend
    leg = TLegend(.20,.90-12*0.04,.40,.90)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.03)


    g = []
    # for i,massPoint in enumerate(massPoints):
    #     if(i==0):
    #         continue
    #     H_dak8.Add(inputFile_dak8.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint)))
    #     H_pnet.Add(inputFile_pnet.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint)))

    #make y-axis projections to get 1D discriminator distributions
    c.SetGridx()
    c.SetGridy()
    c.SetLogy()
    allowNegative = False

    for i,tagger in enumerate(taggers):
        h_Sig = H_histos[tagger]['sum'].ProjectionY()
        h_Bkg = QCD_histos[tagger].ProjectionY()
        temp = makeEffVsMistagTGraph(h_Sig,h_Bkg,allowNegative)
        temp.SetLineWidth(3)
        temp.SetLineStyle(lineStyle[i])
        temp.SetLineColor(kBlack)
        g.append(temp)
    
    for i,tagger in enumerate(taggers):
        for j,massPoint in enumerate(massPoints):
                h_Sig = Y_histos[tagger][massPoint].ProjectionY()
                h_Bkg = QCD_histos[tagger].ProjectionY()
                temp  = makeEffVsMistagTGraph(h_Sig,h_Bkg,allowNegative)
                temp.SetLineWidth(3)
                temp.SetLineStyle(lineStyle[i])
                temp.SetLineColor(color[j])
                g.append(temp)

    for i,graph in enumerate(g):
        graph.Draw('l')
        leg.AddEntry(graph,legend[i],"l")

    leg.Draw()

    gPad.RedrawAxis()

    # save the plot
    c.SaveAs('taggerCompairson.png')

    #leg.Clear()
    #for gr in g:
    #    gr.Delete()
    c.Close()
        #bkg.Delete()

        # close the input file
    inputFile.Close()

def plotSelectedGraphs(graphs,legend,colors,output):
    # create canvas
    c = TCanvas("c", "",1000,1000)
    c.cd()
    c.SetGridx()
    c.SetGridy()
    c.SetLogy()

    # empty 2D background historgram to simplify defining axis ranges to display
    bkg = TH2F('bkg','title;Signal efficiency;Background mistag rate;',100,0.,1.,100,1e-3,1.)
    bkg.GetYaxis().SetTitleOffset(1.5)
    bkg.Draw()
    # create legend
    leg = TLegend(.20,.80-4*0.04,.40,.80)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.03)

    for i,g in enumerate(graphs):
        g.SetLineWidth(2)
        g.SetLineColor(colors[i])
        g.Draw('l')
        leg.AddEntry(g,legend[i],"l")
    
    leg.Draw()
    gPad.RedrawAxis()
        # save the plot
    c.SaveAs(output)

    leg.Clear()
    c.Close()

def main():
    # input file
    #for year in ["16","17","18"]:
    plt.style.use([hep.style.CMS])
    f, axs = plt.subplots()
    axs.set_ylim([3*10e-4,1])
    colors = [["b","k"],["r","g"],["orange","gold"]]
    i=0
    #for year in ["16","17"]:
    for year in ["17"]:
        sigFile = TFile.Open("results/templates/WP_0.8_0.95/20{0}/scaled/MX1600_MY125.root".format(year))
        bkgFile = TFile.Open("results/templates/WP_0.8_0.95/20{0}/scaled/QCD{0}.root".format(year))
        ttbarFile = TFile.Open("results/templates/WP_0.8_0.95/20{0}/scaled/TTbar{0}.root".format(year))

        legend = ["Signal vs QCD {0}".format(year), "Signal vs ttbar {0}".format(year)]
        graphs = []

        h_sig_pnet = sigFile.Get("MX1600_MY125_pnet_pT_H_nom").ProjectionX()
        h_sig_pnet.SetDirectory(0)
        h_bkg_pnet = bkgFile.Get("QCD_pnet_pT_H_nom").ProjectionX()
        h_tt_pnet = ttbarFile.Get("TTbar_pnet_pT_H_nom").ProjectionX()
        allowNegative = False
        # get eff vs mistag rate graph
        gVsQCD, effVsSig, mistagVsQCD, wpTVsQCD,wpLVsQCD = makeEffVsMistagTGraph(h_sig_pnet,h_bkg_pnet,allowNegative)
        graphs.append(gVsQCD)
        gVsTT, effVsTT, mistagVsTT, wpTVsTT,wpLVsTT = makeEffVsMistagTGraph(h_sig_pnet,h_tt_pnet,allowNegative)
        graphs.append(gVsTT)
        #dak8
        # get eff vs mistag rate graph
        #plotSelectedGraphs(graphs,legend,colors,"results/plots/ROC.png")
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
        plt.plot(effVsSig,mistagVsQCD,lineStyle="-" ,color=colors[i][0],label="ParticleNet signal vs QCD 20{0}".format(year))
        plt.plot(effVsTT,mistagVsTT,lineStyle="-",color=colors[i][1], label=r"ParticleNet signal vs $t\bar{t}$"+" 20{0}".format(year))
        if(year=="16"):
            labelT = "WP = 0.95"
            labelL = "WP = 0.8"
        else:
            labelT = '_nolegend_'
            labelL = '_nolegend_'
        plt.plot([wpTVsQCD[0],wpTVsTT[0]], [wpTVsQCD[1],wpTVsTT[1]], marker='o', markersize=5, color="r",label=labelT,linewidth=0)
        plt.plot([wpLVsQCD[0],wpLVsTT[0]], [wpLVsQCD[1],wpLVsTT[1]], marker='o', markersize=5, color="m",label=labelL,linewidth=0)
        i+=1
    axs.legend()
    plt.grid(which='both')
    plt.savefig("ROC.pdf")
    plt.savefig("ROC.png")
if __name__ == '__main__':
    main()
    #compareTaggers()
