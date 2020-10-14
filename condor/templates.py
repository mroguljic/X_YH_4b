run_script_template='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/X_YH_4b
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/X_YH_4b/

export RUN_DIR=RUNDIR

cd ${RUN_DIR}

echo "${WORK_DIR}/eventSelection.py -i ${RUN_DIR}/input/job_1.txt -o ${RUN_DIR}/output/output_1.root --bkg -p QCD500 -m YMASS"
python ${WORK_DIR}/eventSelection.py -i ${RUN_DIR}/input/INPUT -o ${RUN_DIR}/output/output_NJOB.root --PROCTYPE -p SAMPLE -m YMASS
'''

condor_template = """universe              = vanilla
executable            = EXEC
arguments             = $(ClusterID) $(ProcId)
output                = OUTPUT/job_JOB_NUMBER.out
error                 = OUTPUT/job_JOB_NUMBER.err
log                   = OUTPUT/job_JOB_NUMBER.log
+JobFlavour           = "QUEUE"
use_x509userproxy = true
queue
"""

