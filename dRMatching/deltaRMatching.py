import ROOT as r
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
# H 25
# Y 35
# X 45

def getHiggsIndex(event):
    foundFlag  = False
    higgsIndex = -1
    
    for i,ID in enumerate(event.GenPart_pdgId):
        if(ID==25):#H
            if event.GenPart_mass[i]!=125.0:
                print("WARNING: Higgs mass not 125?!")
            #if foundFlag:
            #    print("WARNING: Two Higgs in one event?")
            #print("Found Higgs at ID {0}".format(i))
            #print("Higgs mass is {0}".format(event.GenPart_mass[i]))
            foundFlag  = True
            higgsIndex = i
            return(higgsIndex)
    return(higgsIndex)


def getHigssPt(event):
    higgsIndex = getHiggsIndex(event)
    if(higgsIndex==-1):
        return -1
    higgsPt = event.GenPart_pt[higgsIndex]
    return higgsPt

def getHigssPhiEta(event):
    higgsIndex = getHiggsIndex(event)
    
    if(higgsIndex==-1):
        return 100,100
    
    higgsPhi = event.GenPart_phi[higgsIndex]
    higgsEta = event.GenPart_eta[higgsIndex]

    return higgsPhi,higgsEta

def getYIndex(event):
    foundFlag  = False
    YIndex = -1
    
    for i,ID in enumerate(event.GenPart_pdgId):
        if(ID==35):#Y
            foundFlag  = True
            YIndex = i
            return(YIndex)
    return(YIndex)

def getYPt(event):
    YIndex = getYIndex(event)
    if(YIndex==-1):
        return -1
    YPt = event.GenPart_pt[YIndex]
    return YPt

def getYPhiEta(event):
    YIndex = getYIndex(event)
    
    if(YIndex==-1):
        return 100,100
    
    YPhi = event.GenPart_phi[YIndex]
    YEta = event.GenPart_eta[YIndex]

    return YPhi,YEta


def getBFromHiggsIdxs(event):
    bIdxs = []
    for i,ID in enumerate(event.GenPart_pdgId):
        if not(ID==5 or ID==-5):
            continue
        motherIdx = event.GenPart_genPartIdxMother[i]
        if motherIdx == -1:
            continue
        motherPID = event.GenPart_pdgId[motherIdx]
        if motherPID==25:#Higgs
            bIdxs.append(i)
        if(len(bIdxs)==2):
            return bIdxs
    return bIdxs

def getBFromHiggsPhiEta(event):
    bIdxs = getBFromHiggsIdxs(event)
    if len(bIdxs)!=2:
        return [-1,-1]
    b1PhiEta = [event.GenPart_phi[bIdxs[0]],event.GenPart_eta[bIdxs[0]]]
    b2PhiEta = [event.GenPart_phi[bIdxs[1]],event.GenPart_eta[bIdxs[1]]]
    return b1PhiEta,b2PhiEta

def getBFromYIdxs(event):
    bIdxs = []
    for i,ID in enumerate(event.GenPart_pdgId):
        if not(ID==5 or ID==-5):
            continue
        motherIdx = event.GenPart_genPartIdxMother[i]
        if motherIdx == -1:
            continue
        motherPID = event.GenPart_pdgId[motherIdx]
        if motherPID==35:#Y
            bIdxs.append(i)
        if(len(bIdxs)==2):
            return bIdxs
    return bIdxs

def getBFromYPhiEta(event):
    bIdxs = getBFromYIdxs(event)
    if len(bIdxs)!=2:
        return [-1,-1]
    b1PhiEta = [event.GenPart_phi[bIdxs[0]],event.GenPart_eta[bIdxs[0]]]
    b2PhiEta = [event.GenPart_phi[bIdxs[1]],event.GenPart_eta[bIdxs[1]]]
    return b1PhiEta,b2PhiEta

def deltaR(phieta1,phieta2):
    try:
        DRsquare = np.square(phieta1[0]-phieta2[0])+np.square(phieta1[1]-phieta2[1])
        DR       = np.sqrt(DRsquare)
        return DR
    except:
        print("Couldn't  calculate DR")
        return 99999.

