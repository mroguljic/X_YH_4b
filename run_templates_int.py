import os
import sys
from pathlib import Path

MX = ["800","900","1000","1200","1400","1600","1800","2000","2200","2400","2600","2800","3000"]
MY = ["40","60","80","100","125","150","200","250","300","400"]#,"600","800","1000","1200","1400","1600","1800"]
signalProcesses = []
iDir = sys.argv[1]
outDir = sys.argv[2]
for mx in MX:
    for my in MY:
        if os.path.isdir(iDir+"/"+"MX{0}_MY{1}".format(mx,my)):
            signalProcesses.append("MX{0}_MY{1}".format(mx,my))

samples2016 = ["TTbar","TTbarMtt700","TTbarMtt1000","QCD700","QCD1000","QCD1500","QCD2000","JetHT2016B","JetHT2016C","JetHT2016D","JetHT2016E","JetHT2016F","JetHT2016G","JetHT2016H"]
samples2017 = ["TTbar","TTbarMtt700","TTbarMtt1000","QCD700","QCD1000","QCD1500","QCD2000","JetHT2017B","JetHT2017C","JetHT2017D","JetHT2017E","JetHT2017F"]
samples2018 = ["TTbar","TTbarMtt700","TTbarMtt1000","QCD700","QCD1000","QCD1500","QCD2000","JetHT2018A","JetHT2018B","JetHT2018C","JetHT2018D"]

if("2016" in iDir):
    year=2016
    samples = samples2016

if("2017" in iDir):
    year=2017
    samples = samples2017
if("2018" in iDir):
    year=2018
    samples = samples2018

    
samples+=signalProcesses

variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown","trigUp","trigDown","pnetUp","pnetDown"]
variations = ["nom"]
samples    = ["TTbar","TTbar_pt_incl","TTbarMtt700","TTbarMtt1000","TTbarSemi","TTbarSemi_incl"]
for process in samples:
    for variation in variations:
        if("pnet" in variation and "MX" not in process):
            continue
        if("pnet" in variation or "trig" in variation):
            inputTag = "nom"
        else:
            inputTag = variation

        if("JetHT" in process and variation!="nom"):
            continue
        if("QCD" in process and variation!="nom"):
            continue            
        inputFile = "{0}/{1}_{2}.root".format(iDir,process,inputTag)
        outputFile = os.path.join(outDir,"nonScaled/",process)
        outputFile = outputFile+".root"
        Path(outDir+"/nonScaled").mkdir(parents=True, exist_ok=True)
        Path(outDir+"/scaled").mkdir(parents=True, exist_ok=True)
        if(variation=="nom"):
            mode="RECREATE"
        else:
            mode="UPDATE"
        cmd = "python templateMaker.py -i {0} -o {1} -y {2} -p {3} -v {4} -m {5} -w 0.8 0.95".format(inputFile,outputFile,year,process,variation,mode)
        print(cmd)
        os.system(cmd)