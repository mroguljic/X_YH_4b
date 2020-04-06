import ROOT as r


def calcEfficiency(hPass,hFail,name):
#Returns TEfficiency with *properly* calculated stat. uncertainties
    hPass.Sumw2()
    hFail.Sumw2()

    hTot    = hPass.Clone("tot")
    hTot.Add(hPass,hFail)
    eff     = r.TEfficiency(hPass,hTot)
    eff.SetName(name)
    return eff


def bTagEffPlot(outputFile,massPoints):
    wp0_5 = r.TFile("outputWP_0.5.root")
    wp0_7 = r.TFile("outputWP_0.7.root")
    wp0_9 = r.TFile("outputWP_0.9.root")

    wps = [wp0_5,wp0_7,wp0_9]

    colorCodes = [1,2,4,7,8,20,29]
    nColors    = len(colorCodes)

    c = r.TCanvas("c","c",3000,2200)
    r.gStyle.SetOptStat(0)
    c.Divide(2,2)

    h1Dummy = r.TH2F("h1Dummy","Y bTagHbb efficiency WP=0.5",100,0.,2000.,100,0.,1.00)
    h2Dummy = r.TH2F("h2Dummy","Y bTagHbb efficiency WP=0.7",100,0.,2000.,100,0.,1.00)
    h3Dummy = r.TH2F("h3Dummy","Y bTagHbb efficiency WP=0.9",100,0.,2000.,100,0.,1.00)
    h4Dummy = r.TH2F("h4Dummy","H bTagHbb efficiency" ,100,0.,2000.,100,0.,1.00)

    h1Dummy.SetXTitle("Pt [GeV]")
    h2Dummy.SetXTitle("Pt [GeV]")
    h3Dummy.SetXTitle("Pt [GeV]")
    h4Dummy.SetXTitle("Pt [GeV]")

    h1Dummy.SetYTitle("N_pass/N_total")
    h2Dummy.SetYTitle("N_pass/N_total")
    h3Dummy.SetYTitle("N_pass/N_total")
    h4Dummy.SetYTitle("N_pass/N_total")

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


    for i,massPoint in enumerate(massPoints):
 
        colorIdx = i%nColors
        color    = colorCodes[colorIdx]

        h1      = wp0_5.Get("YMass_{0}/bTagHbb_eff_YMass_{0}".format(massPoint))#TEfficiency actually, not a TH1F
        h2      = wp0_7.Get("YMass_{0}/bTagHbb_eff_YMass_{0}".format(massPoint))#TEfficiency actually, not a TH1F
        h3      = wp0_9.Get("YMass_{0}/bTagHbb_eff_YMass_{0}".format(massPoint))

        h1.SetTitle("Y mass = {0} GeV".format(massPoint))
        h2.SetTitle("Y mass = {0} GeV".format(massPoint))
        h3.SetTitle("Y mass = {0} GeV".format(massPoint))

        h1.SetLineColor(color) 
        h2.SetLineColor(color) 
        h3.SetLineColor(color) 

        c.cd(1)
        h1.Draw("SAME")
        c.cd(2)
        h2.Draw("SAME")
        c.cd(3)
        h3.Draw("SAME")
        c.Modified()
        c.Update()

    c.cd(4)
    histosForLegend = []
    for i,wp in enumerate(wps):
        pts = [0.5,0.7,0.9]
        colorIdx = i%nColors
        color    = colorCodes[colorIdx]
        h4 = wp.Get("H/bTagHbb_eff_H")
        histosForLegend.append(h4) #need to do this since they have the same object name
        h4.SetTitle("WP = {0}".format(pts[i]))
        h4.SetLineColor(color) 
        h4.Draw("SAME")
        c.Modified()
        c.Update()

    c.cd(3)
    legend3 = r.TLegend(0.1,0.5,0.9,0.9)
    legend3.SetBorderSize(0)
    legend3.SetFillStyle(0)
    for massPoint in massPoints:
        legend3.AddEntry("bTagHbb_eff_YMass_{0}".format(massPoint)),
    c.cd(3)
    legend3.Draw()

    c.cd(4)
    legend4 = r.TLegend(0.1,0.1,0.4,0.4)
    legend4.SetBorderSize(0)
    legend4.SetFillStyle(0)
    for h in histosForLegend:
        legend4.AddEntry(h)
    c.cd(4)
    legend4.Draw()

    c.SaveAs(outputFile)

def updateFile(inFile,massPoints = ["90","100","125","150","200","250","300","400","500","600","700"]):
#calculates the TEfficiency and saves it
    f = r.TFile.Open(inFile,"update")
    YmassPoints = ["90","100","125","150","200","250","300","400","500","600","700"]
    directories = []
    for massPoint in YmassPoints:
        directories.append("YMass_{0}".format(massPoint))


    for directory in directories:
        name  = "bTagHbb_eff_{0}".format(directory)
        hPass = f.Get(directory+"/YpassedTagger_pt")
        hFail = f.Get(directory+"/YfailedTagger_pt")
        eff   = calcEfficiency(hPass,hFail,name)
        f.cd(directory)
        eff.Write()

    directory = "H"
    name = "bTagHbb_eff_H"
    hPass = f.Get(directory+"/HpassedTagger_pt")
    hFail = f.Get(directory+"/HfailedTagger_pt")
    eff = calcEfficiency(hPass,hFail,name)
    f.cd(directory)
    eff.Write()

#updateFile("outputWP_0.5.root")
#updateFile("outputWP_0.7.root")
#updateFile("outputWP_0.9.root")

YmassPoints = ["100","150","200","300","500","700"]
bTagEffPlot("test.png",YmassPoints)