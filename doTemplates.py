import ROOT as r

sigSamples = {
    "X800_Y60" : "results/histograms/lumiScaled/X800_Y60_normalized.root",
    "X800_Y80" : "results/histograms/lumiScaled/X800_Y80_normalized.root",
    "X800_Y90" : "results/histograms/lumiScaled/X800_Y90_normalized.root",
    "X800_Y100": "results/histograms/lumiScaled/X800_Y100_normalized.root",
    "X800_Y125": "results/histograms/lumiScaled/X800_Y125_normalized.root",
    "X800_Y150": "results/histograms/lumiScaled/X800_Y150_normalized.root",
    "X800_Y200": "results/histograms/lumiScaled/X800_Y200_normalized.root",
    "X800_Y250": "results/histograms/lumiScaled/X800_Y250_normalized.root",
    "X800_Y300": "results/histograms/lumiScaled/X800_Y300_normalized.root",
    "X800_Y400": "results/histograms/lumiScaled/X800_Y400_normalized.root",
    "X900_Y60" : "results/histograms/lumiScaled/X900_Y60_normalized.root",
    "X900_Y80" : "results/histograms/lumiScaled/X900_Y80_normalized.root",
    "X900_Y90" : "results/histograms/lumiScaled/X900_Y90_normalized.root",
    "X900_Y100": "results/histograms/lumiScaled/X900_Y100_normalized.root",
    "X900_Y125": "results/histograms/lumiScaled/X900_Y125_normalized.root",
    "X900_Y150": "results/histograms/lumiScaled/X900_Y150_normalized.root",
    "X900_Y200": "results/histograms/lumiScaled/X900_Y200_normalized.root",
    "X900_Y250": "results/histograms/lumiScaled/X900_Y250_normalized.root",
    "X900_Y300": "results/histograms/lumiScaled/X900_Y300_normalized.root",
    "X900_Y400": "results/histograms/lumiScaled/X900_Y400_normalized.root",
    "X1000_Y90" : "results/histograms/lumiScaled/X1000_Y90_normalized.root",
    "X1000_Y100": "results/histograms/lumiScaled/X1000_Y100_normalized.root",
    "X1000_Y125": "results/histograms/lumiScaled/X1000_Y125_normalized.root",
    "X1000_Y150": "results/histograms/lumiScaled/X1000_Y150_normalized.root",
    "X1000_Y200": "results/histograms/lumiScaled/X1000_Y200_normalized.root",
    "X1000_Y250": "results/histograms/lumiScaled/X1000_Y250_normalized.root",
    "X1000_Y300": "results/histograms/lumiScaled/X1000_Y300_normalized.root",
    "X1000_Y400": "results/histograms/lumiScaled/X1000_Y400_normalized.root",
    "X1200_Y90" : "results/histograms/lumiScaled/X1200_Y90_normalized.root",
    "X1200_Y100": "results/histograms/lumiScaled/X1200_Y100_normalized.root",
    "X1200_Y125": "results/histograms/lumiScaled/X1200_Y125_normalized.root",
    "X1200_Y150": "results/histograms/lumiScaled/X1200_Y150_normalized.root",
    "X1200_Y200": "results/histograms/lumiScaled/X1200_Y200_normalized.root",
    "X1200_Y250": "results/histograms/lumiScaled/X1200_Y250_normalized.root",
    "X1200_Y300": "results/histograms/lumiScaled/X1200_Y300_normalized.root",
    "X1200_Y400": "results/histograms/lumiScaled/X1200_Y400_normalized.root",
    "X1400_Y90" : "results/histograms/lumiScaled/X1400_Y90_normalized.root",
    "X1400_Y100": "results/histograms/lumiScaled/X1400_Y100_normalized.root",
    "X1400_Y125": "results/histograms/lumiScaled/X1400_Y125_normalized.root",
    "X1400_Y150": "results/histograms/lumiScaled/X1400_Y150_normalized.root",
    "X1400_Y200": "results/histograms/lumiScaled/X1400_Y200_normalized.root",
    "X1400_Y250": "results/histograms/lumiScaled/X1400_Y250_normalized.root",
    "X1400_Y300": "results/histograms/lumiScaled/X1400_Y300_normalized.root",
    "X1400_Y400": "results/histograms/lumiScaled/X1400_Y400_normalized.root",
	"X1600_Y90" : "results/histograms/lumiScaled/X1600_Y90_normalized.root",
	"X1600_Y100": "results/histograms/lumiScaled/X1600_Y100_normalized.root",
	"X1600_Y125": "results/histograms/lumiScaled/X1600_Y125_normalized.root",
	"X1600_Y150": "results/histograms/lumiScaled/X1600_Y150_normalized.root",
	"X1600_Y200": "results/histograms/lumiScaled/X1600_Y200_normalized.root",
	"X1600_Y250": "results/histograms/lumiScaled/X1600_Y250_normalized.root",
    "X1600_Y300": "results/histograms/lumiScaled/X1600_Y300_normalized.root",
    "X1600_Y400": "results/histograms/lumiScaled/X1600_Y400_normalized.root",
    "X1800_Y90" : "results/histograms/lumiScaled/X1800_Y90_normalized.root",
    "X1800_Y100": "results/histograms/lumiScaled/X1800_Y100_normalized.root",
    "X1800_Y125": "results/histograms/lumiScaled/X1800_Y125_normalized.root",
    "X1800_Y150": "results/histograms/lumiScaled/X1800_Y150_normalized.root",
    "X1800_Y200": "results/histograms/lumiScaled/X1800_Y200_normalized.root",
    "X1800_Y250": "results/histograms/lumiScaled/X1800_Y250_normalized.root",
    "X1800_Y300": "results/histograms/lumiScaled/X1800_Y300_normalized.root",
    "X1800_Y400": "results/histograms/lumiScaled/X1800_Y400_normalized.root",
    "X2000_Y90" : "results/histograms/lumiScaled/X2000_Y90_normalized.root",
    "X2000_Y100": "results/histograms/lumiScaled/X2000_Y100_normalized.root",
    "X2000_Y125": "results/histograms/lumiScaled/X2000_Y125_normalized.root",
    "X2000_Y150": "results/histograms/lumiScaled/X2000_Y150_normalized.root",
    "X2000_Y200": "results/histograms/lumiScaled/X2000_Y200_normalized.root",
    "X2000_Y250": "results/histograms/lumiScaled/X2000_Y250_normalized.root",
    "X2000_Y300": "results/histograms/lumiScaled/X2000_Y300_normalized.root",
    "X2000_Y400": "results/histograms/lumiScaled/X2000_Y400_normalized.root"
}

