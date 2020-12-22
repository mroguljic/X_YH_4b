run_script_template='''#!/bin/bash

cd /afs/cern.ch/user/d/devdatta/afswork/CMSREL/Analysis/X_YH_4b/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/X_YH_4b
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/X_YH_4b/

export RUN_DIR=RUNDIR
export OUT_DIR=OUTDIR
cd ${RUN_DIR}

echo "${WORK_DIR}/eventSelection.py -i ${RUN_DIR}/input/INPUT -o ${OUT_DIR}/output/output_NJOB.root --PROCTYPE -p SAMPLE -m YMASS -y YEAR"
python ${WORK_DIR}/eventSelection.py -i ${RUN_DIR}/input/INPUT -o ${OUT_DIR}/output/output_NJOB.root --PROCTYPE -p SAMPLE -m YMASS -y YEAR
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

selection_condor = """universe              = vanilla
executable            = EXEC
output                = OUTPUT/output_$(Cluster)_$(Process).out
error                 = OUTPUT/output_$(Cluster)_$(Process).err
log                   = OUTPUT/output_$(Cluster)_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
use_x509userproxy = true
Queue args from ARGFILE
queue
"""

selection_template='''#!/bin/bash

cd /afs/cern.ch/user/d/devdatta/afswork/CMSREL/Analysis/X_YH_4b/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/X_YH_4b
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/X_YH_4b/
cd JOB_DIR

echo ${WORK_DIR}/eventSelection.py $*
python ${WORK_DIR}/eventSelection.py $*
'''

skim_template='''#!/bin/bash
export WORK_DIR=/afs/cern.ch/user/d/devdatta/afswork/CMSREL/Analysis/X_YH_4b/X_YH_4b/
cd /afs/cern.ch/user/d/devdatta/afswork/CMSREL/Analysis/X_YH_4b/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/user/d/devdatta/afswork/CMSREL/Analysis/X_YH_4b/
source timber-env/bin/activate
cd JOB_DIR
echo ${WORK_DIR}/skim.py $*
python ${WORK_DIR}/skim.py $*
'''

skim_condor = """universe              = vanilla
executable            = EXEC
output                = OUTPUT/output_$(Cluster)_$(Process).out
error                 = OUTPUT/output_$(Cluster)_$(Process).err
log                   = OUTPUT/output_$(Cluster)_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
use_x509userproxy = true
Queue args from ARGFILE
queue
"""

semileptonic_condor = """universe              = vanilla
executable            = EXEC
output                = OUTPUT/output_$(Cluster)_$(Process).out
error                 = OUTPUT/output_$(Cluster)_$(Process).err
log                   = OUTPUT/output_$(Cluster)_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
use_x509userproxy = true
Queue args from ARGFILE
queue
"""

semileptonic_template='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/X_YH_4b/CMSSW_11_1_5/src
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/X_YH_4b
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/X_YH_4b/
cd JOB_DIR

echo ${WORK_DIR}/semiLeptonicSelection.py $*
python ${WORK_DIR}/semiLeptonicSelection.py $*
'''
