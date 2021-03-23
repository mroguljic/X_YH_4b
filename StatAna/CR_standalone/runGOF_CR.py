import os
import sys, subprocess
from ROOT import *
import time, decimal

gStyle.SetOptStat(0)
gStyle.SetOptFit(1)
gStyle.SetOptTitle(0)
gROOT.SetBatch()


def importPars(incard,fitresults,toDrop,verbosity=0):
    # First convert the card
    r = 0
    subprocess.call(['text2workspace.py -b '+incard+' -o morphedWorkspace.root'],shell=True)

    # Open new workspace
    w_f = TFile.Open('morphedWorkspace.root', 'UPDATE')
    w = w_f.Get('w')

    for fr_name in fitresults:
        print ('Importing '+fr_name+' ...')
        # Open fit result we want to import
        fr_f = TFile.Open(fr_name)
        fr = fr_f.Get('fit_b') # b-only fit result (fit_s for s+b)
        myargs = fr.floatParsFinal()

        for i in range(myargs.getSize()):
            var = myargs.at(i)
            if(var.GetName()=="r"):
                r = var.getValV()
            if var.GetName() in toDrop: continue

            if not w.allVars().contains(var):
                print ('WARNING: Could not find %s'%var.GetName())
            else:
                var_to_change = w.var(var.GetName())
                if(verbosity):
                    print (var.GetName())
                    print ('\tBefore:    %.2f +/- %.2f (%.2f,%.2f)'%(var_to_change.getValV(),var_to_change.getError(),var_to_change.getMin(),var_to_change.getMax()))
                var_to_change.setMin(var.getMin())
                var_to_change.setMax(var.getMax())
                var_to_change.setVal(var.getValV())
                var_to_change.setError(var.getError())
                if(verbosity):
                    print ('\tChange to: %.2f +/- %.2f (%.2f,%.2f)'%(var.getValV(),var.getError(),var.getMin(),var.getMax()))
                    print ('\tAfter:     %.2f +/- %.2f (%.2f,%.2f)'%(var_to_change.getValV(),var_to_change.getError(),var_to_change.getMin(),var_to_change.getMax()))
    
    w.saveSnapshot("initialFit",RooArgSet(myargs),True)
    w_f.WriteTObject(w,'w',"Overwrite")
    w_f.Close()
    return r




ntoys        = 500
seed         = 10
algo         = "saturated"
cards        = ["CR_L_16.txt","CR_T_16.txt","CR_L_17.txt","CR_T_17.txt","CR_L_18.txt","CR_T_18.txt","CR_L_RunII.txt","CR_T_RunII.txt"]
fitresults   = ["fitDiagnostics_L_16.root","fitDiagnostics_T_16.root","fitDiagnostics_L_17.root","fitDiagnostics_T_17.root","fitDiagnostics_L_18.root","fitDiagnostics_T_18.root","fitDiagnostics_L_RunII.root","fitDiagnostics_T_RunII.root"]

cards        = ["CR_L_17.txt","CR_T_17.txt","CR_L_18.txt","CR_T_18.txt"]
fitresults   = ["fitDiagnostics_L_17.root","fitDiagnostics_T_17.root","fitDiagnostics_L_18.root","fitDiagnostics_T_18.root"]


