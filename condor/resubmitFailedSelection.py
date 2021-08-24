import os
import sys
import os.path
from os import path
import ROOT as r
targetDir = sys.argv[1]
import time

def file_age(filepath):
    #last modification of file in days
    return (time.time() - os.path.getmtime(filepath))/(24*3600.)


def checkFile(fileName):
    if not path.exists(tempFileName):
        return False
    try:
        f = r.TFile.Open(tempFileName)
        tree = f.Get("Events")
        nEntries = tree.GetEntriesFast()
        if(nEntries<1):
            return False
        else:
            return True
    except:
        return False



samples         = os.listdir(targetDir)
failedJobs      = 0
submit_cmds     = []
if("semileptonic" in targetDir.lower()):
    semilepFlag = True
    variationsSig   = ["nom","jerUp","jerDown","jesUp","jesDown","sfUp","sfDown"]
else:
    semilepFlag = False
    variationsSig   = ["nom","jerUp","jerDown","jesUp","jesDown","jmsUp","jmsDown","jmrUp","jmrDown"]

for sample in samples:
    toResubmit  = ""
    # if not "MX" in sample:
    #     continue
    inputDir        = targetDir+"/"+sample+"/"+"input/"
    condorFile      = inputDir+"condor_{0}.condor".format(sample)
    argsFile        = inputDir+"args_{0}.txt".format(sample)
    argsFileBackup  = argsFile.replace(".txt","_ORIG.txt")
    with open(argsFile,"r") as f:
        argsLen     = (len(f.readlines()))
    if not(path.exists(argsFileBackup)):
        backupLen   = 0
    else:
        with open(argsFileBackup,"r") as f:
            backupLen   = (len(f.readlines()))

    if (argsLen>backupLen):
        os.system("cp {0} {1}".format(argsFile,argsFileBackup))
    f = open(argsFileBackup,"r")
    #f = open(argsFile,"r")
    args = f.readlines()
    for argSet in args:
        missingFileFlag = 0
        argArr  = argSet.split(" ")
        outputFile = argArr[3]
        for var in variationsSig:
            if(var!="nom" and not ("TTbar" in sample or "MX" in sample) and not semilepFlag):
                continue
            if(var!="nom" and semilepFlag and ("SingleMuon" in sample or "EGamma" in sample or "SingleElectron" in sample)):
                continue
            tempFileName = outputFile.replace(".root","_{0}.root".format(var))
            if(checkFile(tempFileName) and file_age(tempFileName)<2.):
            #If files exists and younger than 2 days
                continue
            else:
                #print("Missing: ", tempFileName)
                missingFileFlag = 1
                cmdToRun = "python eventSelection.py "+argSet.replace("\n","")+" --var {0}".format(var)
                print(cmdToRun)
            # else:
            #     print("Found ", tempFileName)

        if missingFileFlag:
            toResubmit+=argSet
    f.close()
    # f = open(argsFile,"w")
    # f.write(toResubmit)
    # if(toResubmit):
    #     submit_cmd = "condor_submit {0}".format(condorFile)
    #     print(submit_cmd)
    #     submit_cmds.append(submit_cmd)

# print("To resubmit: ", failedJobs)
# for submission in submit_cmds:
#     print(submission)
# print(submit_cmd)
