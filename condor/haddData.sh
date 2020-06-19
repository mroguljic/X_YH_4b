#!/bin/bash

dataRun="B C D E F G H"
for val in $dataRun; do
    #echo Data$val/Data$val.root Data$val/output/output*root
    hadd Data$val/Data$val.root Data$val/output/output*root
done
