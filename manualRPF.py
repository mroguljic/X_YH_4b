import ROOT as r

fileDict = {"QCD":"./results/histograms/QCD_merge.root","ttbar":"./results/histograms/ttbar.root"}
taggers = ["pnet","dak8"]

for key, value in fileDict.items():
	f = r.TFile.Open(value)
	r.gROOT.SetBatch(True) 
	for tagger in taggers:

		h_TT = f.Get("{0}_mjHY_mjH_{1}_TT".format(key,tagger))
		h_ATT = f.Get("{0}_mjHY_mjH_{1}_ATT".format(key,tagger))
		h_LL = f.Get("{0}_mjHY_mjH_{1}_LL".format(key,tagger))
		h_ALL = f.Get("{0}_mjHY_mjH_{1}_ATL".format(key,tagger))

		h_TT.RebinX(10)
		h_ATT.RebinX(10)
		h_LL.RebinX(10)
		h_ALL.RebinX(10)

		h_TT.GetXaxis().SetRangeUser(700., 3000.);
		h_TT.GetYaxis().SetRangeUser(80., 230.);
		h_ATT.GetXaxis().SetRangeUser(700., 3000.);
		h_ATT.GetYaxis().SetRangeUser(80., 230.);

		h_LL.GetXaxis().SetRangeUser(700., 3000.);
		h_LL.GetYaxis().SetRangeUser(80., 230.);
		h_ALL.GetXaxis().SetRangeUser(700., 3000.);
		h_ALL.GetYaxis().SetRangeUser(80., 230.);

		c2 = r.TCanvas("c","c",2000,2000)
		c2.SetLogy()

		c2.Divide(2,2)

		h_mJJ_TT = h_TT.ProjectionX()
		h_mJJ_TT.SetTitle("mJJ_TT")
		h_mH_TT = h_TT.ProjectionY()
		h_mH_TT.SetTitle("mH_TT")

		h_mJJ_LL = h_LL.ProjectionX()
		h_mJJ_LL.SetTitle("mJJ_LL")
		h_mH_LL = h_LL.ProjectionY()
		h_mH_LL.SetTitle("mH_LL")

		c2.cd(1)
		r.gPad.SetLogy()
		h_mJJ_TT.Draw("hist")

		c2.cd(2)
		r.gPad.SetLogy()
		h_mH_TT.Draw("hist")

		c2.cd(3)
		r.gPad.SetLogy()
		h_mJJ_LL.Draw("hist")

		c2.cd(4)
		r.gPad.SetLogy()
		h_mH_LL.Draw("hist")

		c2.Update()
		c2.SaveAs("{0}_spectra_{1}.png".format(key,tagger))
		c2.Clear()

		c2.Divide(2,2)

		h_mJJ_ATT = h_ATT.ProjectionX()
		h_mJJ_ATT.SetTitle("mJJ_ATT")
		h_mH_ATT = h_ATT.ProjectionY()
		h_mH_ATT.SetTitle("mH_ATT")

		h_mJJ_ALL = h_ALL.ProjectionX()
		h_mJJ_ALL.SetTitle("mJJ_ALL")
		h_mH_ALL = h_ALL.ProjectionY()
		h_mH_ALL.SetTitle("mH_ALL")

		c2.cd(1)
		r.gPad.SetLogy()
		h_mJJ_ATT.Draw("hist")

		c2.cd(2)
		r.gPad.SetLogy()
		h_mH_ATT.Draw("hist")

		c2.cd(3)
		r.gPad.SetLogy()
		h_mJJ_ALL.Draw("hist")

		c2.cd(4)
		r.gPad.SetLogy()
		h_mH_ALL.Draw("hist")

		c2.Update()
		c2.SaveAs("{0}_anti_spectra_{1}.png".format(key,tagger))



		h_TT.RebinY(4)
		h_ATT.RebinY(4)
		h_LL.RebinY(4)
		h_ALL.RebinY(4)



		Rpf_TT = h_TT.Clone("{0}_Rpf_{1}_TT".format(key,tagger))
		Rpf_TT.Divide(h_TT,h_ATT)
		Rpf_LL = h_TT.Clone("{0}_Rpf_{1}_LL".format(key,tagger))
		Rpf_LL.Divide(h_LL,h_ALL)

		Rpf_TT.GetXaxis().SetRangeUser(700., 3000.);
		Rpf_TT.GetYaxis().SetRangeUser(80., 230.);
		Rpf_LL.GetXaxis().SetRangeUser(700., 3000.);
		Rpf_LL.GetYaxis().SetRangeUser(80., 230.);

		#r.gROOT.SetOptStat(0)
		c = r.TCanvas("c","c",1000,1000)
		Rpf_LL.Draw("LEGO")
		r.gPad.Update()
		statBox = Rpf_LL.FindObject("stats")
		statBox.SetOptStat(0)
		c.SaveAs("{0}_Rpf_{1}_LL.png".format(key,tagger))
		c.Clear()

		Rpf_TT.Draw("LEGO")
		r.gPad.Update()
		statBox = Rpf_TT.FindObject("stats")
		statBox.SetOptStat(0)
		c.SaveAs("{0}_Rpf_{1}_TT.png".format(key,tagger))
		c.Clear()