def plotHistogram(data,outfile,title,xlabel,ylabel="N"):
    plt.hist(data,100)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid(True)
    plt.savefig(outfile)
    plt.clf()


def plotHistogram(data,outfile,title,xlabel,xlow,xup):
    plt.hist(data,100,(xlow,xup))
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid(True)
    plt.savefig(outfile)
    plt.clf()

def calcEfficiency(hPass,hFail,name):
#Returns TEfficiency with *properly* calculated stat. uncertainties
    hPass.Sumw2()
    hFail.Sumw2()

    hTot    = hPass.Clone("tot")
    hTot.Add(hPass,hFail)
    eff     = r.TEfficiency(hPass,hTot)
    eff.SetName(name)
    return eff



def plotRootHistogram(h1,h2,h3,h4,outfile):
    #outfile should be name.png"
    c = r.TCanvas("c","c",900,700)
    r.gStyle.SetOptStat(111111)
    c.Divide(2,2)
    c.cd(1)
    h1.Draw()
    c.cd(2)
    h2.Draw()
    c.cd(3)
    h3.Draw()
    c.cd(4)
    h4.Draw()
    c.Modified()
    c.Update()
    sleep(1)
    c.SaveAs(outfile)

def getYGenMassPoint(event):
    if(event.GenModel_YMass_90==1):
        return 90
    elif(event.GenModel_YMass_100==1):
        return 100
    elif(event.GenModel_YMass_125==1):
        return 125
    elif(event.GenModel_YMass_150==1):
        return 150
    elif(event.GenModel_YMass_200==1):
        return 200
    elif(event.GenModel_YMass_250==1):
        return 250
    elif(event.GenModel_YMass_300==1):
        return 300
    elif(event.GenModel_YMass_400==1):
        return 400
    elif(event.GenModel_YMass_500==1):
        return 500
    elif(event.GenModel_YMass_600==1):
        return 600
    elif(event.GenModel_YMass_700==1):
        return 700
    elif(event.GenModel_YMass_800==1):
        return 800
    elif(event.GenModel_YMass_900==1):
        return 900
    elif(event.GenModel_YMass_1000==1):
        return 1000
    elif(event.GenModel_YMass_1200==1):
        return 1200
    elif(event.GenModel_YMass_1400==1):
        return 1400
    elif(event.GenModel_YMass_1600==1):
        return 1600
    elif(event.GenModel_YMass_1800==1):
        return 1800
    else:
        print("Unknown Y gen mass")
        return 0

def doHiggsMatching(event):
    #Returns idx of the first ak8 matched to H, -1 otherwise
    higgsPhiEta         = getHigssPhiEta(event)
    b1PhiEta,b2PhiEta   = getBFromHiggsPhiEta(event)
    for fatJetIdx in range(event.nFatJet):
        fatJetPhiEta = event.FatJet_phi[fatJetIdx],event.FatJet_eta[fatJetIdx]
        
        h_JetDR  = deltaR(fatJetPhiEta,higgsPhiEta)
        b1_JetDR = deltaR(fatJetPhiEta,b1PhiEta)
        b2_JetDR = deltaR(fatJetPhiEta,b2PhiEta)

        if (h_JetDR<0.8 and b1_JetDR<0.8 and b2_JetDR<0.8):
            return fatJetIdx

    return -1

def doYMatching(event):
    #Returns idx of the first ak8 matched to Y, -1 otherwise
    YPhiEta             = getYPhiEta(event)
    b3PhiEta,b4PhiEta   = getBFromYPhiEta(event)
    for fatJetIdx in range(event.nFatJet):
        fatJetPhiEta = event.FatJet_phi[fatJetIdx],event.FatJet_eta[fatJetIdx]
        
        Y_JetDR  = deltaR(fatJetPhiEta,YPhiEta)
        b3_JetDR = deltaR(fatJetPhiEta,b3PhiEta)
        b4_JetDR = deltaR(fatJetPhiEta,b4PhiEta)  

        if (Y_JetDR<0.8 and b3_JetDR<0.8 and b4_JetDR<0.8):
            return fatJetIdx
    return -1

