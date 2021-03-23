import os
import sys, subprocess
from ROOT import *
import time, decimal


algo         = "saturated"
cards        = ["CR_L_17.txt","CR_T_17.txt","CR_L_18.txt","CR_T_18.txt"]
fitresults   = ["fitDiagnostics_L_17.root","fitDiagnostics_T_17.root","fitDiagnostics_L_18.root","fitDiagnostics_T_18.root"]
tags         = ["L_17","T_17","L_18","T_18"]

regions = ["L","T"]
years   = ["17","18"]

for region in regions:
    for year in years:
        f = TFile.Open("fitDiagnostics_{0}_{1}.root".format(region,year))
        fr = f.Get('fit_b')
        results = {} 
        myargs = fr.floatParsFinal()
        for j in range(myargs.getSize()):
            var = myargs.at(j)
            results[var.GetName()]=[var.getValV(),var.getError()]
        bqqVal, bqqErr = results["bqq{0}_{1}".format(region,year)][0], results["bqq{0}_{1}".format(region,year)][1]
        bqVal,  bqErr  = results["bq{0}_{1}".format(region,year)][0], results["bq{0}_{1}".format(region,year)][1]

        #print(results.keys())
        jms_bqq, jms_bqqErr = results["jmsAK8_bqq"+year][0], results["jmsAK8_bqq"+year][1]
        jms_bq,  jms_bqErr  = results["jmsAK8_bq"+year][0],  results["jmsAK8_bq"+year][1]

        prefitNorm  = f.Get("shapes_prefit/{0}_CR/total_background".format(region)).Integral()
        postfitNorm = f.Get("shapes_fit_b/{0}_CR/total_background".format(region)).Integral()
        print("{0}_{1},\tbqq, {2:.3f}, {3:.3f}, bq, {4:.2f}, {5:.3f}, TT norm, {6:.2f}".format(region,year,bqqVal,bqqErr,bqVal,bqErr,postfitNorm/prefitNorm))
        print(jms_bqq,jms_bqqErr)
