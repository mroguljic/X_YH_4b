import ROOT as r
import json
import sys
import re
import os

def getNProcessed(skimDirectory):
    skimFiles = [os.path.join(skimDirectory, f) for f in os.listdir(skimDirectory) if os.path.isfile(os.path.join(skimDirectory, f))]
    NProcessed = 0
    for file in skimFiles:
        f = r.TFile.Open(file)
        print(file)
        NProcessed += f.Get("skimInfo").GetBinContent(1)
        f.Close()
    return NProcessed



def normalizeProcess(process,xsec,luminosity,year,outFile):
    h_dict = {}
    file     = "/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/{0}/nonScaled/{1}.root".format(year,process)
    f        = r.TFile.Open(file)
    print(file)
    hCutFlow = f.Get("{0}_cutflow".format(process))
    nProc = getNProcessed("/eos/cms/store/group/phys_b2g/mrogulji/skims/{0}/{1}/".format(year,process))
    hCutFlow.SetBinContent(1,nProc)
    #nProc    = hCutFlow.GetBinContent(2)#number of processed events if not running on skims
    print(nProc,xsec*luminosity)
    nLumi    = xsec*luminosity
    scaling  = nLumi/nProc
    print("Scale: {0:.4f}".format(scaling))
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        # if not ("hCutFlow" in hName): #uncomment if you want "original" cutflow
        #     h.Scale(scaling)
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

def mergeHT(fJson,luminosity,process,year,outFile):
    #process - QCD, ZJets, WJets
    with open(fJson) as json_file:
        data = json.load(json_file)
        h_dict = {}
        for sample, sample_cfg in data.items():
            if not process in sample:
                continue
            xsec     = sample_cfg['xsec']
            file     = "/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/{0}/nonScaled/{1}.root".format(year,sample)
            #file     = "/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/triggers/{0}/{1}.root".format(year,sample)
            f        = r.TFile.Open(file)
            hCutFlow = f.Get("{0}_cutflow".format(sample))
            nProc = getNProcessed("/eos/cms/store/group/phys_b2g/mrogulji/skims/{0}/{1}/".format(year,sample))
            print(sample,nProc)
            hCutFlow.SetBinContent(1,nProc)
            #nProc    = hCutFlow.GetBinContent(2)#number of processed events if not running on skims
            nLumi    = xsec*luminosity
            scaling  = nLumi/nProc
            print("Scale: {0:.2f}".format(scaling))
            for key in f.GetListOfKeys():
                h = key.ReadObj()
                hName = h.GetName()
                # if not ("hCutFlow" in hName): #uncomment if you want "original" cutflow
                #     h.Scale(scaling)
                h.Scale(scaling)
                h.SetDirectory(0)
                hKey = re.sub("{0}\d+_".format(process),"{0}_".format(process),hName)
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

def mergeData(inFile,outFile):
    f        = r.TFile.Open(inFile) 
    h_dict = {}   
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        h.SetDirectory(0)
        hKey = re.sub("Data.","data_obs",hName)
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

def mergeSamples(inFiles,outFile,regexMatch,regexReplace):
    for inFile in inFiles:
        print(inFile)
        f        = r.TFile.Open(inFile) 
        h_dict = {}   
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

def createPseudo(inFiles,outFile):
    h_dict = {}   
    for inFile in inFiles:
        f      = r.TFile.Open(inFile) 
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            h.SetDirectory(0)
            hKey = re.sub("[a-zA-Z]+","pseudodata",hName,count=1)
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



if __name__ == '__main__':
    #args: json lumi year
    luminosity = float(sys.argv[2])#35900,41500,59800 (46100 if 2018B-D)
    year     = sys.argv[3]
    with open(sys.argv[1]) as json_file:
        config = json.load(json_file)
        for sample, sample_cfg in config.items():
            if("QCD" in sample):
                continue
            if("WJets" in sample):
                continue
            if("ZJets" in sample):
                continue
            normalizeProcess(sample,sample_cfg['xsec'],luminosity,year,"results/histograms/{0}/lumiScaled/{1}_normalized.root".format(year,sample))
    #mergeHT(sys.argv[1],luminosity,"QCD",year,"results/histograms/triggers/{0}/QCD.root".format(year))
    #mergeData("/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/triggers/{0}/18.11./data_obs_all.root".format(year,sample),"/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/triggers/{0}/18.11./data_obs.root".format(year,sample))  

    mergeHT(sys.argv[1],luminosity,"QCD",year,"results/histograms/{0}/lumiScaled/QCD_normalized.root".format(year))
    # mergeHT(sys.argv[1],luminosity,"ZJets",year,"results/histograms/{0}/lumiScaled/ZJets_normalized.root".format(year))
    # mergeHT(sys.argv[1],luminosity,"WJets",year,"results/histograms/{0}/lumiScaled/WJets_normalized.root".format(year))
    
    # mergeData("/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/{0}/nonScaled/data_obs.root".format(year,sample),"/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/{0}/lumiScaled/data_obs.root".format(year,sample))
    # createPseudo(["results/histograms/{0}/lumiScaled/QCD_normalized.root".format(year),"results/histograms/{0}/lumiScaled/ttbar_normalized.root".format(year)],"/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/{0}/lumiScaled/pseudodata.root".format(year))
    # ST_samples = ["ST_antitop_normalized","ST_top_normalized.root","ST_tW_antitop_normalized.root","ST_tW_top_normalized.root"]
    # ST_files = []
    # for sample in ST_samples:
    #     ST_files.append("results/histograms/{0}/lumiScaled/{1}".format(year,sample))
    
    # VH_samples = ["WminusH_normalized.root","WplusH_normalized.root","ZH_normalized.root"]
    # VH_files = []
    # for sample in VH_samples:
    #     VH_files.append("results/histograms/{0}/lumiScaled/{1}".format(year,sample))
    # VJets_samples = ["ZJets_normalized.root","WJets_normalized.root"]
    # VJets_files = []
    # for sample in VJets_samples:
    #     VJets_files.append("results/histograms/{0}/lumiScaled/{1}".format(year,sample))

    # print(VJets_files)
    # mergeSamples(ST_files,"results/histograms/{0}/lumiScaled/ST_normalized.root".format(year),".+top_","ST_")    
    # mergeSamples(VH_files,"results/histograms/{0}/lumiScaled/VH_normalized.root".format(year),"[a-zA-Z]+H","VH")
    # mergeSamples(VJets_files,"results/histograms/{0}/lumiScaled/VJets_normalized.root".format(year),"[A-Z]Jets","VJets")