import ROOT as r

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0)
c = r.TCanvas("","",3000,1500)
c.cd()


templateDir = "../results/templates_hadronic/2017/scaled/"
templates   = ["TTbar17.root","TTbarIncl17.root","TTbar_pt_incl.root"]
templPrefix = ["TTbar","TTbarIncl","TTbar_pt_incl"]
histos      = []

for i,template in enumerate(templates):
    f     = r.TFile.Open(templateDir+template)
    hTemp = f.Get(templPrefix[i]+"_MTT_skim_nom")
    hTemp.SetDirectory(0)
    hTemp.SetName("h"+str(i))
    histos.append(hTemp)
    f.Close()

labels = ["Stitched (Had,Semi,MTT700,1000)","Had+Semi MTT inclusive","Had MTT inclusive"]
colors = [r.kRed,r.kBlue,r.kViolet]


leg = r.TLegend(.50,.52,.97,.83)
leg.SetBorderSize(0)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.035)

for i,h in enumerate(histos):
    h.SetLineWidth(4-i)
    h.SetLineColor(colors[i])
    if(i==0):
        h.Draw("HIST")
    else:
        h.Draw("HIST same")
    leg.AddEntry(h,labels[i])
leg.Draw()
c.SaveAs("MTT_afterSkimming.png")