import ROOT as r
import json
import sys
import re
import os


def normalizeProcess(process,year,inFile,outFile):
    h_dict = {}
    f = r.TFile.Open(inFile)
    print(inFile)
    json_file = open("skimInfo.json")
    config = json.load(json_file)
    xsec = config[year][process]["xsec"]
    nProc = config[year][process]["nProc"]
    luminosity = config[year]["lumi"]
    print(nProc,xsec*luminosity)
    nLumi    = xsec*luminosity
    scaling  = nLumi/nProc
    print("Scale: {0:.4f}".format(scaling))
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        h.Scale(scaling)
        h.SetDirectory(0)
        if("cutflow" in hName):
            h.SetBinContent(1,nProc)
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
    srProcesses16 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH","X1600_Y125"]
    srProcesses17 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]
    srProcesses18 = ["QCD500","QCD700","QCD1000","QCD1500","QCD2000","ttbar","ttbarHT","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top"
    ,"WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ttH","ZH","WminusH","WplusH"]

    for year in ['2016','2017','2018']:
        print(year)
        nonScaledDir = "results/templates/{0}/nonScaled/".format(year)
        lumiScaledDir = "results/templates/{0}/lumiScaled/".format(year)
        if(year=='2016'):
            processes = srProcesses16
        elif(year=='2017'):
            processes = srProcesses17
        elif(year=='2018'):
            processes = srProcesses18     
        for proc in processes:
            normalizeProcess(proc,year,"{0}/{1}.root".format(nonScaledDir,proc),"{0}/{1}.root".format(lumiScaledDir,proc))
        os.system("hadd -f {0}/ttbar{1}.root {0}/ttbar.root {0}/ttbarHT.root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/QCD{1}.root {0}/QCD*.root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/ST{1}.root {0}/ST_*root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/VJets{1}.root {0}/WJets*root {0}/ZJets*root".format(lumiScaledDir,year))
        os.system("hadd -f {0}/JetHT{1}.root {2}/JetHT*root".format(lumiScaledDir,year,nonScaledDir))

    templatesDir = "results/templates/"
    runIIDir="{0}/FullRunII/".format(templatesDir)
    os.system("hadd -f {0}/ttbarRunII.root {1}/2016/lumiScaled/ttbar16.root {1}/2017/lumiScaled/ttbar17.root {1}/2018/lumiScaled/ttbar18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/QCDRunII.root {1}/2016/lumiScaled/QCD16.root {1}/2017/lumiScaled/QCD17.root {1}/2018/lumiScaled/QCD18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/VJetsRunII.root {1}/2016/lumiScaled/VJets16.root {1}/2017/lumiScaled/VJets17.root {1}/2018/lumiScaled/VJets18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/STRunII.root {1}/2016/lumiScaled/ST16.root {1}/2017/lumiScaled/ST17.root {1}/2018/lumiScaled/ST18.root".format(runIIDir,templatesDir))
    os.system("hadd -f {0}/JetHTII.root {1}/2016/scaled/JetHT16.root {1}/2017/scaled/JetHT17.root {1}/2018/scaled/JetHT18.root".format(runIIDir,muonDir))

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
    #normalizeProcess(process,year,inFile,outFile):
    # normalizeProcess("ttbar","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbar_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbar_scaled.root")
    # normalizeProcess("ttbarHT","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbarHT_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbarHT_scaled.root")
    # normalizeProcess("QCD500","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD500_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD500_scaled.root")
    # normalizeProcess("QCD700","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD700_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD700_scaled.root")
    # normalizeProcess("QCD1000","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1000_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1000_scaled.root")
    # normalizeProcess("QCD1500","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1500_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1500_scaled.root")
    # normalizeProcess("QCD2000","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD2000_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD2000_scaled.root")
    # normalizeProcess("ST_antitop","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_antitop_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_antitop_scaled.root")
    # normalizeProcess("ST_top","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_top_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_top_scaled.root")
    # normalizeProcess("ST_tW_antitop","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_tW_antitop_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_tW_antitop_scaled.root")
    # normalizeProcess("ST_tW_top","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_tW_top_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ST_tW_top_scaled.root")

    # normalizeProcess("ttbar","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ttbar_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ttbar_scaled.root")
    # normalizeProcess("ttbarHT","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ttbarHT_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ttbarHT_scaled.root")
    # normalizeProcess("QCD500","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD500_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD500_scaled.root")
    # normalizeProcess("QCD700","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD700_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD700_scaled.root")
    # normalizeProcess("QCD1000","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD1000_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD1000_scaled.root")
    # normalizeProcess("QCD1500","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD1500_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD1500_scaled.root")
    # normalizeProcess("QCD2000","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD2000_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/QCD2000_scaled.root")
    # normalizeProcess("ST_antitop","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_antitop_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_antitop_scaled.root")
    # normalizeProcess("ST_top","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_top_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_top_scaled.root")
    # normalizeProcess("ST_tW_antitop","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_tW_antitop_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_tW_antitop_scaled.root")
    # normalizeProcess("ST_tW_top","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_tW_top_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2017/ST_tW_top_scaled.root")

    # normalizeProcess("ttbar","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ttbar_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ttbar_scaled.root")
    # normalizeProcess("ttbarHT","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ttbarHT_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ttbarHT_scaled.root")
    # normalizeProcess("QCD500","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD500_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD500_scaled.root")
    # normalizeProcess("QCD700","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD700_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD700_scaled.root")
    # normalizeProcess("QCD1000","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD1000_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD1000_scaled.root")
    # normalizeProcess("QCD1500","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD1500_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD1500_scaled.root")
    # normalizeProcess("QCD2000","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD2000_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/QCD2000_scaled.root")
    # normalizeProcess("ST_antitop","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_antitop_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_antitop_scaled.root")
    # normalizeProcess("ST_top","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_top_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_top_scaled.root")
    # normalizeProcess("ST_tW_antitop","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_tW_antitop_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_tW_antitop_scaled.root")
    # normalizeProcess("ST_tW_top","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_tW_top_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2018/ST_tW_top_scaled.root")

    # normalizeProcess("X1600_Y125","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/X1600_Y125_tpl.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/X1600_Y125_tpl_scaled.root")
    # normalizeProcess("QCD500","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD500.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD500_scaled.root")
    # normalizeProcess("QCD700","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD700.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD700_scaled.root")
    # normalizeProcess("QCD1000","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1000.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1000_scaled.root")
    # normalizeProcess("QCD1500","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1500.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD1500_scaled.root")
    # normalizeProcess("QCD2000","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD2000.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/QCD2000_scaled.root")
    # normalizeProcess("ttbarHT","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbarHT.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbarHT_scaled.root")
    # normalizeProcess("ttbar","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbar.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates/2016/ttbar_scaled.root")

    # normalizeProcess("ttbar","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ttbar_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ttbar_scaled.root")
    # normalizeProcess("ttbarSemi","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ttbarSemi_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ttbarSemi_scaled.root")
    # normalizeProcess("WJetsLNu100","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/WJetsLNu100_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/WJetsLNu100_scaled.root")
    # normalizeProcess("WJetsLNu250","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/WJetsLNu250_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/WJetsLNu250_scaled.root")
    # normalizeProcess("WJetsLNu400","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/WJetsLNu400_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/WJetsLNu400_scaled.root")
    # normalizeProcess("WJetsLNu600","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/WJetsLNu600_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/WJetsLNu600_scaled.root")
    # normalizeProcess("ST_antitop","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ST_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ST_antitop_scaled.root")
    # normalizeProcess("ST_top","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ST_top_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ST_top_scaled.root")
    # normalizeProcess("ST_tW_top","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ST_tW_top_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ST_tW_top_scaled.root")
    # normalizeProcess("ST_tW_antitop","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ST_tW_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ST_tW_antitop_scaled.root")
    # normalizeProcess("ST_sChannel","2016","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/nonScaled/ST_sChannel_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2016/scaled/ST_sChannel_scaled.root")

    # normalizeProcess("ttbar","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ttbar_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ttbar_scaled.root")
    # normalizeProcess("ttbarSemi","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ttbarSemi_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ttbarSemi_scaled.root")
    # normalizeProcess("WJetsLNu100","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/WJetsLNu100_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/WJetsLNu100_scaled.root")
    # normalizeProcess("WJetsLNu250","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/WJetsLNu250_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/WJetsLNu250_scaled.root")
    # normalizeProcess("WJetsLNu400","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/WJetsLNu400_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/WJetsLNu400_scaled.root")
    # normalizeProcess("WJetsLNu600","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/WJetsLNu600_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/WJetsLNu600_scaled.root")
    # normalizeProcess("ST_antitop","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ST_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ST_antitop_scaled.root")
    # normalizeProcess("ST_top","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ST_top_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ST_top_scaled.root")
    # normalizeProcess("ST_tW_top","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ST_tW_top_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ST_tW_top_scaled.root")
    # normalizeProcess("ST_tW_antitop","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ST_tW_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ST_tW_antitop_scaled.root")
    # normalizeProcess("ST_s_top","2017","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/nonScaled/ST_s_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2017/scaled/ST_s_top_scaled.root")

    # normalizeProcess("ttbarSemi","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ttbarSemi_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ttbarSemi_scaled.root")
    # normalizeProcess("WJetsLNu100","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/WJetsLNu100_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/WJetsLNu100_scaled.root")
    # normalizeProcess("WJetsLNu250","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/WJetsLNu250_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/WJetsLNu250_scaled.root")
    # normalizeProcess("WJetsLNu400","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/WJetsLNu400_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/WJetsLNu400_scaled.root")
    # normalizeProcess("WJetsLNu600","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/WJetsLNu600_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/WJetsLNu600_scaled.root")
    # normalizeProcess("ST_antitop","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ST_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ST_antitop_scaled.root")
    # normalizeProcess("ST_top","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ST_top_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ST_top_scaled.root")
    # normalizeProcess("ST_tW_top","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ST_tW_top_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ST_tW_top_scaled.root")
    # normalizeProcess("ST_tW_antitop","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ST_tW_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ST_tW_antitop_scaled.root")
    # normalizeProcess("ST_s_antitop","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ST_s_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ST_s_antitop_scaled.root")
    # normalizeProcess("ST_s_top","2018","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/nonScaled/ST_s_antitop_nonScaled.root","/afs/cern.ch/work/m/mrogulji/X_YH_4b/results/templates_semiLeptonic/2018/scaled/ST_s_top_scaled.root")



    # semilepProcesses = ["QCD1000","QCD1500","QCD2000","ttbar","ttbarSemi","ST_top","ST_antitop","ST_tW_antitop","ST_tW_top","ST_sChannel",
    # "WJetsLNu100","WJetsLNu250","WJetsLNu400","WJetsLNu600"]
    # for proc in semilepProcesses:
    #     print(proc)
    #     normalizeProcess(proc,"2016","results/templates_semiLeptonic/electron/2016/nonScaled/{0}.root".format(proc),"results/templates_semiLeptonic/electron/2016/scaled/{0}.root".format(proc))

    #scaleEvtSelHistos()
    scaleMuonTemplates()