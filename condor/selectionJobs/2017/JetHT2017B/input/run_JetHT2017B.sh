#!/bin/bash

cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/CMSSW_11_1_5/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/
source timber-env/bin/activate

export WORK_DIR=/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/
cd /afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/condor/selectionJobs/2017/JetHT2017B

echo eventSelection.py $*
python $WORK_DIR/eventSelection.py $* --var nom
