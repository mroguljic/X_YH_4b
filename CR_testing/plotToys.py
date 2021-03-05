import ROOT as r

r.gROOT.SetBatch(True)

for year in ["16","17","18"]:
	for region in ["L","T"]:

		f 		= r.TFile.Open("CR_{0}_{1}/higgsCombinegof.GenerateOnly.mH120.10.root".format(region, year))
		rooVar 	= r.RooRealVar("CMS_th1x","Probe jet mass",15,0,15);
		frame 	= rooVar.frame(15)

		c  		= r.TCanvas("","",1500,1500)
		c.cd()
		for i in range(1,500):
			dataset = f.Get("toys/toy_{0}".format(i))
		 	dataset.plotOn(frame)

		# g      	= r.TFile.Open("CR_{0}_{1}/morphedWorkspace.root".format(region, year))
		# fitW 	= g.Get("w")
		# data 	= fitW.data("data_obs")
		# data.plotOn(frame)

		frame.Draw()
		c.SaveAs("toys_CR_{0}_{1}.png".format(region, year))

