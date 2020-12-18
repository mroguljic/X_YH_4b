import ROOT as r
import os
import sys
#Extract histogram from files in the input dir and place at destination

inputDir = sys.argv[1]
outputDir= sys.argv[2]

allFiles = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f))]

for f in allFiles:
    if not ".root" in f:
        continue
    tag = f.replace(".root","")
    cmd = "rootmv --recreate {0}/{1}:{2}* {3}/{1}".format(inputDir,f,tag,outputDir)
    print(cmd)
    os.system(cmd)