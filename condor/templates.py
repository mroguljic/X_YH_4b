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
output                = OUTPUT/output_$(Process).out
error                 = OUTPUT/output_$(Process).err
log                   = OUTPUT/output_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
use_x509userproxy = true
Queue args from ARGFILE
queue
"""

selection_template='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/
cd JOB_DIR

echo eventSelection.py $*
python $WORK_DIR/eventSelection.py $* --var nom
python $WORK_DIR/eventSelection.py $* --var jesDown
python $WORK_DIR/eventSelection.py $* --var jesUp
python $WORK_DIR/eventSelection.py $* --var jerDown
python $WORK_DIR/eventSelection.py $* --var jerUp
python $WORK_DIR/eventSelection.py $* --var jmsDown
python $WORK_DIR/eventSelection.py $* --var jmsUp
python $WORK_DIR/eventSelection.py $* --var jmrDown
python $WORK_DIR/eventSelection.py $* --var jmrUp
'''

selection_template_data='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/
cd JOB_DIR

echo eventSelection.py $*
python $WORK_DIR/eventSelection.py $* --var nom
'''


semileptonic_condor = """universe              = vanilla
executable            = EXEC
output                = OUTPUT/output_$(Process).out
error                 = OUTPUT/output_$(Process).err
log                   = OUTPUT/output_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
use_x509userproxy = true
Queue args from ARGFILE
queue
"""


semileptonic_template='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/
cd JOB_DIR

echo semiLeptonicSelection.py $*
python $WORK_DIR/semiLeptonicSelection.py $* --var nom
python $WORK_DIR/semiLeptonicSelection.py $* --var jesDown
python $WORK_DIR/semiLeptonicSelection.py $* --var jesUp
python $WORK_DIR/semiLeptonicSelection.py $* --var jerDown
python $WORK_DIR/semiLeptonicSelection.py $* --var jerUp
python $WORK_DIR/semiLeptonicSelection.py $* --var sfDown
python $WORK_DIR/semiLeptonicSelection.py $* --var sfUp

'''

semileptonic_template_data='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/
cd JOB_DIR

echo semiLeptonicSelection.py $*
python $WORK_DIR/semiLeptonicSelection.py $* --var nom
'''

templates_condor = """universe              = vanilla
executable            = EXEC
output                = OUTPUT/output_$(Process).out
error                 = OUTPUT/output_$(Process).err
log                   = OUTPUT/output_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
use_x509userproxy = true
Queue args from ARGFILE
queue
"""

templates_template='''#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b//
cd $WORK_DIR

echo templateMaker.py $*
python templateMaker.py $* -v nom -m RECREATE
python templateMaker.py $* -v jesDown -m UPDATE
python templateMaker.py $* -v jesUp -m UPDATE
python templateMaker.py $* -v jerDown -m UPDATE
python templateMaker.py $* -v jerUp -m UPDATE
python templateMaker.py $* -v jmsDown -m UPDATE
python templateMaker.py $* -v jmsUp -m UPDATE
python templateMaker.py $* -v jmrDown -m UPDATE
python templateMaker.py $* -v jmrUp -m UPDATE
python templateMaker.py $* -v trigUp -m UPDATE
python templateMaker.py $* -v trigDown -m UPDATE
python templateMaker.py $* -v pnetUp -m UPDATE
python templateMaker.py $* -v pnetDown -m UPDATE
'''
