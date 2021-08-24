import ROOT as r
import os

MX = [800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000]
MY = [40,50,60,70,80,90,100,125,150,200,250,300,350,400,450,500,600,700,800]#,600,800,1000,1200,1400,1600,1800]
signalPoints  = []
for X in MX:
    for Y in MY:
        signalPoints.append("MX{0}_MY{1}".format(X,Y))

for signalPoint in signalPoints:
    for year in ["16","17","18"]:
        sourceFile = "../results/templates_hadronic/20{0}/scaled/{1}.root".format(year,signalPoint)
        targetFile  = "remadeSignal/20{0}/{1}.root".format(year,signalPoint)
        
        if not(os.path.exists(sourceFile)):
            continue

        h_dict = {}
        f = r.TFile.Open(sourceFile)
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            h.SetDirectory(0)
            h_dict[hName] = h
            if("T_AL" in hName or "L_AL" in hName):
                h.Reset()
        f.Close()

        f = r.TFile(targetFile,"RECREATE")
        f.cd()
        for key in h_dict:
            histo = h_dict[key]
            histo.Write()
        f.Close()