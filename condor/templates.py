run_script_template='''#!/bin/bash

export WORK_DIR=/afs/cern.ch/user/m/mrogulji/X_YH_4b/

export RUN_DIR=RUNDIR

cd ${RUN_DIR}

python ${WORK_DIR}/eventSelection.py -i ${RUN_DIR}/input/INPUT -o ${RUN_DIR}/output/output_NJOB.root --PROCTYPE -p SAMPLE
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

