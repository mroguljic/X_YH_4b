import ROOT as r
r.gROOT.SetBatch()

r.gStyle.SetPaintTextFormat(".2f")

def plotTrigEff(hPass,hTot,outputFile,RebinX=1,RebinY=1,xTitle="",yTitle=""):
    h1 = hPass.Clone()
    h1.SetDirectory(0)
    h2 = hTot.Clone()
    h2.SetDirectory(0)

    h1.RebinX(RebinX)
    h1.RebinY(RebinY)
    h2.RebinX(RebinX)
    h2.RebinY(RebinY)
    allTriggersEff = r.TEfficiency(h1,h2)
    allTriggersEff.SetTitle(";{0};{1}".format(xTitle,yTitle))
    c = r.TCanvas("","",1000,1000)
    allTriggersEff.Draw("colz text 45")
    c.SaveAs(outputFile)

samples = {"QCD","ttbar","X1400_Y100","X1000_Y100","X2000_Y100"}
for sample in samples:
    f = r.TFile.Open("results/histograms/lumiScaled/{0}_normalized.root".format(sample))
    hTot = f.Get("{0}_noTriggers".format(sample))
    hAllTrigers = f.Get("{0}_triggersNoBtag".format(sample))
    hwithoutBTrig = f.Get("{0}_triggersAll".format(sample))
    plotTrigEff(hAllTrigers,hTot,"results/plots/{0}_allTrigger.png".format(sample),RebinX=10,RebinY=5,xTitle="m_{jj} / 100 GeV",yTitle="m_{j,y} / 50 GeV")
    plotTrigEff(hwithoutBTrig,hTot,"results/plots/{0}_noBTrigger.png".format(sample),RebinX=10,RebinY=5,xTitle="m_{jj} / 100 GeV",yTitle="m_{j,y} / 50 GeV")
    f.Close()