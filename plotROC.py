#
# Simple script to produce the performance plots
#

from array import array
from ROOT import *

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

    b_eff = array('f')
    nonb_eff = array('f')
    tot_b= histo_b.GetEntries()
    tot_nonb= histo_nonb.GetEntries()

    print "Total number of jets:"
    print tot_b,"b jets"
    print tot_nonb,"non-b jets"

    b_abovecut = 0
    nonb_abovecut = 0

    firstbin = histo_b.GetXaxis().FindBin(0.) - 1
    if allowNegative: firstbin = -1
    lastbin = histo_b.GetXaxis().GetNbins() + 1 # '+ 1' to also include any entries in the overflow bin

    for i in xrange(lastbin,firstbin,-1) : # from 'overflow' bin to 0, in steps of "-1"
        b_abovecut += histo_b.GetBinContent(i)
        nonb_abovecut += histo_nonb.GetBinContent(i)
        b_eff.append(b_abovecut/tot_b)
        nonb_eff.append(nonb_abovecut/tot_nonb)

    return TGraph(len(b_eff), b_eff, nonb_eff)

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
    massPoints = [100,125,200,300]
    inputFile_dak8 = TFile.Open('efficiencies_dak8.root')
    H_dak8 = inputFile_dak8.Get('matchedH_pt_vs_tag_Y100')
    jet0_dak8 = inputFile_dak8.Get('FatJet[0]_pt_vs_tag_QCD')
    jet1_dak8 = inputFile_dak8.Get('FatJet[1]_pt_vs_tag_QCD')
    jet0_dak8.Add(jet1_dak8)
    Ys_dak8 = []
    for i,massPoint in enumerate(massPoints):
        temp = inputFile_dak8.Get('matchedY_pt_vs_tag_Y{0}'.format(massPoint))
        temp.SetName("dak8_Y_{0}".format(massPoint))
        temp.SetDirectory(0)
        Ys_dak8.append(temp)
        if(i==0):
            continue
        H_dak8.Add(inputFile_dak8.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint)))
    
    H_dak8.SetName("H_dak8")
    jet0_dak8.SetName("QCD_dak8")
    H_dak8.SetDirectory(0)
    jet0_dak8.SetDirectory(0)
    inputFile_dak8.Close()



    inputFile_pnet = TFile.Open('efficiencies.root')
    H_pnet = inputFile_pnet.Get('matchedH_pt_vs_tag_Y100')
    jet0_pnet = inputFile_pnet.Get('FatJet[0]_pt_vs_tag_QCD')
    jet1_pnet = inputFile_pnet.Get('FatJet[1]_pt_vs_tag_QCD')
    jet0_pnet.Add(jet1_pnet)
    Ys_pnet = []
    for i,massPoint in enumerate(massPoints):
        temp = inputFile_pnet.Get('matchedY_pt_vs_tag_Y{0}'.format(massPoint))
        temp.SetName("pnet_Y_{0}".format(massPoint))
        temp.SetDirectory(0)
        Ys_pnet.append(temp)
        if(i==0):
            continue
        H_pnet.Add(inputFile_pnet.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint)))
    
    H_pnet.SetName("H_pnet")
    jet0_pnet.SetName("QCD_pnet")
    H_pnet.SetDirectory(0)
    jet0_pnet.SetDirectory(0)
    inputFile_pnet.Close()

    color = [kOrange, kRed, kCyan, kGreen, kMagenta, kBlue, kBlack]
    legend = ['dak8 H eff','pnet H eff','dak8 Y 100 eff','pnet Y 100 eff','dak8 Y 200 eff','pnet Y 200 eff']

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


    g = [0]*10
    # for i,massPoint in enumerate(massPoints):
    #     if(i==0):
    #         continue
    #     H_dak8.Add(inputFile_dak8.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint)))
    #     H_pnet.Add(inputFile_pnet.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint)))

    #make y-axis projections to get 1D discriminator distributions
    c.SetGridx()
    c.SetGridy()
    c.SetLogy()


    discrH_dak8 = H_dak8.ProjectionY()
    discr_qcd_dak8 = jet0_dak8.ProjectionY()
    discrH_pnet = H_pnet.ProjectionY()
    discr_qcd_pnet = jet0_pnet.ProjectionY()
    allowNegative = False
    # get eff vs mistag rate graph
    g[0] = makeEffVsMistagTGraph(discrH_dak8,discr_qcd_dak8,allowNegative)
    g[1] = makeEffVsMistagTGraph(discrH_pnet,discr_qcd_pnet,allowNegative)
    g[2] = makeEffVsMistagTGraph(Ys_dak8[0].ProjectionY(),discr_qcd_dak8,allowNegative)
    g[3] = makeEffVsMistagTGraph(Ys_pnet[0].ProjectionY(),discr_qcd_pnet,allowNegative)
    g[4] = makeEffVsMistagTGraph(Ys_dak8[2].ProjectionY(),discr_qcd_dak8,allowNegative)
    g[5] = makeEffVsMistagTGraph(Ys_pnet[2].ProjectionY(),discr_qcd_pnet,allowNegative)
    for i in range(0,6):
        g[i].SetLineWidth(2)
        g[i].SetLineColor(color[i])
        g[i].Draw('l')
        leg.AddEntry(g[i],legend[i],"l")

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
    inputFile_pnet.Close()
    inputFile_dak8.Close()

