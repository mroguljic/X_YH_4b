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
    xsec = config[year][process]["xsec"]
    luminosity = config[year]["lumi"]
    nProc = f.Get("{0}_cutflow".format(process)).GetBinContent(1)
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
    semilepProcesses16 = ["ttbar","ttbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_sChannel","WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600"]
    semilepProcesses17 = ["ttbar","ttbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_s_top","WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600"]
    semilepProcesses18 = ["ttbar","ttbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_s_top","ST_s_antitop","WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600"]

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
            normalizeProcess(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
        year=year[-2:]#2018->18
        os.system("hadd -f {0}/ttbar{1}.root {0}/ttbar.root {0}/ttbarSemi.root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/ST{1}.root {0}/ST_*root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/WJets{1}.root {0}/WJetsL*root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/SingleMuon{1}.root {2}/SingleMuon*root".format(lumiScaledDir,year,nonScaledDir))
    
    runIIDir="{0}/FullRunII/".format(muonDir)
    os.system("hadd -f {0}/ttbarRunII.root {1}/2016/scaled/ttbar16.root {1}/2017/scaled/ttbar17.root {1}/2018/scaled/ttbar18.root".format(runIIDir,muonDir))
    os.system("hadd -f {0}/STRunII.root {1}/2016/scaled/ST16.root {1}/2017/scaled/ST17.root {1}/2018/scaled/ST18.root".format(runIIDir,muonDir))
    os.system("hadd -f {0}/WJetsRunII.root {1}/2016/scaled/WJets16.root {1}/2017/scaled/WJets17.root {1}/2018/scaled/WJets18.root".format(runIIDir,muonDir))
    os.system("hadd -f {0}/SingleMuonRunII.root {1}/2016/scaled/SingleMuon16.root {1}/2017/scaled/SingleMuon17.root {1}/2018/scaled/SingleMuon18.root".format(runIIDir,muonDir))


def scaleEvtSelTemplates():
    MX = [800,900,1000,1200,1400,1600,1800,2000]
    MY = [60,90,100,125,200,300,400,600,800,1000,1200,1400,1600,1800]
    signalPoints  = []
    for X in MX:
        for Y in MY:
            if((X>(Y+125.0))):
                signalPoints.append("X{0}_Y{1}".format(X,Y))
    srProcesses16 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]
    srProcesses17 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]
    srProcesses18 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]

    srProcesses16=srProcesses16+signalPoints
    srProcesses17=srProcesses17+signalPoints
    srProcesses17=srProcesses17+signalPoints

    for year in ['2016']:#,'2017','2018']:
        print(year)
        nonScaledDir = "results/templates/{0}/nonScaled/".format(year)
        lumiScaledDir = "results/templates/{0}/scaled/".format(year)
        if(year=='2016'):
            processes = srProcesses16
        elif(year=='2017'):
            processes = srProcesses17
        elif(year=='2018'):
            processes = srProcesses18     
        for proc in processes:
            nonScaledFile = "{0}/{1}.root".format(nonScaledDir,proc)
            if(os.path.isfile(nonScaledFile)):
                normalizeProcess(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
            else:
                print("{0} does not exist, skipping!".format(nonScaledFile))
        
        QCDsamples = ["QCD500.root","QCD700.root","QCD1000.root","QCD1500.root","QCD2000.root"]
        QCDsamples = [lumiScaledDir+f for f in QCDsamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(QCDsamples,"{0}/QCD{1}.root".format(lumiScaledDir,year[-2:]),"QCD\d+_","QCD_")

        ttSamples = ["ttbar.root","ttbarHT.root"]
        ttSamples = [lumiScaledDir+f for f in ttSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(ttSamples,"{0}/ttbar{1}.root".format(lumiScaledDir,year[-2:]),"ttbar[a-zA-Z]+_","ttbar_")

        STsamples = ["ST_top.root","ST_antitop.root","ST_tW_antitop.root","ST_tW_top.root"]
        STsamples = [lumiScaledDir+f for f in STsamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(STsamples,"{0}/ST{1}.root".format(lumiScaledDir,year[-2:]),".+top_","ST_")

        VJetsSamples = ["WJets400.root","WJets600.root","WJets800.root","ZJets400.root","ZJets600.root","ZJets800.root"]
        VJetsSamples = [lumiScaledDir+f for f in VJetsSamples if (os.path.isfile(os.path.join(lumiScaledDir, f)))]
        mergeSamples(VJetsSamples,"{0}/VJets{1}.root".format(lumiScaledDir,year[-2:]),"[A-Z]Jets\d+_","VJets_")

        JetHTSamples = [nonScaledDir+f for f in os.listdir(nonScaledDir) if (os.path.isfile(os.path.join(nonScaledDir, f)) and "JetHT" in f)]#We are not lumi scaling data!
        mergeSamples(JetHTSamples,"{0}/JetHT{1}.root".format(lumiScaledDir,year[-2:]),"JetHT201[0-9][A-Z]_","JetHT_")
    templatesDir = "results/templates/"
    runIIDir="{0}/FullRunII/".format(templatesDir)
    os.system("hadd -f {0}/ttbarRunII.root {1}/2016/scaled/ttbar16.root {1}/2017/scaled/ttbar17.root {1}/2018/scaled/ttbar18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/QCDRunII.root {1}/2016/scaled/QCD16.root {1}/2017/scaled/QCD17.root {1}/2018/scaled/QCD18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/VJetsRunII.root {1}/2016/scaled/VJets16.root {1}/2017/scaled/VJets17.root {1}/2018/scaled/VJets18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/STRunII.root {1}/2016/scaled/ST16.root {1}/2017/scaled/ST17.root {1}/2018/scaled/ST18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/JetHTRunII.root {1}/2016/scaled/JetHT16.root {1}/2017/scaled/JetHT17.root {1}/2018/scaled/JetHT18.root".format(runIIDir,templatesDir))

def scaleEvtSelHistos():
    #Scales and merges histograms coming from event selection
    srProcesses16 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH","X1600_Y125"]
    srProcesses17 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]
    srProcesses18 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]

    for year in ['2016','2017','2018']:
        print(year)
        nonScaledDir = "results/histograms/{0}/nonScaled/".format(year)
        lumiScaledDir = "results/histograms/{0}/lumiScaled/".format(year)
        if(year=='2016'):
            processes = srProcesses16
        elif(year=='2017'):
            processes = srProcesses17
        elif(year=='2018'):
            processes = srProcesses18     
        for proc in processes:
            normalizeProcess(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))

        QCDsamples = ["QCD500.root","QCD700.root","QCD1000.root","QCD1500.root","QCD2000.root"]
        QCDsamples = [lumiScaledDir+s for s in QCDsamples]
        mergeSamples(QCDsamples,"{0}/QCD{1}.root".format(lumiScaledDir,year[-2:]),"QCD\d+_","QCD_")

        ttSamples = ["ttbar.root","ttbarHT.root"]
        ttSamples = [lumiScaledDir+s for s in ttSamples]
        mergeSamples(ttSamples,"{0}/ttbar{1}.root".format(lumiScaledDir,year[-2:]),"ttbar[a-zA-Z]+_","ttbar_")

        STsamples = ["ST_top.root","ST_antitop.root","ST_tW_antitop.root","ST_tW_top.root"]
        STsamples = [lumiScaledDir+s for s in STsamples]
        mergeSamples(STsamples,"{0}/ST{1}.root".format(lumiScaledDir,year[-2:]),".+top_","ST_")

        VJetsSamples = ["WJets400.root","WJets600.root","WJets800.root","ZJets400.root","ZJets600.root","ZJets800.root"]
        VJetsSamples = [lumiScaledDir+s for s in VJetsSamples]
        mergeSamples(VJetsSamples,"{0}/VJets{1}.root".format(lumiScaledDir,year[-2:]),"[A-Z]Jets","VJets")

        os.system("hadd -f {0}/JetHT{1}.root {2}/JetHT*root".format(lumiScaledDir,year,nonScaledDir))

if __name__ == '__main__':

    # semilepProcesses = ["QCD1000","QCD1500","QCD2000","ttbar","ttbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_sChannel",
    # "WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600"]
    # for proc in semilepProcesses:
    #     print(proc)
    #     normalizeProcess(proc,"2016","results/templates_semiLeptonic/electron/2016/nonScaled/{0}.root".format(proc),"results/templates_semiLeptonic/electron/2016/scaled/{0}.root".format(proc))

    #scaleEvtSelHistos()
    #scaleMuonTemplates()
    scaleEvtSelTemplates()