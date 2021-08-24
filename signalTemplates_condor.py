import os
import sys
from pathlib import Path

process = sys.argv[1]
iDir = sys.argv[2]
outDir = sys.argv[3]
wpL     = sys.argv[4]
wpT     = sys.argv[5]

if("2016" in iDir):
    year=2016
if("2017" in iDir):
    year=2017
if("2018" in iDir):
    year=2018

variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown","trigUp","trigDown","pnetUp","pnetDown","puRwtUp","puRwtDown"]
for variation in variations:
    if("pnet" in variation or "trig" in variation or "puRwt" in variation):
        inputTag = "nom"
    else:
        inputTag = variation

    inputFile = "{0}/{1}_{2}.root".format(iDir,process,inputTag)
    outputFile = os.path.join(outDir,"nonScaled/",process)
    outputFile = outputFile+".root"
    Path(outDir+"/nonScaled").mkdir(parents=True, exist_ok=True)
    Path(outDir+"/scaled").mkdir(parents=True, exist_ok=True)
    if(variation=="nom"):
        mode="RECREATE"
    else:
        mode="UPDATE"
    cmd = "python templateMaker.py -i {0} -o {1} -y {2} -p {3} -v {4} -m {5} -w {6} {7}".format(inputFile,outputFile,year,process,variation,mode,wpL,wpT)
    print(cmd)
    os.system(cmd)