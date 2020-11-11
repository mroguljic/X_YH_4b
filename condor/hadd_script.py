import os

bkg_samples="QCD200 QCD300 QCD500 QCD700 QCD1000 QCD1500 QCD2000 ttbar ZJets400 ZJets600 ZJets800 WJets400 WJets600 WJets800 ST_antitop ST_top ST_tW_top ST_tW_antitop WminusH WplusH ZH ttH"
Y_masses = ["60","80","90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
X_masses = ["800","900","1000","1200","1400","1600","1800","2000"]


years = ["2016","2017","2018"]
for year in years:
    inputDir = "/eos/cms/store/group/phys_b2g/mrogulji/{0}/06.11./".format(year)
    outputDir = "/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/histograms/{0}/nonScaled/".format(year)

    for X in X_masses:
        for Y in Y_masses:
            inputFull = "{0}/X{1}/X{1}_Y{2}/output/".format(inputDir,X,Y)
            outFile = "X{0}_Y{1}.root".format(X,Y)
            haddCmd = "hadd {0}/{1} {2}/*root".format(outputDir,outFile,inputFull)
            if os.path.isdir(inputFull):
                #print(inputFull)
                print(haddCmd)
                os.system(haddCmd)

    for sample in bkg_samples.split(" "):
        inputFull = "{0}/{1}/output/".format(inputDir,sample)
        outFile = "{0}.root".format(sample)
        haddCmd = "hadd {0}/{1} {2}/*root".format(outputDir,outFile,inputFull)
        if os.path.isdir(inputFull):
            #print(inputFull)
            print(haddCmd)
            os.system(haddCmd)   