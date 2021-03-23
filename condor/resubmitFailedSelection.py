import os
import sys
import os.path
from os import path
import ROOT as r
targetDir = sys.argv[1]

samples         = os.listdir(targetDir)
failedJobs      = 0
submit_cmds     = []
variations      = ["jerUp","jerDown","jesUp","jesDown","jmsUp","jmsDown","jmrUp","jmrDown"]
for sample in samples:
    inputDir    = targetDir+"/"+sample+"/"+"input/"
    condorFile  = "condor_{0}.condor".format(sample)
    argsFile    =  "args_{0}.txt".format(sample)
    f = open(inputDir+argsFile,"r")
    args = f.readlines()
    toResubmit  = ""
    for argSet in args:
        argArr  = argSet.split(" ")
        outputFile = argArr[3]
        outputFile = outputFile.replace(".root","_nom.root")
        print(outputFile)
        if(path.exists(outputFile)):
            try:
                temp = r.TFile.Open(outputFile)
                temp.Get("Events").GetEntriesFast()
                varFlag = True                
                for variation in variations:
                    if("JetHT" in outputFile or "SingleMuon" in outputFile or "QCD" in outputFile):
                        continue
                    varFile = outputFile.replace("nom",variation)
                    if not(path.exists(varFile)):
                        print("Missing {0}".format(varFile))
                        varFlag = False
                if(varFlag):
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
