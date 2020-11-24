#!/usr/bin/env python

import os, sys, re
from pathlib import Path
from templates import *

def split_jobs(files, njobs):
  for i in range(0, len(files), njobs):
    yield files[i:i + njobs]




def create_jobs(config, dry=True, queue='',year="2016",jobs_dir="",out_dir=""):
    for sample, sample_cfg in config.items():
      print(sample)
      if re.match('^X', sample):
        proctype = 'sig'
      elif re.match('^Data', sample):
        proctype = 'data'
      else:
        proctype = 'bkg'
      
      sampleJobs_dir = os.path.join(jobs_dir,sample)
      sampleOut_dir = os.path.join(out_dir, sample)
      #Create dir to store jobs and dir to store output
      Path(os.path.join(sampleJobs_dir, 'input')).mkdir(parents=True, exist_ok=True)
      Path(os.path.join(sampleJobs_dir, 'output')).mkdir(parents=True, exist_ok=True)
      Path(sampleOut_dir).mkdir(parents=True, exist_ok=True)

      #Create condor file and sh file
      exeScript = selection_template.replace("JOB_DIR",sampleJobs_dir)
      open(os.path.join(sampleJobs_dir, 'input', 'run_{}.sh'.format(sample)), 'w').write(exeScript)

      condor_script = re.sub('EXEC',os.path.join(sampleJobs_dir, 'input', 'run_{}.sh'.format(sample)), selection_condor)
      condor_script = re.sub('ARGFILE',os.path.join(sampleJobs_dir, 'input', 'args_{}.txt'.format(sample)), condor_script)
      condor_script = re.sub('OUTPUT',os.path.join(sampleJobs_dir, 'output'), condor_script)
      condor_script = re.sub('QUEUE',queue, condor_script)
      open(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample)), 'w').write(condor_script)

      #Split input files
      skimDirectory = sample_cfg["dataset"]
      skimFiles = [os.path.join(skimDirectory, f) for f in os.listdir(skimDirectory) if os.path.isfile(os.path.join(skimDirectory, f))]
      njobs = int(max(1, len(skimFiles)/20))
      job_list = split_jobs(skimFiles, njobs)
      import subprocess

      #Create file with arguments to the python script
      argsFile = open(os.path.join(sampleJobs_dir, 'input', 'args_{}.txt'.format(sample)), 'w')
      if(proctype=="sig"):
        ymass = "-m {0}".format(sample_cfg["YMass"])
      else:
        ymass = ''
      for n, l  in enumerate(list(job_list)):
        inputPath = os.path.join(sampleJobs_dir, 'input', 'input_{}.txt'.format(n))
        outputPath = os.path.join(sampleOut_dir,'{0}_{1}.root'.format(sample,n))
        open(inputPath, 'w').writelines("{}\n".format(root_file) for root_file in l)
        argsFile.write("-i {0} -o {1} --{2} -p {3} {4} -y {5}\n".format(inputPath,outputPath,proctype,sample,ymass,year))
      #Submit
      if dry==False:
        print("condor_submit {0}".format(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample))))
        job_output = subprocess.call(["condor_submit", "{0}".format(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample)))],shell=True)
        print(job_output)

def main():

  import json
  
  from argparse import ArgumentParser
  parser = ArgumentParser(description="Do -h to see usage")

  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-c', '--config', help='Job config file in JSON format')
  parser.add_argument('-y', '--year', help='Dataset year',default="2016")
  parser.add_argument('-d', '--dry', action='store_true', help='Dry run (Do not submit jobs)')
  parser.add_argument('-o', '--outdir',help='Output directory')
  parser.add_argument('-j', '--jobdir',help='Jobs directory')
  parser.add_argument("-q", "--queue", dest="queue", action='store', default='longlunch', help="Default is 'longlunch' (This parameter is optional)", metavar="QUEUE")
 
  args = parser.parse_args()

  print(args)

  with open(args.config, 'r') as config_file:
    config = json.load(config_file)
    create_jobs(config, args.dry,queue=args.queue, year=args.year,out_dir=args.outdir,jobs_dir=args.jobdir)
          

      

if __name__ == "__main__":
  main()

