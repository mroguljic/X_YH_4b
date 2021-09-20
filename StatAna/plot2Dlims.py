#!/usr/bin/env python

import os, sys
import uproot4 as rt
import numpy as np
import matplotlib
import ROOT as r
#from tdrStyle import setTDRStyle
#setTDRStyle()
import CMS_lumi

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


def fillGaps(h2):
    nx = h2.GetNbinsX()
    ny = h2.GetNbinsY()
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            if h2.GetBinContent(i,j)==0:
                if((j-i)>8 ):
                    continue
                fillValue = h2.GetBinContent(i-1,j)
                h2.SetBinContent(i,j,fillValue)
    return h2

def significances2D():
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')

    h2D = r.TH2D("hSignificance","",len(MX)-1,MX,len(MY)-1,MY)
    minSignificance = {"value":1.0, "mass_point":"placeholder"}

    for mx in MX:
        for my in MY:
            if((mx<1200 and my>200)):
                continue
            if((mx<1300 and my>300)):
                continue
            tempFileName = "limits/significances/MX{0}_MY{1}.root".format(int(mx),int(my))
            if not (os.path.exists(tempFileName)):
                    continue
            fTemp = r.TFile.Open(tempFileName)
            try:
                limTree = fTemp.Get("limit")
                limTree.GetEntry(0)
            except:
                print("Bad file: MX{0}_MY{1}.root".format(int(mx),int(my)))
                continue
            significance = limTree.limit
            if(significance<minSignificance["value"]):
                minSignificance["value"] = significance
                minSignificance["mass_point"] = "MX{0}_MY{1}".format(int(mx),int(my))
            binx = h2D.GetXaxis().FindBin(mx)
            biny = h2D.GetYaxis().FindBin(my)
            h2D.SetBinContent(binx,biny,significance)


    #h2D = fillGaps(h2D)

    c = r.TCanvas("","",2000,2000)
    c.SetRightMargin(0.20)
    c.SetLeftMargin(0.20)
    c.SetTopMargin(0.10)
    c.SetBottomMargin(0.17)
    c.SetLogz()
    h2D.GetXaxis().SetTitleSize(.05);
    h2D.GetXaxis().SetNdivisions(6);
    h2D.GetXaxis().SetRangeUser(900,4000);
    h2D.GetYaxis().SetRangeUser(60,700)
    h2D.GetXaxis().SetLabelSize(.04);
    h2D.GetYaxis().SetTitleSize(.05);
    h2D.GetYaxis().SetLabelSize(.04);
    h2D.GetYaxis().SetTitle("M_{Y} [GeV]")
    h2D.GetXaxis().SetTitle("M_{X} [GeV]")
    h2D.GetZaxis().SetTitle("Observed significance (p-value)")
    h2D.GetZaxis().SetTitleSize(.05);
    h2D.SetMaximum(1)
    h2D.SetMinimum(10e-5)
    h2D.SetTitleOffset(1.2,"Y")
    h2D.SetTitleOffset(1.2,"Z")
    h2D.Draw("colz")

    # l = r.TLatex();
    # l.SetTextSize(0.05);
    # l.DrawLatexNDC(0.80,0.92,"138 fb^{-1}")

    pad = r.gPad
    CMS_lumi.CMS_lumi(pad,  iPeriod=1,  iPosX=1, sim=False )   
       
    print("Min significance {0} for {1}".format(minSignificance["value"],minSignificance["mass_point"]))

    c.SaveAs("significance.pdf")
    c.SaveAs("significance.png")


def lims2D(obs=False,outputFile="2DexpLims.png"):
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600],dtype='float64')

    h2D = r.TH2D("hLims","",len(MX)-1,MX,len(MY)-1,MY)

    for mx in MX:
        for my in MY:
            if((mx<1200 and my>200)):
                continue
            if((mx<1300 and my>300)):
                continue
            tempFileName = "limits/obsLimits/MX{0}_MY{1}.root".format(int(mx),int(my))
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
            limit = limTree.limit*0.5    
            binx = h2D.GetXaxis().FindBin(mx)
            biny = h2D.GetYaxis().FindBin(my)
            h2D.SetBinContent(binx,biny,limit)
            #print(mx,my,limit)


    #h2D = fillGaps(h2D)

    c = r.TCanvas("","",2000,2000)
    c.SetRightMargin(0.20)
    c.SetLeftMargin(0.20)
    c.SetTopMargin(0.10)
    c.SetBottomMargin(0.17)
    c.SetLogz()
    h2D.GetXaxis().SetTitleSize(.06);
    h2D.GetXaxis().SetNdivisions(6);
    h2D.GetXaxis().SetRangeUser(900,4000);
    h2D.GetYaxis().SetRangeUser(60,700)
    h2D.GetXaxis().SetLabelSize(.04);
    h2D.GetYaxis().SetTitleSize(.06);
    h2D.GetYaxis().SetLabelSize(.04);
    h2D.GetYaxis().SetTitle("M_{Y} [GeV]")
    h2D.GetXaxis().SetTitle("M_{X} [GeV]")
    if not obs:
        h2D.GetZaxis().SetTitle("Expected exclusion limits [fb]")
    else:
        h2D.GetZaxis().SetTitle("Observed exclusion limits [fb]")
    h2D.GetZaxis().SetTitleSize(.05);
    h2D.SetMaximum(100)
    h2D.SetMinimum(0.05)
    h2D.SetTitleOffset(1.3,"Y")
    h2D.Draw("colz")

    #l = r.TLatex();
    #l.SetTextSize(0.05);
    #l.DrawLatexNDC(0.80,0.92,"138 fb^{-1}")

    pad = r.gPad
    CMS_lumi.CMS_lumi(pad,  iPeriod=1,  iPosX=1, sim=False )       

    c.SaveAs(outputFile)
    c.SaveAs(outputFile.replace(".png",".pdf"))



significances2D()
#lims2D(outputFile="2DexpLims.png")
lims2D(obs=True,outputFile="2DobsLims.png")
lims2D(obs=False,outputFile="2DdataExpLims.png")
