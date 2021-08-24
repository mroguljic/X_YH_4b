import os
import sys
from pathlib import Path

iDir = sys.argv[1]
outDir = sys.argv[2]


samples = [d for d in os.listdir(iDir) if os.path.isdir(iDir+"/"+d)]


if("2016" in iDir):
    year=2016
    wpL = 0.94
    wpT = 0.98
if("2017" in iDir):
    year=2017
    wpL = 0.94
    wpT = 0.98
if("2018" in iDir):
    year=2018
    wpL = 0.94
    wpT = 0.98

variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown","trigUp","trigDown","sfUp","sfDown","IdUp","IdDown","ptRwtUp","ptRwtDown","puRwtUp","puRwtDown"]
varsSeparateSelection = ["sfUp","sfDown","jesUp","jesDown","jerUp","jerDown"]
for process in samples:
    print(process) 
    for variation in variations:
        if("SingleMuon" in process and variation!="nom"):
            continue
        if("SingleElectron" in process and variation!="nom"):
            continue
        if("EGamma" in process and variation!="nom"):
            continue
        if("ptRwt" in variation and not "TTbar" in process):
            continue
        if(variation in varsSeparateSelection):
            inputTag = variation
        else:
            inputTag = "nom"
        inputFile  = "{0}/{1}_{2}.root".format(iDir,process,inputTag)
        outputFile = os.path.join(outDir,"nonScaled/",process)
        outputFile = outputFile+".root"
        Path(outDir+"/nonScaled").mkdir(parents=True, exist_ok=True)
        Path(outDir+"/scaled").mkdir(parents=True, exist_ok=True)
        if(variation=="nom"):
            mode="RECREATE"
        else:
            mode="UPDATE"
        cmd = "python makeSemiLeptonicTemplates.py -i {0} -o {1} -y {2} -p {3} -v {4} -m {5} -w {6} {7}".format(inputFile,outputFile,year,process,variation,mode,wpL,wpT)
        print(cmd)
        os.system(cmd)