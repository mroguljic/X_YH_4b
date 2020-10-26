import ROOT as r

sigSamples = {
	"X1600_Y90" : "results/histograms/lumiScaled/X1600_Y90_normalized.root",
	"X1600_Y100": "results/histograms/lumiScaled/X1600_Y100_normalized.root",
	"X1600_Y125": "results/histograms/lumiScaled/X1600_Y125_normalized.root",
	"X1600_Y150": "results/histograms/lumiScaled/X1600_Y150_normalized.root",
	"X1600_Y200": "results/histograms/lumiScaled/X1600_Y200_normalized.root",
	"X1600_Y250": "results/histograms/lumiScaled/X1600_Y250_normalized.root",
	"X1600_Y300": "results/histograms/lumiScaled/X1600_Y300_normalized.root"
}

bkgSamples = {
	"QCD"   : "results/histograms/lumiScaled/QCD_normalized.root",
	"ttbar" : "results/histograms/lumiScaled/ttbar_normalized.root"
}

def rebin2d(h2d):
	#x is mY from 0 to 400, 10GeV bin
	#y is mJJ from 0 to 4000, 10GeV bin
	#returns rebined 2d hist, under/overflow included
	xmin = 60
	xmax = 360
	ymin = 1000
	ymax = 3000
	hRebined = r.TH2F("hTemp","",15,xmin,xmax,20,ymin,ymax)
	NbinsX 	 = h2d.GetNbinsX()
	NbinsY 	 = h2d.GetNbinsY()
	xaxis = h2d.GetXaxis()
	yaxis = h2d.GetYaxis()
	for i in range(NbinsX+2):
		for j in range(NbinsY+2):
			x = xaxis.GetBinCenter(i)
			y = yaxis.GetBinCenter(j)
			value = h2d.GetBinContent(i,j)
			if(value==0):
				continue
			if(x<xmin):
				x = xmin+0.1
			if(x>xmax):
				x = xmax-0.1
			if(y<ymin):
				y = ymin+0.1
			if(y>ymax):
				y = ymax-0.1
			hRebined.Fill(x,y,value)
	return hRebined



tagger = "pnet"
histos  = []
h_pseudoData_LL = r.TH2F("mJJ_mjY_LL_data_obs","",15,60,360,20,1000,3000)
h_pseudoData_TT = r.TH2F("mJJ_mjY_TT_data_obs","",15,60,360,20,1000,3000)

for sample, fileName in sigSamples.items():
	print(sample)
	h2dName    = "mJJ_mY_REGION_{0}".format(sample)
	h2dName    = h2dName.replace("_X","_MX")
	h2dName    = h2dName.replace("_Y","_MY")
	fTemp      = r.TFile.Open(fileName)
	TT_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_TT".format(sample,tagger))
	TT_h2d 	   = TT_h3dTemp.Project3D("zxe")
	TT_rebined = rebin2d(TT_h2d)
	#TT_h2d 	   = TT_h3dTemp.Project3D("xze") #if you want to flip axes
	TT_rebined.SetName(h2dName.replace("REGION","TT"))
	TT_rebined.SetTitle(";mj_Y [GeV];mJJ [GeV]")
	TT_rebined.SetDirectory(0)
	histos.append(TT_rebined)

	LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
	LL_h2d 	   = LL_h3dTemp.Project3D("zxe")
	LL_rebined = rebin2d(LL_h2d)
	#LL_h2d 	   = LL_h3dTemp.Project3D("xze") #if you want to flip axes
	LL_rebined.SetName(h2dName.replace("REGION","LL"))
	LL_rebined.SetTitle(";mj_Y [GeV];mJJ [GeV]")
	LL_rebined.SetDirectory(0)
	histos.append(LL_rebined)

for sample, fileName in bkgSamples.items():
	print(sample)
	h2dName    = "mJJ_mY_REGION_{0}".format(sample)
	if(sample=="ttbar"):
		h2dName = h2dName.replace("ttbar","TTbar")
	fTemp      = r.TFile.Open(fileName)
	TT_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_TT".format(sample,tagger))
	TT_h2d 	   = TT_h3dTemp.Project3D("zxe")
	TT_rebined = rebin2d(TT_h2d)
	#TT_h2d 	   = TT_h3dTemp.Project3D("xze") #if you want to flip axes
	TT_rebined.SetName(h2dName.replace("REGION","TT"))
	TT_rebined.SetTitle(";mj_Y [GeV];mJJ [GeV]")
	TT_rebined.SetDirectory(0)
	histos.append(TT_rebined)
	h_pseudoData_TT.Add(TT_rebined)

	LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
	LL_h2d 	   = LL_h3dTemp.Project3D("zxe")
	LL_rebined = rebin2d(LL_h2d)
	#LL_h2d 	   = LL_h3dTemp.Project3D("xze") #if you want to flip axes
	LL_rebined.SetName(h2dName.replace("REGION","LL"))
	LL_rebined.SetTitle(";mj_Y [GeV];mJJ [GeV]")
	LL_rebined.SetDirectory(0)
	histos.append(LL_rebined)
	h_pseudoData_LL.Add(LL_rebined)

histos.append(h_pseudoData_LL)
histos.append(h_pseudoData_TT)


f = r.TFile.Open("{0}_templates.root".format(tagger),"RECREATE")
f.cd()
for h in histos:
	h.Write()
f.Close()


	#LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
