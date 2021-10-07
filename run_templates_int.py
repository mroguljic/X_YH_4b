import os
import sys
from pathlib import Path


iDir = sys.argv[1]
outDir = sys.argv[2]

samples2016 = ["TTbar","TTbarHT","QCD700","QCD1000","QCD1500","QCD2000","JetHT2016B","JetHT2016C","JetHT2016D","JetHT2016E","JetHT2016F","JetHT2016G","JetHT2016H","ST_top","ST_antitop","ST_tW_top","ST_tW_antitop","WJets400","WJets600","WJets800","ZJets400","ZJets600","ZJets800","ZH","WminusH","WplusH"]
samples2017 = ["TTbar","TTbarSemi","TTbarMtt700","TTbarMtt1000","QCD700","QCD1000","QCD1500","QCD2000","JetHT2017B","JetHT2017C","JetHT2017D","JetHT2017E","JetHT2017F"]
samples2018 = ["TTbar","TTbarSemi","TTbarMtt700","TTbarMtt1000","QCD700","QCD1000","QCD1500","QCD2000","JetHT2018A","JetHT2018B","JetHT2018C","JetHT2018D"]



if("2016" in iDir):
    year=2016
    samples = samples2016
    wpL = 0.94
    wpT = 0.98

if("2017" in iDir):
    year=2017
    samples = samples2017
    wpL = 0.94
    wpT = 0.98

if("2018" in iDir):
    year=2018
    samples = samples2018
    wpL = 0.94
    wpT = 0.98


variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown","trigUp","trigDown","pnetUp","pnetDown","ptRwtUp","ptRwtDown","puRwtUp","puRwtDown"]
varsFromNomTree = ["trigUp","trigDown","pnetUp","pnetDown","ptRwtUp","ptRwtDown","puRwtUp","puRwtDown"]
for process in samples:
    for variation in variations:
        if("ptRwt" in variation and "TTbar" not in process):
            continue
        if("pnet" in variation and "MX" not in process):
            continue
        if(variation!="nom" and not ("MX" in process or "TTbar" in process or "QCD" in process)):
            continue           
        if("QCD" in process and not (variation=="nom" or "puRwt" in variation)):
            continue

        if(variation in varsFromNomTree):
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
