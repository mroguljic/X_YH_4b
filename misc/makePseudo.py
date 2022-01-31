import re
import ROOT as r
import sys
import random
#For generating pseudo data
def mergeSamples(inFiles,outFile,regexMatch,regexReplace):
    scalings2016 = {"bqq":{"L":0.84,"T":0.76},"bq":{"L":0.91,"T":1.07}}
    scalings2017 = {"bqq":{"L":0.82,"T":0.87},"bq":{"L":1.32,"T":1.31}}
    scalings2018 = {"bqq":{"L":0.83,"T":0.90},"bq":{"L":1.12,"T":1.35}}
    scalings = {"2016":scalings2017,"2017":scalings2017,"2018":scalings2018}
    h_dict = {}
    print("Merging to {0}".format(outFile))
    if("16" in inFiles[0]):
        year = "2016"
    if("17" in inFiles[0]):
        year = "2017"
    if("18" in inFiles[0]):
        year = "2018"    
    for inFile in inFiles:
        print(inFile)
        f        = r.TFile.Open(inFile) 
        for key in f.GetListOfKeys():
            h = key.ReadObj()
            hName = h.GetName()
            if("mJY_mJJ_TT" in hName and "bqq_" in hName):
                scaling = scalings[year]["bqq"]["T"]
            if("mJY_mJJ_TT" in hName and "bq_" in hName):
                scaling = scalings[year]["bq"]["T"]
            elif("mJY_mJJ_LL" in hName and "bqq_" in hName):
                scaling = scalings[year]["bqq"]["L"]
            elif("mJY_mJJ_LL" in hName and "bq_" in hName):
                scaling = scalings[year]["bq"]["L"]
            else:
                scaling = 1.0
            if(scaling!=1.0):
                print(scaling, hName)
            h.Scale(scaling)
            h.SetDirectory(0)
            hKey = re.sub(regexMatch,regexReplace,hName,count=1)
            if not hKey in h_dict:
                h.SetName(hKey)
                h_dict[hKey] = h
            else:
                h_dict[hKey].Add(h)
        f.Close()
    f = r.TFile(outFile,"recreate")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()
    print("\n")

def generatePseudo():
    for year in ['2016','2017','2018']:
        print(year)
        lumiScaledDir = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/templates/WP_0.94_0.98/corrected_mSD/{0}/".format(year)
        pseudoSamples = ["{0}/QCD{1}.root".format(lumiScaledDir,year[-2:]),"{0}/TTbar{1}.root".format(lumiScaledDir,year[-2:])]
        mergeSamples(pseudoSamples,"{0}/pseudo{1}.root".format(lumiScaledDir,year[-2:]),"QCD|TTbar","data_obs")

#For generating data-like toys
def getYear(inFile):
    if("16") in inFile:
        year = "2016"
    elif("17") in inFile:
        year = "2017"
    elif("18") in inFile:
        year = "2018"
    else:
        print("Year not recognized for {0}".format(inFile))
        sys.exit()
    return year


def constructTT(inFiles,region):
    scalings2016 = {"bqq":{"L":0.82,"T":0.78},"bq":{"L":1.00,"T":1.17}}
    scalings2017 = {"bqq":{"L":0.79,"T":0.85},"bq":{"L":1.32,"T":1.25}}
    scalings2018 = {"bqq":{"L":0.85,"T":0.87},"bq":{"L":1.12,"T":1.20}}
    scalings = {"2016":scalings2017,"2017":scalings2017,"2018":scalings2018}

    h2_TTbar = None
    for inFile in inFiles:
        #print(inFile)
        year        = getYear(inFile)        
        f           = r.TFile.Open(inFile) 
        
        h2_bqq_temp = f.Get("TTbar_bqq_mJY_mJJ_{0}_nom".format(region))
        h2_bq_temp  = f.Get("TTbar_bq_mJY_mJJ_{0}_nom".format(region))
        h2_qq_temp  = f.Get("TTbar_qq_mJY_mJJ_{0}_nom".format(region))
        h2_unm_temp = f.Get("TTbar_unm_mJY_mJJ_{0}_nom".format(region))

        h2_bqq_temp.Scale(scalings[year]["bqq"][region[0]])
        h2_bq_temp.Scale(scalings[year]["bq"][region[0]])

        if not h2_TTbar:
            h2_TTbar  = h2_bqq_temp.Clone("h2_TTbbar_{0}".format(region))
            h2_TTbar.Reset()
            h2_TTbar.SetDirectory(0)

        h2_TTbar.Add(h2_bqq_temp)
        h2_TTbar.Add(h2_bq_temp)
        h2_TTbar.Add(h2_qq_temp)
        h2_TTbar.Add(h2_unm_temp)
        f.Close()
    return h2_TTbar


