import os
import sys, subprocess
from ROOT import *
import time, decimal


cards        = ["CR_L_16_full.txt","CR_T_16_full.txt","CR_L_17_full.txt","CR_T_17_full.txt","CR_L_18_full.txt","CR_T_18_full.txt"]
fitresults   = ["fitDiagnostics_L_16.root","fitDiagnostics_T_16.root","fitDiagnostics_L_17.root","fitDiagnostics_T_17.root","fitDiagnostics_L_18.root","fitDiagnostics_T_18.root"]
tags         = ["L_16","T_16","L_17","T_17","L_18","T_18"]

regions = ["L","T"]
years   = ["16","17","18"]

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
        prefitBqq   = f.Get("shapes_prefit/{0}_CR/TTbar_bqq".format(region)).Integral()
        prefitBq    = f.Get("shapes_prefit/{0}_CR/TTbar_bq".format(region)).Integral()
        postfitNorm = f.Get("shapes_fit_b/{0}_CR/total_background".format(region)).Integral()
        postfitBqq   = f.Get("shapes_fit_b/{0}_CR/TTbar_bqq".format(region)).Integral()
        postfitBq    = f.Get("shapes_fit_b/{0}_CR/TTbar_bq".format(region)).Integral()
        #print("{0}_{1},\tbqq, {2:.3f} +/- {3:.3f}, bq, {4:.2f} +/-{5:.3f}, TT norm, {6:.2f}".format(region,year,bqqVal,bqqErr,bqVal,bqErr,postfitNorm/prefitNorm))
        print(jms_bqq,jms_bqqErr)
        # print("  {0}_{1}".format(region,year))
        # print("  bqq: {0:.3f} +/- {1:.3f} Prefit: {2:.1f}, Postfit: {3:.1f}".format(bqqVal,bqqErr,prefitBqq,postfitBqq))
        # print("  bq: {0:.3f} +/- {1:.3f} Prefit: {2:.1f}, Postfit: {3:.1f}".format(bqVal,bqErr,prefitBq,postfitBq))
        print("  {0}_{1}".format(region,year))
        print("  bqq {0:.3f} {1:.3f}".format(bqqVal,bqqErr))
        print("  bq: {0:.3f} {1:.3f}".format(bqVal,bqErr))