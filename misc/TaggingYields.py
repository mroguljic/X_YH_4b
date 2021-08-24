import ROOT as r

years       = ["16","17","18"]
regions     = ["NAL_T","NAL_L","NAL_AL","TT","LL","L_AL","T_AL"]
processes   = ["data_obs","TTbar","QCD","MX1600_MY125"]
files       = ["JetHT.root","TTbar.root","QCD.root","MX1600_MY125.root"]

for year in years:
    tplDir = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/20{0}/scaled/".format(year)
    print("\nTable for year 20{0}".format(year))
    headline = " & ".join(regions)
    print(headline)
    for i,proc in enumerate(processes):
        if not "MX" in files[i]:
            tempFile = r.TFile.Open(tplDir+files[i].replace(".root","{0}.root".format(year)))
        else:
            tempFile = r.TFile.Open(tplDir+files[i])
        line     = "{0}".format(proc)
        for region in regions:
            h2   = tempFile.Get("{0}_mJY_mJJ_{1}_nom".format(proc,region))
            xLow = h2.GetXaxis().FindBin(60)
            xUp  = h2.GetXaxis().FindBin(640)
            yLow = h2.GetYaxis().FindBin(800)
            yUp  = h2.GetYaxis().FindBin(4000)
            #nEvt = h2.Integral(xLow,xUp,yLow,yUp)
            nEvt = h2.Integral()
            if("MX" in files[i]):
                nEvt=nEvt/10.
            #print(xLow,xUp,yLow,yUp)
            line+= " & {0:.2f}".format(nEvt)
        line+="\\\\"
        print(line)