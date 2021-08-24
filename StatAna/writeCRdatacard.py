# regions = ["T","L"]
# years   = ["16"]
header ='''imax * number of channels
jmax * number of processes minus 1
kmax * number of nuisance parameters
------------------------------------------------------------
bin REGION_CR
observation -1.0
------------------------------------------------------------'''

shapes ='''
shapes *\t REGION_CR\t PATH/$PROCESSYEAR.root\t $PROCESS_mSD_REGION_nom $PROCESS_mSD_REGION_$SYSTEMATIC
shapes TTbar_bqq REGION_CR\t PATH/TTbarYEAR.root\t $PROCESS_mSD_REGION_nom $PROCESS_mSD_REGION_$SYSTEMATIC
shapes TTbar_bq REGION_CR\t PATH/TTbarYEAR.root\t $PROCESS_mSD_REGION_nom $PROCESS_mSD_REGION_$SYSTEMATIC
shapes data_obs\t REGION_CR\t PATH/SingleMuonYEAR.root\t data_obs_mSD_REGION
------------------------------------------------------------'''

# procs = ["TTbar","ST","WJets"]
# jetCats = ["bqq","bq","qq","unmatched"]
procs = ["TTbar","Other"]
jetCats = ["bqq","bq"]
processes = {}
rateParams=""
i = 1
for p in procs:
    if not "TTbar" in p:
        processes[p]=i
        i+=1
    else:
        for cat in jetCats:
            proc = p+"_"+cat
            processes[proc]=i
            i+=1
            rateParams+="{0}REGION_YEAR rateParam REGION_CR {1} 1.0 [0.0,5.0]\n".format(cat,proc)
sortedProcs = sorted(processes.items(), key=lambda x: x[1])

binLine = "bin\t\t"
processNames = "process\t\t"
processCodes = "process\t\t"
rates = "rate\t\t"
for process in sortedProcs:
    print(process)
    binLine +="REGION_CR\t"
    processNames += "{0}\t".format(process[0])
    processCodes +="{0}\t".format(process[1])
    rates+="-1\t"




uniShapeUncs = ["jer","jes","jms","jmr","id","iso","trig","sf","puRwt"]
uncLines = ""
for unc in uniShapeUncs:
    uncLine = "{0}\tshape\t".format(unc)
    for process in sortedProcs:
        uncLine+="1.0\t"
    uncLines+=uncLine+"\n"
uncLines  += "ptRwt\tshape\t1.0\t1.0\t-\n"

lumiline     = "lumi\tlnN\t"
pdfline      = "pdfrewt\tlnN\t"
prefline     = "prefiring\tlnN\t"
for p in sortedProcs:
    lumiline+="1.025\t"
    pdfline +="1.01\t"
    prefline+="1.02\t"
normLines = "\n".join([lumiline,pdfline])
topxsecline  = "topxsec\tlnN\t0.938/1.061\t0.938/1.061\t-"
#topxsecline  = "topxsec\tlnN\t1.30\t1.30\t-"
# rateParams  += "#tqqRateL rateParam * TTbar (0.42*@0+0.58*@1) bqq_rateL,bq_rateL\n"
# rateParams  += "#tqqRateT rateParam * TTbar (0.46*@0+0.54*@1) bqq_rateT,bq_rateT"

renamers = """
nuisance edit rename TTbar_bqq REGION_CR jms jmsAK8_bqqYEAR
nuisance edit rename TTbar_bq REGION_CR jms jmsAK8_bqYEAR
nuisance edit rename Other REGION_CR jms jmsAK8_OtherYEAR
nuisance edit rename * REGION_CR jmr jmrAK8YEAR
nuisance edit rename * REGION_CR id muonIDYEAR
nuisance edit rename * REGION_CR iso muonIsoYEAR
nuisance edit rename * REGION_CR trig muonTrigYEAR
nuisance edit rename * REGION_CR sf btagSFAK4_YEAR
nuisance edit rename * REGION_CR jes jesYEAR
nuisance edit rename * REGION_CR jer jerYEAR
nuisance edit rename * REGION_CR lumi lumiYEAR
nuisance edit rename * REGION_CR ptRwt topPtRwt
"""


autoMCstats = "* autoMCStats 10000 1 1"

#card = "\n".join([header,shapes,binLine,processNames,processCodes,rates,normLines,uncLines,topxsecline,rateParams,renamers,autoMCstats])
card = "\n".join([header,shapes,binLine,processNames,processCodes,rates,normLines,uncLines,rateParams,renamers,autoMCstats])




regions = ["T","L"]
#years   = ["16","17","18","RunII"]
years   = ["16","17","18"]
for region in regions:
    for year in years:
        outputName = "CR_{0}_{1}.txt".format(region,year)
        outCard     = card.replace("REGION",region)
        if(year=="RunII"):
            outCard     = outCard.replace("PATH","/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_semileptonic/FullRunII")
        else:
            outCard     = outCard.replace("PATH","/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_semileptonic/20YEAR/scaled")
        outCard     = outCard.replace("YEAR",year)
        fOut = open(outputName,"w")
        fOut.write(outCard  )
        fOut.close()

