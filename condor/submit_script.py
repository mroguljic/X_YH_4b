import os
from pathlib import Path
import sys
year = sys.argv[1]
outDir = "/eos/cms/store/group/phys_b2g/mrogulji/{0}/06.11.".format(year)
runDir = "./{0}/06.11.".format(year)
thisDir = os.getcwd()
Path(outDir).mkdir(parents=True, exist_ok=True)
Path(runDir).mkdir(parents=True, exist_ok=True)
os.chdir(runDir)
print(os.getcwd())
ttbarCMD = "python {0}/run_jobs.py -c {0}/{1}_config/ttbar_submit.json -o {2} -y {1} batch -q workday".format(thisDir,year,outDir)
print(ttbarCMD)
qcdCMD = "python {0}/run_jobs.py -c {0}/{1}_config/qcd_submit.json -o {2} -y {1} batch -q workday".format(thisDir,year,outDir)
print(qcdCMD)
otherCMD = "python {0}/run_jobs.py -c {0}/{1}_config/other_submit.json -o {2} -y {1} batch -q longlunch".format(thisDir,year,outDir)
print(otherCMD)
dataCMD = "python {0}/run_jobs.py -c {0}/{1}_config/data_submit.json -o {2} -y {1} batch -q tomorrow".format(thisDir,year,outDir)
print(dataCMD)

if(sys.argv[2]=="submit"):
    print("bkg")
    #os.system(ttbarCMD)
    #os.system(qcdCMD)
    #os.system(otherCMD)
    os.system(dataCMD)


sig_samples=["X800","X900","X1000","X1200","X1400","X1600","X1800","X2000"]
for sig in sig_samples:
    Path(sig).mkdir(parents=True, exist_ok=True)
    os.chdir(sig)
    sigCMD = "python {0}/run_jobs.py -c {0}/{2}_config/{1}_submit.json -o {3} -y {2} batch -q espresso".format(thisDir,sig,year,outDir)
    print(os.getcwd())
    print(sigCMD)
    if(sys.argv[2]=="submit"):
        print("skipping sig")
        #os.system(sigCMD)

    os.chdir("./..")


