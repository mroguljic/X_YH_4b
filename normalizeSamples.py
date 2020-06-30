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
        hCutFlow = f.Get("hCutFlow_pnet")#nTotal is the same for pnet and dak8
        nTotal   = hCutFlow.GetBinContent(1)
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            print(hName, h.Integral())
            nRegion  = h.Integral()
            eff      = nRegion/nTotal
            norm     = eff*luminosity*xsec
            print(norm/h.Integral())
            h.Scale(norm/h.Integral())
            h.SetDirectory(0)
            h_dict[hName] = h
        f.Close()
    f = r.TFile(outFile,"recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()

def mergeQCD(luminosity):
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
            hCutFlow = f.Get("hCutFlow_pnet")#nTotal is the same for pnet and dak8
            nTotal   = hCutFlow.GetBinContent(1)
            for key in f.GetListOfKeys():
                h = key.ReadObj()
                hName = h.GetName()
                if not "QCD" in hName:
                    continue
                nRegion  = h.Integral()
                eff      = nRegion/nTotal
                norm     = eff*luminosity*xsec
                h.Scale(norm/h.Integral())
                h.SetDirectory(0)
                hKey = re.sub("QCD\d+_","QCD_",hName)
                if not hKey in h_dict:
                    h.SetName(hKey)
                    h_dict[hKey] = h
                else:
                    h_dict[hKey].Add(h)
            f.Close()
    f = r.TFile("QCD_normalized.root","recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()

if __name__ == '__main__':
    luminosity = 137000
    mergeQCD(luminosity)
    #normalizeProcess("ttbar",luminosity,"ttbar_normalized.root")
    #normalizeProcess("X1600",luminosity,"X1600_normalized.root")