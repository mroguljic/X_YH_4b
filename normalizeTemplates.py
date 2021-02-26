import ROOT as r
import json
import sys
import re
import os


def normalizeProcess(process,year,inFile,outFile):
    h_dict = {}
    f = r.TFile.Open(inFile)
    print(process,inFile)
    json_file = open("skimInfo.json")
    config = json.load(json_file)
    if("MX" in process):
        xsec = 0.01
    else:
        xsec = config[year][process]["xsec"]
    luminosity = config[year]["lumi"]
    nProc = f.Get("{0}_cutflow_nom".format(process)).GetBinContent(1)
    print(nProc,xsec*luminosity)
    nLumi    = xsec*luminosity
    scaling  = nLumi/nProc
    print("Scale: {0:.4f}".format(scaling))
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        h.Scale(scaling)
        h.SetDirectory(0)
        h_dict[hName] = h
    f.Close()

    f = r.TFile(outFile,"recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()

def normalizeProcessGenW(process,year,inFile,outFile):
    #Assumes genW was applied when filling the source histogram
    h_dict = {}
    f = r.TFile.Open(inFile)
    print(process,inFile)
    json_file = open("skimInfo.json")
    config = json.load(json_file)
    if("MX" in process):
        xsec = 0.01
    else:
        xsec = config[year][process]["xsec"]
    luminosity = config[year]["lumi"]
    nProc = f.Get("{0}_cutflow_nom".format(process)).GetBinContent(1)
    avgW  = config[year][process]["avgW"]
    print(nProc,xsec*luminosity)
    nLumi    = xsec*luminosity
    scaling  = nLumi/(nProc*avgW)
    print("Scale: {0:.4f}".format(scaling))
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        h.Scale(scaling)
        h.SetDirectory(0)
        h_dict[hName] = h
    f.Close()

    f = r.TFile(outFile,"recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()


def mergeSamples(inFiles,outFile,regexMatch,regexReplace):
    h_dict = {}
    print("Merging to {0}".format(outFile))
    for inFile in inFiles:
        print(inFile)
        f        = r.TFile.Open(inFile) 
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            h.SetDirectory(0)
            hKey = re.sub(regexMatch,regexReplace,hName,count=1)
            if not hKey in h_dict:
                h.SetName(hKey)
                h_dict[hKey] = h
            else:
                h_dict[hKey].Add(h)
        f.Close()
    f = r.TFile(outFile,"recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()
    print("\n")


def scaleMuonTemplates():
    semilepProcesses16 = ["TTbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_sChannel","WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600","TTW","TTZ"]
    semilepProcesses17 = ["TTbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_s_top","ST_s_antitop","WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600","TTW","TTZ"]
    semilepProcesses18 = ["TTbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_s_top","ST_s_antitop","WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600","TTW","TTZ"]

    for year in ['2016','2017','2018']:
        print(year)
        muonDir = "results/templates_semiLeptonic/muon/"
        nonScaledDir = "{0}/{1}/nonScaled/".format(muonDir,year)
        lumiScaledDir = "{0}/{1}/scaled/".format(muonDir,year)
        if(year=='2016'):
            processes = semilepProcesses16
        elif(year=='2017'):
            processes = semilepProcesses17
        elif(year=='2018'):
            processes = semilepProcesses18     
        for proc in processes:
            normalizeProcessGenW(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
            #normalizeProcess(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
        year=year[-2:]#2018->18

        ttSamples = ["TTbarSemi.root"]
        ttSamples = [lumiScaledDir+f for f in ttSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(ttSamples,"{0}/TTbar{1}.root".format(lumiScaledDir,year[-2:]),"TTbarSemi|TTbar","TTbar")

        STsamples = ["ST_top.root","ST_antitop.root","ST_tW_antitop.root","ST_tW_top.root","ST_s_top","ST_antitop"]
        if(year=="16"):
            STsamples = ["ST_top.root","ST_antitop.root","ST_tW_antitop.root","ST_tW_top.root","ST_sChannel"]
        STsamples = [lumiScaledDir+f for f in STsamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(STsamples,"{0}/ST{1}.root".format(lumiScaledDir,year[-2:]),"ST.+top_|ST.+nel","ST_")

        WJetsSamples = ["WJetsLNu100.root","WJetsLNu250.root","WJetsLNu400.root","WJetsLNu600.root"]
        WJetsSamples = [lumiScaledDir+f for f in WJetsSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(WJetsSamples,"{0}/WJets{1}.root".format(lumiScaledDir,year[-2:]),"WJets.+\d+_","WJets_")

        TTVSamples = ["TTW.root","TTZ.root"]
        TTVSamples = [lumiScaledDir+f for f in TTVSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(TTVSamples,"{0}/TTV{1}.root".format(lumiScaledDir,year[-2:]),"TT._","TTV_")


        SingleMuonSamples = [nonScaledDir+f for f in os.listdir(nonScaledDir) if (os.path.isfile(os.path.join(nonScaledDir, f)) and "SingleMuon" in f)]#We are not lumi scaling data!
        mergeSamples(SingleMuonSamples,"{0}/SingleMuon{1}.root".format(lumiScaledDir,year[-2:]),"SingleMuon201[0-9][A-Z]_","data_obs_")
    
    # runIIDir="{0}/FullRunII/".format(muonDir)
    # os.system("hadd -f {0}/TTbarRunII.root {1}/2016/scaled/TTbar16.root {1}/2017/scaled/TTbar17.root {1}/2018/scaled/TTbar18.root".format(runIIDir,muonDir))
    # os.system("hadd -f {0}/STRunII.root {1}/2016/scaled/ST16.root {1}/2017/scaled/ST17.root {1}/2018/scaled/ST18.root".format(runIIDir,muonDir))
    # os.system("hadd -f {0}/WJetsRunII.root {1}/2016/scaled/WJets16.root {1}/2017/scaled/WJets17.root {1}/2018/scaled/WJets18.root".format(runIIDir,muonDir))
    # os.system("hadd -f {0}/SingleMuonRunII.root {1}/2016/scaled/SingleMuon16.root {1}/2017/scaled/SingleMuon17.root {1}/2018/scaled/SingleMuon18.root".format(runIIDir,muonDir))


def scaleEvtSelTemplates():
    MX = [800,900,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000]
    MY = [40,60,90,100,125,200,300,400]#,600,800,1000,1200,1400,1600,1800]
    signalPoints  = []
    for X in MX:
        for Y in MY:
            if((X>(Y+125.0))):
                signalPoints.append("MX{0}_MY{1}".format(X,Y))

    srProcesses16 = ["QCD700","QCD1000","QCD1500","QCD2000","TTbar","TTbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]
    srProcesses17 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","TTbar","TTbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]
    srProcesses18 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","TTbar","TTbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]

    srProcesses16=srProcesses16+signalPoints
    srProcesses17=srProcesses17+signalPoints
    srProcesses18=srProcesses18+signalPoints

    for year in ['2016','2017','2018']:
        print(year)
        nonScaledDir = "results/templates/WP_0.8_0.95/{0}/nonScaled/".format(year)
        lumiScaledDir = "results/templates/WP_0.8_0.95/{0}/scaled/".format(year)
        if(year=='2016'):
            processes = srProcesses16
        elif(year=='2017'):
            processes = srProcesses17
        elif(year=='2018'):
            processes = srProcesses18 
        for proc in processes:
            nonScaledFile = "{0}/{1}.root".format(nonScaledDir,proc)
            if(os.path.isfile(nonScaledFile)):
                try:
                    if("TTbar" in proc):
                        normalizeProcessGenW(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
                    else:                        
                        normalizeProcess(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
                except:
                    print("Couldn't normalize {0}".format(proc))
            else:
                print("{0} does not exist, skipping!".format(nonScaledFile))
        
        QCDsamples = ["QCD700.root","QCD1000.root","QCD1500.root","QCD2000.root"]
        QCDsamples = [lumiScaledDir+f for f in QCDsamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(QCDsamples,"{0}/QCD{1}.root".format(lumiScaledDir,year[-2:]),"QCD\d+_","QCD_")

        ttSamples = ["TTbar.root","TTbarHT.root"]
        ttSamples = [lumiScaledDir+f for f in ttSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(ttSamples,"{0}/TTbar{1}.root".format(lumiScaledDir,year[-2:]),"TTbarHT|TTbar","TTbar")

        STsamples = ["ST_top.root","ST_antitop.root","ST_tW_antitop.root","ST_tW_top.root"]
        STsamples = [lumiScaledDir+f for f in STsamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(STsamples,"{0}/ST{1}.root".format(lumiScaledDir,year[-2:]),".+top_","ST_")

        VJetsSamples = ["WJets400.root","WJets600.root","WJets800.root","ZJets400.root","ZJets600.root","ZJets800.root"]
        VJetsSamples = [lumiScaledDir+f for f in VJetsSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(VJetsSamples,"{0}/VJets{1}.root".format(lumiScaledDir,year[-2:]),"[A-Z]Jets\d+_","VJets_")

        VHSamples = ["WminusH.root","WplusH.root","ZH.root"]
        VHSamples = [lumiScaledDir+f for f in VHSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(VHSamples,"{0}/VH{1}.root".format(lumiScaledDir,year[-2:]),"[a-zA-Z]+H_","VH_")

        JetHTSamples = [nonScaledDir+f for f in os.listdir(nonScaledDir) if (os.path.isfile(os.path.join(nonScaledDir, f)) and "JetHT" in f)]#We are not lumi scaling data!
        mergeSamples(JetHTSamples,"{0}/JetHT{1}.root".format(lumiScaledDir,year[-2:]),"JetHT201[0-9][A-Z]_","data_obs_")

        pseudoSamples = ["{0}/QCD{1}.root".format(lumiScaledDir,year[-2:]),"{0}/TTbar{1}.root".format(lumiScaledDir,year[-2:])]
        mergeSamples(pseudoSamples,"{0}/pseudo{1}.root".format(lumiScaledDir,year[-2:]),"QCD|TTbar","data_obs")

    templatesDir = "results/templates/WP_0.8_0.95/"
    runIIDir="{0}/FullRunII/".format(templatesDir)
    os.system("hadd -f {0}/ttbarRunII.root {1}/2016/scaled/TTbar16.root {1}/2017/scaled/TTbar17.root {1}/2018/scaled/TTbar18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/QCDRunII.root {1}/2016/scaled/QCD16.root {1}/2017/scaled/QCD17.root {1}/2018/scaled/QCD18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/VJetsRunII.root {1}/2016/scaled/VJets16.root {1}/2017/scaled/VJets17.root {1}/2018/scaled/VJets18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/STRunII.root {1}/2016/scaled/ST16.root {1}/2017/scaled/ST17.root {1}/2018/scaled/ST18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/JetHTRunII.root {1}/2016/scaled/JetHT16.root {1}/2017/scaled/JetHT17.root {1}/2018/scaled/JetHT18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/pseudoRunII.root {1}/2016/scaled/pseudo16.root {1}/2017/scaled/pseudo17.root {1}/2018/scaled/pseudo18.root".format(runIIDir,templatesDir))



if __name__ == '__main__':

    scaleMuonTemplates()
    #scaleEvtSelTemplates()
