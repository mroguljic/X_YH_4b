import os
import ROOT as r
import json

skimsPath = "/eos/cms/store/group/phys_b2g/XToHYTo4B/skims_v2/v2_25May2020"
year = "2016"
yearPath = os.path.join(skimsPath,year)
sampleDirs = os.listdir(yearPath)
xsecsFile = open("xsecs.json","r")
xsecs = json.load(xsecsFile)
yearSummary = {}
for sampleDir in sampleDirs:
    if("JetHT" in sampleDir or "SingleMuon" in sampleDir):
        continue
    tempDir = os.path.join(yearPath,sampleDir)
    files = os.listdir(tempDir)
    nSampleProc = 0
    nSampleSkim = 0
    validFiles = []
    invalidFiles = []
    for file in files:
        nProc = 0
        nSkim = 0
        f = r.TFile.Open(os.path.join(tempDir,file))
        try:
            h = f.Get("skimInfo")
            try:
                nProc  = h.GetBinContent(1)
                nSkim = h.GetBinContent(2)
            except:
                nProc=0
                nSkim=0
            if(nProc>0):
                print(nProc,file)
                validFiles.append(file)
            else:
                invalidFiles.append(file)
        except:
            invalidFiles.append(file)
        nSampleProc+=nProc
        nSampleSkim+=nSkim
    sampleSummary = {}
    sampleSummary["valid"] = len(validFiles)
    sampleSummary["invalid"] = invalidFiles
    sampleSummary["nProc"] = nSampleProc
    sampleSummary["nSkim"] = nSampleSkim
    if not "Data" in sampleDir:
        sampleSummary["xsec"] = xsecs[sampleDir]
    yearSummary[sampleDir] = sampleSummary

print(yearSummary)
json.dump(yearSummary,open("checkMCSkims.json","w"))
