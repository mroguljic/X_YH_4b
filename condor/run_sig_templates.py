#!/usr/bin/env python

import os, sys, re
from pathlib import Path
from templates import *

# python run_sig_templates.py -i /afs/cern.ch/work/m/mrogulji/X_YH_4b/results/eventSelection/forUL/2016/ -o /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/2016/ -j /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/condor/templates_signal/2016/ --wpL 0.94 --wpT 0.98
# python run_sig_templates.py -i /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2016/ -o /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/2016/ -j /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/condor/templates_signal/2016/ --wpL 0.94 --wpT 0.98
# python run_sig_templates.py -i /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2017/ -o /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/2017/ -j /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/condor/templates_signal/2017/ --wpL 0.94 --wpT 0.98
# python run_sig_templates.py -i /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/eventSelection/2018/ -o /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/2018/ -j /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/condor/templates_signal/2018/ --wpL 0.94 --wpT 0.98

def create_jobs(inputDir,outputDir,wpL,wpT,jobs_dir):
          #Create dir to store jobs and dir to store output
    Path(os.path.join(jobs_dir, 'input')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(jobs_dir, 'output')).mkdir(parents=True, exist_ok=True)

    exeScript = templates_signal.replace("JOB_DIR",jobs_dir)
    open(os.path.join(jobs_dir, 'input', 'run.sh'), 'w').write(exeScript)

    condor_script = re.sub('EXEC',os.path.join(jobs_dir, 'input', 'run.sh'), templates_condor)
    condor_script = re.sub('ARGFILE',os.path.join(jobs_dir, 'input', 'args.txt'), condor_script)
    condor_script = re.sub('OUTPUT',os.path.join(jobs_dir, 'output'), condor_script)
    open(os.path.join(jobs_dir, 'input', 'condor_sig.condor'), 'w').write(condor_script)

      #Create file with arguments to the python script
    argsFile = open(os.path.join(jobs_dir, 'input', 'args.txt'), 'w')
    directories=[d for d in os.listdir(inputDir) if os.path.isdir(os.path.join(inputDir,d))]
    for directory in directories:
        sample = directory.split("/")[-1]
        if not "MX" in sample:
            continue
        argsFile.write("{0} {1} {2} {3} {4}\n".format(sample,inputDir,outputDir,wpL,wpT))

    print("condor_submit {0}".format(os.path.join(jobs_dir, 'input', 'condor_sig.condor')))


def main():
    import json

    from argparse import ArgumentParser
    parser = ArgumentParser(description="Do -h to see usage")

    parser.add_argument('-i', '--input',  help='Directory with selected event trees')
    parser.add_argument('-o', '--output', help='Directory where templates will be stored')
    parser.add_argument('-j', '--jobdir', help='Jobs directory') 
    parser.add_argument('--wpL', help='Loose Wp') 
    parser.add_argument('--wpT', help='Tight Wp') 
    args = parser.parse_args()

    print(args)
    create_jobs(args.input,args.output,args.wpL,args.wpT,args.jobdir)
              

      

if __name__ == "__main__":
    main()

