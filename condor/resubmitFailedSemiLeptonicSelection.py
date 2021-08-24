import os
import sys
import os.path
from os import path
import ROOT as r
targetDir = sys.argv[1]

samples         = os.listdir(targetDir)
failedJobs      = 0
submit_cmds     = []
variationsSig   = ["nom","jerUp","jerDown","jesUp","jesDown","sfUp","sfDown"]
for sample in samples:
    inputDir    = targetDir+"/"+sample+"/"+"input/"
    condorFile  = "condor_{0}.condor".format(sample)
    argsFile    =  "args_{0}.txt".format(sample)
    f = open(inputDir+argsFile,"r")
    args = f.readlines()
    missingFileFlag = 0
    for argSet in args:
        argArr  = argSet.split(" ")
        outputFile = argArr[3]
        for var in variationsSig:
            if(("EGamma" in sample) or "Single" in sample):
                if(var!="nom"):
                    continue
            tempFileName = outputFile.replace(".root","_{0}.root".format(var))
            if not(path.exists(tempFileName)):
                #print("Missing: ", tempFileName)
                missingFileFlag = 1
                cmdToRun = "python semiLeptonicSelection.py "+argSet.replace("\n","")+" --var {0}".format(var)
                print(cmdToRun)
    f.close()
    # if(missingFileFlag):
    #     submit_cmd = "condor_submit {0}/{1}".format(inputDir,condorFile)
    #     submit_cmds.append(submit_cmd)

# for submission in submit_cmds:
#     print(submission)
# print(submit_cmd)    

    #     if(path.exists(outputFile)):
    #         try:
    #             temp = r.TFile.Open(outputFile)
    #             temp.Get("Events").GetEntriesFast()
    #             varFlag = True
    #             if("TTbar" in outputFile or "MX" in outputFile):
    #                 if("MX" in outputFile):
    #                     variations = variationsSig
    #                 else:
    #                     variations = variationsTT
    #                 for variation in variations:
    #                     varFile = outputFile.replace("nom",variation)
    #                     if not(path.exists(varFile)):
    #                         print("Missing {0}".format(varFile))
    #                         varFlag = False
    #             if(varFlag):
    #                 continue
    #         except:
    #             print("Caught a zombie: ", outputFile)
    #     toResubmit+=argSet
    #     failedJobs+=1
    # f.close()
#     if not toResubmit:
#         continue
#     f = open(inputDir+argsFile,"w")
#     f.write(toResubmit)
#     submit_cmd = "condor_submit {0}/{1}".format(inputDir,condorFile)
#     submit_cmds.append(submit_cmd)

# print("To resubmit: ", failedJobs)
# for submission in submit_cmds:
#     print(submission)
# print(submit_cmd)