def applyRratio(rpf,rratioFile):
    finalRpf = rpf.Clone(rpf.GetName()+"_final")
    f = r.TFile.Open(rratioFile)
    rratio = f.Get("rpf_final")
    for i in range(1,rpf.GetNbinsX()+1):
        for j in range(1,rpf.GetNbinsX()+1):
            rpfVal = rpf.GetBinContent(i,j)
            xVal   = rpf.GetXaxis().GetBinCenter(i)
            yVal   = rpf.GetYaxis().GetBinCenter(i)
            iRRatio = rratio.GetXaxis().FindBin(xVal)
            jRRatio = rratio.GetYaxis().FindBin(yVal)
            rratioVal = rratio.GetBinContent(iRRatio,jRRatio)
            if(rratioVal==0):
                rratioVal = 1.0
            finalRpf.SetBinContent(i,j,rpfVal*rratioVal)
    finalRpf.SetDirectory(0)
    return finalRpf


def constructQCD(datatMinusTTFile,rpfFile,region):
    #inFiles are data-TT files
    h2_QCD = None
    if(region=="TT"):
        rpfName     = "rpf_WAL_AL_WAL_T"
        rratioFile  = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/RunII_NAL_11_CR/NAL_T/plots/postfit_rpf_fitb.root"
        failRegion  = "T_AL"
    else:
        rpfName     = "rpf_WAL_AL_WAL_L" 
        rratioFile  = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/RunII_NAL_11_CR/NAL_L/plots/postfit_rpf_fitb.root"
        failRegion  = "L_AL"  

    print("Constructing QCD PDF for region {0}:".format(region))
    print("Rpf file {0}".format(rpfFile))
    print("RRatio file {0}".format(rratioFile))      
  
    rpfFile         = r.TFile.Open(rpfFile) 
    rpf             = rpfFile.Get(rpfName)
    rpf             = applyRratio(rpf,rratioFile)

    datatMinusTTFile  = r.TFile.Open(datatMinusTTFile)
    qcdFail         = datatMinusTTFile.Get("QCD_mJY_mJJ_{0}_nom".format(failRegion))
    qcdPass         = qcdFail.Clone("QCD_{0}".format(region))
    qcdPass.Multiply(rpf)
    qcdPass.SetDirectory(0)
    rpfFile.Close()
    datatMinusTTFile.Close()
    return qcdPass

def getCumulativePDF(h2_pdf,h2_name):
    nx      = h2_pdf.GetNbinsX()
    ny      = h2_pdf.GetNbinsY()
    hPDF    = r.TH1F(h2_name,"",nx*ny,0,nx*ny)
    cumulativeBin = 0
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            cumulativeBin+=1
            pdf = h2_pdf.GetBinContent(i,j)+hPDF.GetBinContent(cumulativeBin-1)
            hPDF.SetBinContent(cumulativeBin,pdf)
    return hPDF


