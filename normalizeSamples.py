import ROOT as r
import json
import sys
import re



def normalizeProcess(process,xsec,luminosity,outFile):
    h_dict = {}
    file     = "/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/nonScaled/{0}.root".format(process)
    f        = r.TFile.Open(file)
    print(file)
    hCutFlow = f.Get("{0}_cutflow".format(process))
    nProc    = hCutFlow.GetBinContent(1)#number of processed events
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

def mergeHT(fJson,luminosity,process,outFile):
    #process - QCD, ZJets, WJets
    with open(fJson) as json_file:
        data = json.load(json_file)
        h_dict = {}
        for sample, sample_cfg in data.items():
            if not process in sample:
                continue
            xsec     = sample_cfg['xsec']
            file     = "/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/nonScaled/{0}.root".format(sample)
            f        = r.TFile.Open(file)
            print(file)
            hCutFlow = hCutFlow = f.Get("{0}_cutflow".format(sample))
            nProc    = hCutFlow.GetBinContent(1)#number of processed events
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
    luminosity = 35900
    with open(sys.argv[1]) as json_file:
        config = json.load(json_file)
        for sample, sample_cfg in config.items():
            if("QCD" in sample):
                continue
            if("WJets" in sample):
                continue
            if("ZJets" in sample):
                continue
    #         normalizeProcess(sample,sample_cfg['xsec'],luminosity,"results/histograms/lumiScaled/{0}_normalized.root".format(sample))
    # mergeHT(sys.argv[1],luminosity,"QCD","results/histograms/lumiScaled/QCD_normalized.root")
    # mergeHT(sys.argv[1],luminosity,"ZJets","results/histograms/lumiScaled/ZJets_normalized.root")
    # mergeHT(sys.argv[1],luminosity,"WJets","results/histograms/lumiScaled/WJets_normalized.root")

    #mergeData("/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/nonScaled/data_obs.root","/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/lumiScaled/data_obs.root")
    createPseudo(["results/histograms/lumiScaled/QCD_normalized.root","results/histograms/lumiScaled/ttbar_normalized.root"],"/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/lumiScaled/pseudodata.root")
    
#     ST_files = ["results/histograms/lumiScaled/ST_antitop_normalized.root",
# "results/histograms/lumiScaled/ST_top_normalized.root",
# "results/histograms/lumiScaled/ST_tW_antitop_normalized.root",
# "results/histograms/lumiScaled/ST_tW_top_normalized.root"]
#     VH_files = ["results/histograms/lumiScaled/WminusH_normalized.root",
# "results/histograms/lumiScaled/WplusH_normalized.root",
# "results/histograms/lumiScaled/ZH_normalized.root"]
#     VJets_files = ["results/histograms/lumiScaled/ZJets_normalized.root",
# "results/histograms/lumiScaled/WJets_normalized.root"]
#     mergeSamples(ST_files,"results/histograms/lumiScaled/ST_normalized.root",".+top_","ST_")    
#     mergeSamples(VH_files,"results/histograms/lumiScaled/VH_normalized.root","[a-zA-Z]+H","VH")
#     mergeSamples(VJets_files,"results/histograms/lumiScaled/VJets_normalized.root","[A-Z]Jets","VJets")