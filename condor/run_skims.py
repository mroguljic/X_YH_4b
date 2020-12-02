#!/usr/bin/env python

import os, sys, re
from pathlib import Path

from templates import *

def split_jobs(files, njobs):
  for i in range(0, len(files), njobs):
    yield files[i:i + njobs]




def create_jobs(config, dry=True, queue='',jobs_dir="",out_dir="",nFiles=1):
    for sample, sample_cfg in config.items():
      #print(sample)
      if re.match('^X', sample):
        proctype = 'sig'
      elif re.match('^Data', sample):
        proctype = 'data'
      else:
        proctype = 'bkg'

      if(proctype=='data'):
        dataFlag = '--data'
      else:
        dataFlag = ''
      
      sampleJobs_dir = os.path.join(jobs_dir,sample)
      sampleOut_dir = os.path.join(out_dir, sample)
      #Create dir to store jobs and dir to store output
      Path(os.path.join(sampleJobs_dir, 'input')).mkdir(parents=True, exist_ok=True)
      Path(os.path.join(sampleJobs_dir, 'output')).mkdir(parents=True, exist_ok=True)
      Path(sampleOut_dir).mkdir(parents=True, exist_ok=True)

      #Create condor file and sh file
      exeScript = skim_template.replace("JOB_DIR",sampleJobs_dir)
      open(os.path.join(sampleJobs_dir, 'input', 'run_{}.sh'.format(sample)), 'w').write(exeScript)

      condor_script = re.sub('EXEC',os.path.join(sampleJobs_dir, 'input', 'run_{}.sh'.format(sample)), skim_condor)
      condor_script = re.sub('ARGFILE',os.path.join(sampleJobs_dir, 'input', 'args_{}.txt'.format(sample)), condor_script)
      condor_script = re.sub('OUTPUT',os.path.join(sampleJobs_dir, 'output'), condor_script)
      condor_script = re.sub('QUEUE',queue, condor_script)
      open(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample)), 'w').write(condor_script)

      #Split input files
      dataset = sample_cfg["dataset"]
      if dataset.split('/')[-1] == "USER":
        instance = 'prod/phys03'
      else:
        instance = 'global'
      das_query=[]
      for singleDataset in dataset.split(','):
        query = "dasgoclient -query='file dataset={singleDataset} instance={instance}'".format(**locals())
        das_query.append(query)
      import subprocess
      allFiles = []
      for query in das_query:
        files = subprocess.check_output(das_query, shell=True).split()
        for file in files:
          allFiles.append(file.decode("utf-8"))
      job_list = split_jobs(allFiles, nFiles)


      #Create file with arguments to the python script
      argsFile = open(os.path.join(sampleJobs_dir, 'input', 'args_{}.txt'.format(sample)), 'w')
      for n, l  in enumerate(list(job_list)):
        #print(n,l)
        inputPath = os.path.join(sampleJobs_dir, 'input', 'input_{}.txt'.format(n))
        outputPath = os.path.join(sampleOut_dir,'{0}_{1}.root'.format(sample,n))
        open(inputPath, 'w').writelines("{}\n".format('root://cms-xrd-global.cern.ch//'+root_file) for root_file in l)
        argsFile.write("-i {0} -o {1} {2}\n".format(inputPath,outputPath,dataFlag))        

      #Submit
      print("condor_submit {0}".format(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample))))
      if dry==False:
        job_output = subprocess.call(["condor_submit",  "{0}".format(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample)))])


def main():

  import json
  
  from argparse import ArgumentParser
  parser = ArgumentParser(description="Do -h to see usage")

  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-c', '--config', help='Job config file in JSON format')
  parser.add_argument('-d', '--dry', action='store_true', help='Dry run (Do not submit jobs)')
  parser.add_argument('-o', '--outdir',help='Output directory')
  parser.add_argument('-j', '--jobdir',help='Jobs directory')
  parser.add_argument('-n', '--nFiles',help='Number of files per job',type=int,default=1)
  parser.add_argument("-q", "--queue", dest="queue", action='store', default='longlunch', help="Default is 'longlunch' (This parameter is optional)", metavar="QUEUE")
 
  args = parser.parse_args()

  print(args)
#/eos/cms/store/group/phys_b2g/mrogulji/skims/2016
#/afs/cern.ch/work/m/mrogulji/X_YH_4b/condor/skimJobs/2016
  with open(args.config, 'r') as config_file:
    config = json.load(config_file)
    create_jobs(config, args.dry,queue=args.queue,out_dir=args.outdir,jobs_dir=args.jobdir,nFiles=args.nFiles)
          

      

if __name__ == "__main__":
  main()

