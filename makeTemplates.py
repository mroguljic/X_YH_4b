import os
import sys
from pathlib import Path

year = sys.argv[1]

evtSelDir = "results/eventSelection/{0}".format(year)
templateDir = "results/templates/WP_0.8_0.9/{0}".format(year)
samples = ["QCD700","QCD1000","QCD1500","QCD2000","TTbar","TTbarHT"]#add signals
variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown"]
for process in samples:
    for variation in variations:
        inputFile = "{0}/{1}_{2}.root".format(evtSelDir,process,variation)
        outputFile = os.path.join(templateDir,"nonScaled/",process)
        Path(templateDir+"/nonScaled").mkdir(parents=True, exist_ok=True)
        Path(templateDir+"/scaled").mkdir(parents=True, exist_ok=True)
        if(variation=="nom"):
            mode="RECREATE"
        else:
            mode="UPDATE"
        cmd = "python templateMaker.py -i {0} -o {1} -y {2} -p {3} -v {4} -m {5}".format(inputFile,outputFile,year,process,variation,mode)
        print(cmd)
        os.system(cmd)