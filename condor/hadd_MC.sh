#!/bin/bash

samples="X1600 QCD500 QCD700 QCD1000 QCD1500 QCD2000 ttbar"

for val in $samples; do
    echo hadd $val/$val.root $val/output/output*root
    hadd $val/$val.root $val/output/output*root
done