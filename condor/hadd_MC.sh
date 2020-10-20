#!/bin/bash

#samples="QCD500 QCD700 QCD1000 QCD1500 QCD2000 ttbar"
#samples="X1600_Y100 X1600_Y150 X1600_Y200 X1600_Y300 X1600_Y400"
samples="X1600_Y100 X1600_Y150 X1600_Y200 X1600_Y300 X1600_Y400 QCD500 QCD700 QCD1000 QCD1500 QCD2000 ttbar ZJets400 ZJets600 ZJets800 WJets ST_antitop ST_top ST_tW_top ST_tW_antitop"
for val in $samples; do
    echo hadd $val/$val.root $val/output/output*root
    hadd $val/$val.root $val/output/output*root
    cp $val/$val.root /afs/cern.ch/user/m/mrogulji/X_YH_4b/results/histograms/nonScaled/$val.root
done
