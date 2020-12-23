import os
import sys

year = sys.argv[1]

evtSelDir = "results/eventSelection/{0}".format(year)
templateDir = "results/templates/{0}".format(year)

files = [f for f in os.listdir(evtSelDir) if (os.path.isfile(os.path.join(evtSelDir, f)) and ".root" in f)]
for file in files:
    inputFile = os.path.join(evtSelDir,file)
    outputFile = os.path.join(templateDir,"nonScaled/",file)
    process = file.replace(".root","")
    cmd = "python templateMaker.py -i {0} -o {1} -y {2} -p {3}".format(inputFile,outputFile,year,process)
    print(cmd)
    os.system(cmd)