for i,card in enumerate(cards):
    gofDir   = card.replace(".txt","")
    mkdirCmd = "mkdir {0}".format(gofDir)
    print(mkdirCmd)
    os.system(mkdirCmd)
    os.chdir(gofDir)
    print("CWD: "+os.getcwd())
    print("../{0}".format(card),"../{0}".format(fitresults[i]))
    r = importPars("../{0}".format(card),["../{0}".format(fitresults[i])],[],verbosity=0)

    gen_command  = 'combine -M GenerateOnly -d morphedWorkspace.root --snapshotName initialFit --toysFrequentist --bypassFrequentistFit -t '+str(ntoys)+' --saveToys -s '+str(seed)+' -n gof'
    gof_data_cmd = 'combine -M GoodnessOfFit morphedWorkspace.root --algo='+algo+' -n gof_data_'+algo
    gof_toy_cmd  = 'combine -M GoodnessOfFit morphedWorkspace.root --algo='+algo+' --toysFrequentist --toysFile higgsCombinegof.GenerateOnly.mH120.'+str(seed)+'.root --saveWorkspace -t '+str(ntoys)+' -s '+str(seed) +' -n gof_'+algo

    print(gen_command)
    subprocess.call(gen_command,shell=True)
    print(gof_data_cmd)
    subprocess.call(gof_data_cmd,shell=True)
    print(gof_toy_cmd)
    subprocess.call(gof_toy_cmd,shell=True)
    
    #Plotting
    toyOutput = TFile.Open("higgsCombinegof_{0}.GoodnessOfFit.mH120.{1}.root".format(algo,seed))
    toyLimitTree = toyOutput.Get('limit')
    gofOutput = TFile.Open("higgsCombinegof_data_{0}.GoodnessOfFit.mH120.root".format(algo))#data gof
    gofLimitTree = gofOutput.Get('limit')
    gofLimitTree.GetEntry(0)
    gofLimit = gofLimitTree.limit

    toyLimitTree.Draw('limit>>hlimit','limit>1.0 && limit<%s && limit != %s'%(gofLimit*5.0,gofLimit)) 
    toyLimits = gDirectory.Get('hlimit')
    time.sleep(1) # if you don't sleep the code moves too fast and won't perform the fit
    toyLimits.Fit("gaus")

    # Fit toys and derive p-value
    gaus = toyLimits.GetFunction("gaus")
    pvalue = 1-(1/gaus.Integral(-float("inf"),float("inf")))*gaus.Integral(-float("inf"),gofLimit)

    # Write out for reference
    out = open('gof_results.txt','w')
    out.write('Test statistic in data = '+str(gofLimit))
    out.write('Mean from toys = '+str(gaus.GetParameter(1)))
    out.write('Width from toys = '+str(gaus.GetParameter(2)))
    out.write('p-value = '+str(pvalue))

    # Extend the axis if needed
    if toyLimits.GetXaxis().GetXmax() < gofLimit:
        print 'Axis limit greater than GOF t value'
        binwidth = toyLimits.GetXaxis().GetBinWidth(1)
        xmin = toyLimits.GetXaxis().GetXmin()
        new_xmax = int(gofLimit*1.1)
        new_nbins = int((new_xmax-xmin)/binwidth)
        toyLimitTree.Draw('limit>>hlimitrebin('+str(new_nbins)+', '+str(xmin)+', '+str(new_xmax)+')','limit>0.001 && limit<1500') 
        toyLimits = gDirectory.Get('hlimitrebin')
        toyLimits.Fit("gaus")
        gaus = toyLimits.GetFunction("gaus")

    # Arrow for observed
    arrow = TArrow(gofLimit,0.25*toyLimits.GetMaximum(),gofLimit,0)
    arrow.SetLineWidth(2)

    # Legend
    leg = TLegend(0.1,0.7,0.4,0.9)
    leg.SetLineColor(kWhite)
    leg.SetLineWidth(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.AddEntry(toyLimits,"toy data","lep")
    leg.AddEntry(arrow,"observed = %.1f"%gofLimit,"l")
    leg.AddEntry(0,"p-value = %.2E"%decimal.Decimal(pvalue),"")

    # Draw
    cout = TCanvas('cout','cout',800,700)
    toyLimits.Draw('pez')
    arrow.Draw()
    leg.Draw()

    cout.Print('gof_plot_{0}.pdf'.format(algo),'pdf')
    cout.Print('gof_plot_{0}.png'.format(algo),'png')
    cout.SaveAs('gof_plot_{0}.root'.format(algo),'root')
    os.system("cp gof_plot_{0}.png ../postfitPlots/gof_plot_{0}_{1}.png".format(algo,gofDir.replace("CR_","")))

    os.chdir("..")

