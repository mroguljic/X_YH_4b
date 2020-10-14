#!/usr/bin/env python

import os, sys, re

from templates import *

def split_jobs(files, njobs):
  for i in range(0, len(files), njobs):
    yield files[i:i + njobs]




def create_jobs(config, dry=True, batch=False, queue=''):
    for sample, sample_cfg in config.items():
      if re.match('^X', sample):
        proctype = 'sig'
      elif re.match('^Data', sample):
        proctype = 'data'
      else:
        proctype = 'bkg'
      
      run_dir = os.path.join(os.getcwd(), sample)
      os.mkdir(run_dir)
      os.mkdir(os.path.join(run_dir, 'input'))
      os.mkdir(os.path.join(run_dir, 'output'))

      dataset = sample_cfg["dataset"]
      if dataset.split('/')[-1] == "USER":
        instance = 'prod/phys03'
      else:
        instance = 'global'
      das_query=[]
      for singleDataset in dataset.split(','):
        print(singleDataset)
        query = "dasgoclient -query='file dataset={singleDataset} instance={instance}'".format(**locals())
        das_query.append(query)
      import subprocess
      allFiles = []
      for query in das_query:
        files = subprocess.check_output(das_query, shell=True).split()
        for file in files:
          allFiles.append(file.decode("utf-8"))
      njobs = int(max(1, len(allFiles)/50))

      job_list = split_jobs(allFiles, njobs)
      for n, l  in enumerate(list(job_list)):
        #print(n,l)
        open(os.path.join(run_dir, 'input', 'job_{}.txt'.format(n)), 'w').writelines("{}\n".format('root://cms-xrd-global.cern.ch//'+root_file) for root_file in l)
        run_script = run_script_template.replace('INPUT', 'job_{}.txt'.format(n))
        run_script = run_script.replace('NJOB', str(n))
        run_script = run_script.replace('SAMPLE', sample)
        run_script = run_script.replace('RUNDIR', run_dir)
        run_script = run_script.replace('PROCTYPE', proctype)
        if(proctype=="sig"):
          ymass = sample_cfg["YMass"]
          run_script = run_script.replace('YMASS',str(ymass))
        else:
          run_script = run_script.replace('-m YMASS',"")
        open(os.path.join(run_dir, 'input', 'run_{}.sh'.format(n)), 'w').write(run_script)
        
        if batch == True:
          condor_script = re.sub('EXEC', os.path.join(run_dir, 'input', 'run_{}.sh'.format(n)), condor_template)
          condor_script = re.sub('QUEUE', queue, condor_script)
          condor_script = re.sub('JOB_NUMBER', str(n), condor_script)
          condor_script = re.sub('OUTPUT', os.path.join(run_dir, 'output'), condor_script)
          
          open(os.path.join(run_dir, 'input', 'condor_{}.condor'.format(n)), 'w').write(condor_script)
          
          if dry == False:
            print("bash {0}".format(os.path.join(run_dir, 'input', 'run_{}.sh'.format(n))))
            job_output = subprocess.call(["condor_submit",  "{0}".format(os.path.join(run_dir, 'input', 'condor_{}.condor'.format(n)))])


        elif dry == False:
          print("bash {0}".format(os.path.join(run_dir, 'input', 'run_{}.sh'.format(n))))
          job_output = subprocess.call(["bash",  "{0}".format(os.path.join(run_dir, 'input', 'run_{}.sh'.format(n)))])




def main():

  import json
  
  from argparse import ArgumentParser
  parser = ArgumentParser(description="Do -h to see usage")

  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-c', '--config', help='Job config file in JSON format')
  parser.add_argument('-d', '--dry', action='store_true', help='Dry run (Do not submit jobs)')
  
  subparsers = parser.add_subparsers(dest='command')
  
  parser_run = subparsers.add_parser('run', help='Run interactively')
  
  parser_batch = subparsers.add_parser('batch', help='Run batch jobs')
  parser_batch.add_argument("-q", "--queue", dest="queue", action='store', default='longlunch', help="Default is 'longlunch' (This parameter is optional)", metavar="QUEUE")
 
  args = parser.parse_args()

  print(args)

  with open(args.config, 'r') as config_file:
    config = json.load(config_file)

  if args.command == 'run':
    create_jobs(config, args.dry)

  if args.command == 'batch':
    create_jobs(config, args.dry, batch=True, queue=args.queue)
      

      

if __name__ == "__main__":
  main()

