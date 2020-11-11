import ROOT as r
import os

Y_masses = ["60","80","90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
X_masses = ["800","900","1000","1200","1400","1600","1800","2000"]


years = ["2016","2017","2018"]
for year in years:
    sigSamples = {}   
    inputDir = "/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/histograms/{0}/lumiScaled/".format(year)

    for X in X_masses:
        for Y in Y_masses:
            sigFile = "{0}/X{1}_Y{2}_normalized.root".format(inputDir,X,Y)
            sigSample = "X{0}_Y{1}".format(X,Y)
            print(sigFile)
            if os.path.isfile(sigFile):
                sigSamples[sigSample] = sigFile

    bkgSamples = {
        "QCD"   : "results/histograms/{0}/lumiScaled/QCD_normalized.root".format(year),
        "ttbar" : "results/histograms/{0}/lumiScaled/ttbar_normalized.root".format(year)
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


    f = r.TFile.Open("results/histograms/templates/{0}_templates_{1}.root".format(tagger,year),"RECREATE")
    f.cd()
    for h in histos:
    	h.Write()
    f.Close()
    print(sigSamples)

	#LL_h3dTemp = fTemp.Get("{0}_mjY_mjH_mjjHY_{1}_LL".format(sample,tagger))
