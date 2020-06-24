import ROOT as r

f = r.TFile.Open("QCD_merge.root")

h_TT = f.Get("QCD_mjHY_mjH_pnet_TT")
h_ATT = f.Get("QCD_mjHY_mjH_pnet_ATT")
h_LL = f.Get("QCD_mjHY_mjH_pnet_LL")
h_ALL = f.Get("QCD_mjHY_mjH_pnet_ATL")

h_TT.RebinX(10)
#h_TT.RebinY(10)
h_ATT.RebinX(10)
#h_ATT.RebinY(10)
h_LL.RebinX(10)
#h_TT.RebinY(10)
h_ALL.RebinX(10)
#h_ATT.RebinY(10)
h_TT.GetXaxis().SetRangeUser(700., 3000.);
h_TT.GetYaxis().SetRangeUser(80., 230.);
h_ATT.GetXaxis().SetRangeUser(700., 3000.);
h_ATT.GetYaxis().SetRangeUser(80., 230.);

h_LL.GetXaxis().SetRangeUser(700., 3000.);
h_LL.GetYaxis().SetRangeUser(80., 230.);
h_ALL.GetXaxis().SetRangeUser(700., 3000.);
h_ALL.GetYaxis().SetRangeUser(80., 230.);


Rpf_TT = h_TT.Clone("Rpf_TT")
Rpf_TT.Divide(h_TT,h_ATT)

Rpf_LL = h_TT.Clone("Rpf_LL")
Rpf_LL.Divide(h_LL,h_ALL)


r.gROOT.SetBatch(True) 
#r.gROOT.SetOptStat(0)
c = r.TCanvas("c","c",1000,1000)
Rpf_LL.Draw("LEGO")
r.gPad.Update()
statBox = Rpf_LL.FindObject("stats")
statBox.SetOptStat(0)
c.SaveAs("Rpf_LL.png")
c.Clear()

Rpf_TT.Draw("LEGO")
r.gPad.Update()
statBox = Rpf_TT.FindObject("stats")
statBox.SetOptStat(0)
c.SaveAs("Rpf_TT.png")