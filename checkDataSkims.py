import os
import ROOT as r
import json

skimsPath = "/eos/cms/store/group/phys_b2g/XToHYTo4B/skims_v2/v2_25May2020"
year = "2018"
yearPath = os.path.join(skimsPath,year)
sampleDirs = os.listdir(yearPath)
sampleDirs = ["DataA","DataB","DataC","DataD"]
yearSummary = {}
for sampleDir in sampleDirs:
    tempDir = os.path.join(yearPath,sampleDir)
    files = os.listdir(tempDir)
    nSampleProc = 0
    nSampleSkim = 0
    validFiles = []
    invalidFiles = []
    for file in files:
        nSkim = 0
        f = r.TFile.Open(os.path.join(tempDir,file))
        try:
            nSkim = f.Get("Events").GetEntriesFast()
            if(nSkim>0):
                print(nSkim,file)
                validFiles.append(file)
            else:
                invalidFiles.append(file)
        except:
            invalidFiles.append(file)
        nSampleSkim+=nSkim
    sampleSummary = {}
    sampleSummary["valid"] = len(validFiles)
    sampleSummary["invalid"] = invalidFiles
    sampleSummary["nSkim"] = nSampleSkim
    yearSummary[sampleDir] = sampleSummary

print(yearSummary)
json.dump(yearSummary,open("checkDataSkims.json","w"))
