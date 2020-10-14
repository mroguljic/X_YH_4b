import ROOT as r
import json
import re



def normalizeProcess(process,luminosity,outFile):
    with open("results.json") as json_file:
        data = json.load(json_file)
        h_dict = {}
        processInfo = data[process]
        xsec     = processInfo['xsec']
        file     = processInfo['file']
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
            if not ("hCutFlow" in h.GetName()):
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

def mergeQCD(luminosity,outFile):
    with open("results.json") as json_file:
        data = json.load(json_file)
        h_dict = {}
        for sample, sample_cfg in data.items():
            if not "QCD" in sample:
                continue
            xsec     = sample_cfg['xsec']
            file     = sample_cfg['file']
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
                if not ("hCutFlow" in hName):
                    h.Scale(scaling)
                h.SetDirectory(0)
                hKey = re.sub("QCD\d+_","QCD_",hName)
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
    mergeQCD(luminosity,"results/histograms/QCD_normalized.root")
    normalizeProcess("ttbar",luminosity,"results/histograms/ttbar_normalized.root")
    normalizeProcess("X1600_Y100",luminosity,"results/histograms/X1600_Y100_normalized.root")