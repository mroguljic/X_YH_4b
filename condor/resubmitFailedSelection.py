import os
import sys
import os.path
from os import path
import ROOT as r
targetDir = sys.argv[1]

samples = os.listdir(targetDir)
failedJobs=0
submit_cmds=[]
for sample in samples:
    inputDir   = targetDir+"/"+sample+"/"+"input/"
    condorFile = "condor_{0}.condor".format(sample)
    argsFile   =  "args_{0}.txt".format(sample)
    f = open(inputDir+argsFile,"r")
    args = f.readlines()
    toResubmit = ""
    for argSet in args:
        argArr = argSet.split(" ")
        outputFile = argArr[3]
        if(path.exists(outputFile)):
            try:
                temp = r.TFile.Open(outputFile)
                temp.Get("Events").GetEntriesFast()
            #print(outputFile, " exists")
                continue
            except:
                print("Caught a zombie: ", outputFile)
        toResubmit+=argSet
        failedJobs+=1
    f.close()
    if not toResubmit:
        continue
    f = open(inputDir+argsFile,"w")
    f.write(toResubmit)
    submit_cmd = "condor_submit {0}/{1}".format(inputDir,condorFile)
    submit_cmds.append(submit_cmd)

print("To resubmit: ", failedJobs)
for submission in submit_cmds:
    print(submission)
print(submit_cmd)