def writehistlist(dictList, outfile):
#dictList is a list of dictionaries with key being mass point and value being corresponding histogram
    f = r.TFile(outfile,"RECREATE")
    for collection in dictList:
        for massPoint in collection:
            temp = collection[massPoint]
            try:
                temp.SetXTitle("Matched boson Gen Pt [GeV]")
            except:
                pass
            temp.Write()
    f.ls()


def processAllYMassPoints(infile):
    tfile = r.TFile.Open(infile)

    print("Number of entries: {0}".format(tfile.Events.GetEntriesFast()))

    failedH_histograms  = {}
    failedY_histograms  = {}
    matchedH_histograms = {}
    matchedY_histograms = {}
    HefficienciesHistos = {}
    YefficienciesHistos = {}
    Hak8MassHistos      = {}
    Yak8MassHistos      = {}

    massPoints = ["90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
    for massPoint in massPoints:
        failedH_histograms[massPoint]  = r.TH1F("failedMatchH_{0}".format(massPoint),"Higgs with failed DR matching",100,0.,2000.)
        failedY_histograms[massPoint]  = r.TH1F("failedMatchY_{0}".format(massPoint),"Y with failed DR matching"    ,100,0.,2000.)
        matchedH_histograms[massPoint] = r.TH1F("matchedH_{0}".format(massPoint)    ,"Higgs with DR matched AK8"    ,100,0.,2000.)
        matchedY_histograms[massPoint] = r.TH1F("matchedY_{0}".format(massPoint)    ,"Y with matched AK8"           ,100,0.,2000.)
        HefficienciesHistos[massPoint] = r.TEfficiency()
        YefficienciesHistos[massPoint] = r.TEfficiency()
        Hak8MassHistos[massPoint]      = r.TH1F("Hak8mass_{0}".format(massPoint)    ,"H-AK8 mass distribution"      ,100,0.,1000.)
        Yak8MassHistos[massPoint]      = r.TH1F("Yak8mass_{0}".format(massPoint) ,"Y-AK8 mass distribution"         ,100,0.,1000.)


    for i,event in enumerate(tfile.Events):

        # if(i>10000):
        #     break

        if(i%100000==0):
            print("Processing event {0}\n".format(i))

        massPoint = getYGenMassPoint(event)


        higgsPt     = getHigssPt(event)
        YPt         = getYPt(event)
        matchedHidx = doHiggsMatching(event)
        matchedYidx = doYMatching(event)
        print(matchedHidx)
        print(matchedYidx)
        print("-")
        if(matchedHidx==-1):
            failedH_histograms[str(massPoint)].Fill(higgsPt)
        else:
            matchedH_histograms[str(massPoint)].Fill(higgsPt)
            Hak8MassHistos[str(massPoint)].Fill(event.FatJet_msoftdrop[matchedHidx])
        if(matchedYidx==-1):
            failedY_histograms[str(massPoint)].Fill(YPt)
        else:
            matchedY_histograms[str(massPoint)].Fill(YPt)  
            Yak8MassHistos[str(massPoint)].Fill(event.FatJet_msoftdrop[matchedYidx])      

    for massPoint in massPoints:
        effNameH = "effMatchH_{0}".format(massPoint)
        effNameY = "effMatchY_{0}".format(massPoint)
        HefficienciesHistos[massPoint] = calcEfficiency(matchedH_histograms[massPoint],failedH_histograms[massPoint],effNameH)
        YefficienciesHistos[massPoint] = calcEfficiency(matchedY_histograms[massPoint],failedY_histograms[massPoint],effNameY)
        #HefficienciesHistos[massPoint].Divide(matchedH_histograms[massPoint],failedH_histograms[massPoint]+matchedH_histograms[massPoint])
        #YefficienciesHistos[massPoint].Divide(matchedY_histograms[massPoint],failedY_histograms[massPoint]+matchedY_histograms[massPoint])

    writehistlist([failedH_histograms,failedY_histograms,matchedH_histograms,matchedY_histograms,HefficienciesHistos,YefficienciesHistos,Hak8MassHistos,Yak8MassHistos],"test_eff.root")


if __name__ == '__main__':
    massPoints = ["90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
    processAllYMassPoints("E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root")