def generatePDF(region):
    #Generates a PDF from TTbar simulation and QCD from Rpf
    #returns a 2D PDF, its cumulative pdf and the number of events from the estimate
    TTsamples = []
    if(region=="TT"):
        rpfRegion   = "WAL_T"
    else:
        rpfRegion   = "WAL_L"
    tplDir          = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/templates/WP_0.94_0.98/"
    for year in ['2016','2017','2018']:
        #print(year)
        lumiScaledDir = tplDir+"{0}/".format(year)
        TTsamples.append(lumiScaledDir+"TTbar{0}.root".format(year[2:]))
    #print(TTsamples)
    h2_TT       = constructTT(TTsamples,region)
    h2_QCD      = constructQCD(tplDir+"RunII/dataMinusTTbar.root",tplDir+"RunII/DataMinusTT1DRpf_{0}.root".format(rpfRegion),region)
    h2_pdf      = h2_TT.Clone("pdf_{0}".format(region))
    h2_pdf.Add(h2_QCD)
    nRegion     = h2_pdf.Integral(1,h2_pdf.GetNbinsX()+1,1,h2_pdf.GetNbinsY()+1)
    h2_pdf.Scale(1/nRegion)
    h2_pdf.SetDirectory(0)
    cumulativePDF = getCumulativePDF(h2_pdf,"cumulative_pdf_{0}".format(region))



    return h2_pdf, cumulativePDF, int(nRegion)

def findPDFintersection(rand,cumulativePDF):
    for i in range(1,cumulativePDF.GetNbinsX()+1):
        pdfVal = cumulativePDF.GetBinContent(i)
        if(pdfVal>rand):
            return i
    print("Intersection with PDF not found, something is wrong")
    return -1


def globalBinTo2D(h2_pdf,globalBin):
    #globalBins start from 1
    #globalBin 1 = (1,1), 2 = (1,2) and so on
    globalBin = globalBin - 1
    NX      = h2_pdf.GetNbinsX()
    NY      = h2_pdf.GetNbinsY()

    nx      = int(globalBin)/int(NY)+1
    ny      = globalBin%NY+1

    return nx,ny


def generateToy(h2_pdf, cumulativePDF, nEvents, h2_name):
    h2_toy = h2_pdf.Clone(h2_name)
    h2_toy.Reset()
    h2_toy.SetDirectory(0)
    for i in range(nEvents):
        rand      = random.uniform(0,1)
        globalBin = findPDFintersection(rand,cumulativePDF)
        nx, ny    = globalBinTo2D(h2_pdf,globalBin)
        nx        = int(nx)
        ny        = int(ny)
        #print(rand,globalBin)
        h2_toy.SetBinContent(nx,ny,h2_toy.GetBinContent(nx,ny)+1)
    return h2_toy


def getFailTemplate(rFile,region):
    f = r.TFile.Open(rFile)
    if(region=="TT"):
        h = f.Get("data_obs_mJY_mJJ_T_AL_nom")
    else:
        h = f.Get("data_obs_mJY_mJJ_L_AL_nom")
    h.SetDirectory(0)
    f.Close()
    return h

h2_pdf_TT, cumulativePDF_TT, nTT = generatePDF("TT")
h2_TT_toy = generateToy(h2_pdf_TT, cumulativePDF_TT, int(nTT), "data_obs_mJY_mJJ_TT_nom")
h2_TT_fail= getFailTemplate("/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/templates/WP_0.94_0.98/RunII/JetHT.root","TT")
h2_pdf_LL, cumulativePDF_LL, nLL = generatePDF("LL")
h2_LL_fail= getFailTemplate("/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/CMSSW_10_6_14/src/2DAlphabet/templates/WP_0.94_0.98/RunII/JetHT.root","LL")
h2_LL_toy = generateToy(h2_pdf_LL, cumulativePDF_LL, int(nLL), "data_obs_mJY_mJJ_LL_nom")

f = r.TFile.Open("test.root","RECREATE")
f.cd()
h2_pdf_TT.Write()
cumulativePDF_TT.Write()
h2_TT_toy.Write()
h2_TT_fail.Write()

h2_pdf_LL.Write()
cumulativePDF_LL.Write()
h2_LL_toy.Write()
h2_LL_fail.Write()

f.Close()
#print(h2_pdf.Integral(1,10))