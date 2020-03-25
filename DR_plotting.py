import ROOT as r

def plotSingleMassPoint(inputfile,outfile,massPoint):
    inFile  = r.TFile(inputfile)
    h1      = inFile.Get("Heffiencies_{0}".format(massPoint))
    h2      = inFile.Get("Yeffiencies_{0}".format(massPoint))
    h3      = inFile.Get("Hak8mass_{0}".format(massPoint))
    h4      = inFile.Get("Yak8mass_{0}".format(massPoint))

    h1.SetXTitle("Matched boson Pt [GeV]")
    h1.SetYTitle("AK8 matching efficiency")
    h2.SetXTitle("Matched boson Pt [GeV]")
    h2.SetYTitle("AK8 matching efficiency")
    h3.SetXTitle("Higgs matched AK8 jet mass [GeV]")
    h4.SetXTitle("Y matched AK8 jet mass [GeV]")

    c = r.TCanvas("c","c",900,700)
    r.gStyle.SetOptStat(111111)
    c.Divide(2,2)
    c.cd(1)
    h1.Draw()
    c.cd(2)
    h2.Draw()
    c.cd(3)
    h3.Draw()
    c.cd(4)
    h4.Draw()
    c.Modified()
    c.Update()
    c.SaveAs(outfile)


def singleCanvas(inputfile,outputFile,massPoints):
    inFile  = r.TFile(inputfile)

    colorCodes = [1,2,4,7,8,20,29]
    nColors    = len(colorCodes)

    c = r.TCanvas("c","c",1500,1200)
    r.gStyle.SetOptStat(0)
    c.Divide(2,2)
#---Setting up the axes range, label and plot titles---#
    h1Dummy = r.TH2F("h1Dummy","DR matching efficiency for H",100,0.,2000.,100,0.,1.05)
    h2Dummy = r.TH2F("h2Dummy","DR matching efficiency for Y",100,0.,2000.,100,0.,1.05)
    h3Dummy = r.TH2F("h3Dummy","DR H-matched AK8 softdrop mass",100,0.,400.,100,0.,8400.)
    h4Dummy = r.TH2F("h4Dummy","DR Y-matched AK8 softdrop mass",100,0.,500.,100,0.,9200.)
    h1Dummy.SetXTitle("Pt [GeV]")
    h2Dummy.SetXTitle("Pt [GeV]")
    h1Dummy.SetYTitle("N_matched/N_total")
    h2Dummy.SetYTitle("N_matched/N_total")
    h3Dummy.SetXTitle("AK8 softdrop mass [GeV]")
    h4Dummy.SetXTitle("AK8 softdrop mass [GeV]")
    h1Dummy.GetXaxis().SetTitleSize(0.05)
    h2Dummy.GetXaxis().SetTitleSize(0.05)
    h3Dummy.GetXaxis().SetTitleSize(0.05)
    h4Dummy.GetXaxis().SetTitleSize(0.05)
    h1Dummy.GetYaxis().SetTitleSize(0.05)
    h2Dummy.GetYaxis().SetTitleSize(0.05)
    h3Dummy.GetYaxis().SetTitleSize(0.05)
    h4Dummy.GetYaxis().SetTitleSize(0.05)
    c.cd(1)
    h1Dummy.Draw()
    c.cd(2)
    h2Dummy.Draw()
    c.cd(3)
    h3Dummy.Draw()
    c.cd(4)
    h4Dummy.Draw()
#-----------------------------------------------------#
    for i,massPoint in enumerate(massPoints):
 
        colorIdx = i%nColors
        color    = colorCodes[colorIdx]

        h1      = inFile.Get("effMatchH_{0}".format(massPoint))#TEfficiency actually, not a TH1F
        h2      = inFile.Get("effMatchY_{0}".format(massPoint))#TEfficiency actually, not a TH1F
        h3      = inFile.Get("Hak8mass_{0}".format(massPoint))
        h4      = inFile.Get("Yak8mass_{0}".format(massPoint))

        h1.SetTitle("Y mass = {0} GeV".format(massPoint))
        h2.SetTitle("Y mass = {0} GeV".format(massPoint))
        h3.SetTitle("Y mass = {0} GeV".format(massPoint))
        h4.SetTitle("Y mass = {0} GeV".format(massPoint))

        h1.SetLineColor(color) 
        h2.SetLineColor(color) 
        h3.SetLineColor(color) 
        h4.SetLineColor(color)
        #h1.SetFillColor(color) 
        #h2.SetFillColor(color) 
        h3.SetFillColor(color) 
        h4.SetFillColor(color)
        if(i==0):
            c.cd(1)
            h1.Draw("SAME")
        c.cd(2)
        h2.Draw("SAME")
        c.cd(3)
        h3.Draw("SAME")
        c.cd(4)
        h4.Draw("SAME")
        c.Modified()
        c.Update()

    c.cd(1)
    legend1 = r.TLegend(0.6,0.1,0.9,0.4)
    legend1.AddEntry("effMatchH_{0}".format(massPoints[0]))
    c.cd(2)
    legend2 = r.TLegend(0.6,0.1,0.9,0.4)
    for massPoint in massPoints:
        legend2.AddEntry("effMatchY_{0}".format(massPoint))
    c.cd(3)
    legend3 = r.TLegend(0.6,0.1,0.9,0.4)
    for massPoint in massPoints:
        legend3.AddEntry("Hak8mass_{0}".format(massPoint))
    c.cd(4)
    legend4 = r.TLegend(0.6,0.4,0.9,0.7)
    for massPoint in massPoints:
        legend4.AddEntry("Yak8mass_{0}".format(massPoint))

    c.cd(1)
    legend1.Draw()
    c.cd(2)
    legend2.Draw()
    c.cd(3)
    legend3.Draw()
    c.cd(4)
    legend4.Draw()

    # c.cd(1).BuildLegend(0.6,0.1,0.9,0.4)
    # c.cd(2).BuildLegend(0.6,0.1,0.9,0.4)
    # c.cd(3).BuildLegend(0.6,0.1,0.9,0.4)
    # c.cd(4).BuildLegend(0.6,0.1,0.9,0.4)



    c.SaveAs(outputFile)
        #c.SaveAs(str(massPoint)+outputFile)


if __name__ == '__main__':
    massPoints = ["90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
    # for massPoint in massPoints:
    #     outfile = "allMassPoints/massY_{0}GeV.png".format(massPoint)
    #     plotSingleMassPoint("test.root",outfile,massPoint)

    mPointsForSingleCanvas = ["100","150","200","250","300","400"]
    singleCanvas("test_eff.root","singleCanvas.png",mPointsForSingleCanvas)