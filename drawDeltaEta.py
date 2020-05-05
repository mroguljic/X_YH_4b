import ROOT as r
from time import sleep

f = r.TFile.Open("deltaEta.root")

tree = f.Get("test")




hDummy = r.TH2F("hDummy","FatJet_eta[0]-FatJet_eta[1]",50,-4.5,4.5,100,0.,0.07)

massPoints = [200,400,800,1000]
colorCodes = [1,2,4,30,8,20,29]
nColors    = len(colorCodes)

histograms = []
for point in massPoints:
    hName = "M_Y={0}".format(point)
    hTemp = r.TH1F(hName,hName,50,-4.5,4.5)
    tree.Draw("deltaEta>>{0}".format(hName),"GenModel_YMass_{0}==1".format(point),"norm")
    histograms.append(hTemp)
    #hTemp.Draw("same")
#r.htemp.SetLineColor(r.kOrange)
c = r.TCanvas("c","c",3000,2200)
c.cd()
hDummy.Draw()

legend = r.TLegend(0.1,0.5,0.3,0.9)
legend.SetBorderSize(0)
legend.SetFillStyle(0)

for i,h in  enumerate(histograms):
    colorIdx = i%nColors
    color    = colorCodes[colorIdx]
    h.SetLineColor(color)
    h.SetLineWidth(2)
    h.SetStats(0)
    h.Draw("same")
    print(h.GetName())
    legend.AddEntry(h.GetName())

legend.Draw()
r.gStyle.SetOptStat(0000)
r.gPad.Modified()
r.gPad.Update()
c.SaveAs("deltaEta.png")
