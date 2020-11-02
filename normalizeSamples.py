import ROOT as r
import json
import sys
import re



def normalizeProcess(process,xsec,luminosity,outFile):
    h_dict = {}
    file     = "/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/nonScaled/{0}.root".format(process)
    f        = r.TFile.Open(file)
    print(file)
    hCutFlow = f.Get("hCutFlow")
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
            hCutFlow = f.Get("hCutFlow")
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
                if ("hCutFlow" in hName):
                    hKey = hName
                else:
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

def mergeData(inFiles,samples,outFile):
    for inFile in inFiles:
        f        = r.TFile.Open(inFile) 
        h_dict = {}   
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            h.SetDirectory(0)
            if ("hCutFlow" in hName):
                hKey = hName
            else:
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

def createPseudo(inFile,outFile):
    f        = r.TFile.Open(inFile) 
    h_dict = {}   
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        hName = h.GetName()
        h.SetDirectory(0)
        if ("hCutFlow" in hName):
            hKey = hName
        else:
            hKey = re.sub(".+_","data_obs_",hName)
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
    luminosity = 137000
    with open(sys.argv[1]) as json_file:
        config = json.load(json_file)
        for sample, sample_cfg in config.items():
            print(sample)
            if("QCD" in sample):
                continue
            if("WJets" in sample):
                continue
            if("ZJets" in sample):
                continue
            #normalizeProcess(sample,sample_cfg['xsec'],luminosity,"results/histograms/lumiScaled/{0}_normalized.root".format(sample))
    # mergeHT(sys.argv[1],luminosity,"QCD","results/histograms/lumiScaled/QCD_normalized.root")    
    # mergeHT(sys.argv[1],luminosity,"ZJets","results/histograms/lumiScaled/ZJets_normalized.root")
    # mergeHT(sys.argv[1],luminosity,"WJets","results/histograms/lumiScaled/WJets_normalized.root")
    mergeData("/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/nonScaled/data_obs.root","/afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/lumiScaled/data_obs.root")