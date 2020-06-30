import ROOT as r

def makePseudo(processes,outFile):
    h_dict = {}
    for process in processes:
        fName = process+"_normalized.root"
        f = r.TFile.Open(fName,"r")
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            h.SetDirectory(0)
            if not process in hName:
                continue
            pseudoName = hName.replace(process,"pdata")
            if not pseudoName in h_dict:
                h.SetName(pseudoName)
                h_dict[pseudoName] = h
            else:
                h_dict[pseudoName].Add(h)
        f.Close()

    f = r.TFile(outFile,"recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()

processes = ["QCD","ttbar"]
makePseudo(["QCD","ttbar"],"pseudo.root")
makePseudo(["QCD"],"pseudo_QCD.root")
makePseudo(["ttbar"],"pseudo_ttbar.root")