bkgSamples = {
	"QCD"   : "results/histograms/lumiScaled/QCD_normalized.root",
	"ttbar" : "results/histograms/lumiScaled/ttbar_normalized.root"
}

def rebin2d(h2d):
	#x is mY from 60 to 360, 20GeV bin
	#y is mJJ from 1000 to 3000, 100GeV bin
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
h_pseudoData_LL = r.TH2F("mJJ_mJY_LL_data_obs",";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV",15,60,360,20,1000,3000)
h_pseudoData_TT = r.TH2F("mJJ_mJY_TT_data_obs",";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV",15,60,360,20,1000,3000)
h_pseudoData_AT = r.TH2F("mJJ_mJY_AT_data_obs",";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV",15,60,360,20,1000,3000)

for sample, fileName in sigSamples.items():
	print(sample)
	h2dName    = "mJJ_mJY_REGION_{0}".format(sample)
	h2dName    = h2dName.replace("_X","_MX")
	h2dName    = h2dName.replace("_Y","_MY")
	fTemp      = r.TFile.Open(fileName)
	TT_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_TT".format(sample,tagger))
	TT_h2d 	   = TT_h3dTemp.Project3D("zxe")
	TT_rebined = rebin2d(TT_h2d)
	#TT_h2d 	   = TT_h3dTemp.Project3D("xze") #if you want to flip axes
	TT_rebined.SetName(h2dName.replace("REGION","TT"))
	TT_rebined.SetTitle(";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV")
	TT_rebined.SetDirectory(0)
	histos.append(TT_rebined)

	LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
	LL_h2d 	   = LL_h3dTemp.Project3D("zxe")
	LL_rebined = rebin2d(LL_h2d)
	#LL_h2d 	   = LL_h3dTemp.Project3D("xze") #if you want to flip axes
	LL_rebined.SetName(h2dName.replace("REGION","LL"))
	LL_rebined.SetTitle(";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV")
	LL_rebined.SetDirectory(0)
	histos.append(LL_rebined)

	AT_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_AT".format(sample,tagger))
	AT_h2d 	   = AT_h3dTemp.Project3D("zxe")
	AT_rebined = rebin2d(AT_h2d)
	#AT_h2d 	   = AT_h3dTemp.Project3D("xze") #if you want to flip axes
	AT_rebined.SetName(h2dName.replace("REGION","AT"))
	AT_rebined.SetTitle(";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV")
	AT_rebined.SetDirectory(0)
	histos.append(AT_rebined)

for sample, fileName in bkgSamples.items():
	print(sample)
	h2dName    = "mJJ_mJY_REGION_{0}".format(sample)
	if(sample=="ttbar"):
		h2dName = h2dName.replace("ttbar","TTbar")
	fTemp      = r.TFile.Open(fileName)
	TT_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_TT".format(sample,tagger))
	TT_h2d 	   = TT_h3dTemp.Project3D("zxe")
	TT_rebined = rebin2d(TT_h2d)
	#TT_h2d 	   = TT_h3dTemp.Project3D("xze") #if you want to flip axes
	TT_rebined.SetName(h2dName.replace("REGION","TT"))
	TT_rebined.SetTitle(";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV")
	TT_rebined.SetDirectory(0)
	histos.append(TT_rebined)
	h_pseudoData_TT.Add(TT_rebined)

	LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
	LL_h2d 	   = LL_h3dTemp.Project3D("zxe")
	LL_rebined = rebin2d(LL_h2d)
	#LL_h2d 	   = LL_h3dTemp.Project3D("xze") #if you want to flip axes
	LL_rebined.SetName(h2dName.replace("REGION","LL"))
	LL_rebined.SetTitle(";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV")
	LL_rebined.SetDirectory(0)
	histos.append(LL_rebined)
	h_pseudoData_LL.Add(LL_rebined)

	AT_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_AT".format(sample,tagger))
	AT_h2d 	   = AT_h3dTemp.Project3D("zxe")
	AT_rebined = rebin2d(AT_h2d)
	#AT_h2d 	   = AT_h3dTemp.Project3D("xze") #if you want to flip axes
	AT_rebined.SetName(h2dName.replace("REGION","AT"))
	AT_rebined.SetTitle(";Y-jet mSD / 20 GeV; Dijet invariant mass / 100 GeV")
	AT_rebined.SetDirectory(0)
	histos.append(AT_rebined)
	h_pseudoData_AT.Add(AT_rebined)

histos.append(h_pseudoData_LL)
histos.append(h_pseudoData_TT)
histos.append(h_pseudoData_AT)


f = r.TFile.Open("results/histograms/templates/{0}_templates.root".format(tagger),"RECREATE")
f.cd()
for h in histos:
	h.Write()
f.Close()


	#LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