def main():
        # input file
    inputFile = TFile.Open('efficiencies.root')


    color = [kOrange, kRed, kCyan, kGreen, kMagenta, kBlue, kBlack]
    legend = ['matched H vs FatJet0','matched H vs FatJet1','matched Y vs FatJet0','matched Y vs FatJet1',]


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

    massPoints = [100,125,200,300]
    g = [0]*4
    for massPoint in massPoints:
        discrVsPt_H    = inputFile.Get('matchedH_pt_vs_tag_Y{0}'.format(massPoint))
        discrVsPt_Y    = inputFile.Get('matchedY_pt_vs_tag_Y{0}'.format(massPoint))
        discrVsPt_Jet0 = inputFile.Get('FatJet[0]_pt_vs_tag_QCD')
        discrVsPt_Jet1 = inputFile.Get('FatJet[1]_pt_vs_tag_QCD')
        print("Pt bin width in GeV: {0}".format(discrVsPt_H.ProjectionX().GetBinWidth(10)))
        # make y-axis projections to get 1D discriminator distributions
        discr_H    = discrVsPt_H.ProjectionY()
        discr_Y    = discrVsPt_Y.ProjectionY()
        discr_Jet0 = discrVsPt_Jet0.ProjectionY()
        discr_Jet1 = discrVsPt_Jet1.ProjectionY()

        allowNegative = False
        # get eff vs mistag rate graph
        g[0] = makeEffVsMistagTGraph(discr_H,discr_Jet0,allowNegative)
        g[1] = makeEffVsMistagTGraph(discr_H,discr_Jet1,allowNegative)
        g[2] = makeEffVsMistagTGraph(discr_Y,discr_Jet0,allowNegative)
        g[3] = makeEffVsMistagTGraph(discr_Y,discr_Jet1,allowNegative)
        for i in range(4):
            g[i].SetLineWidth(2)
            g[i].SetLineColor(color[i])
            g[i].Draw('l')
            leg.AddEntry(g[i],legend[i],"l")

        leg.Draw()

        gPad.RedrawAxis()

        # save the plot
        c.SaveAs('ROC_Y{0}.png'.format(massPoint))

        leg.Clear()
        for gr in g:
            gr.Delete()
    c.Close()
        #bkg.Delete()

        # close the input file
    inputFile.Close()


if __name__ == '__main__':
    compareTaggers()
