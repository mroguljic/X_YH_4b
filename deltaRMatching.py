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
            temp.SetXTitle("Matched boson Gen Pt [GeV]")
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
        HefficienciesHistos[massPoint] = r.TH1F("Heffiencies_{0}".format(massPoint) ,"H matching efficencies"       ,100,0.,2000.)
        YefficienciesHistos[massPoint] = r.TH1F("Yeffiencies_{0}".format(massPoint) ,"Y matching efficencies"       ,100,0.,2000.)
        Hak8MassHistos[massPoint]      = r.TH1F("Hak8mass_{0}".format(massPoint)    ,"H-AK8 mass distribution"      ,100,0.,1000.)
        Yak8MassHistos[massPoint]      = r.TH1F("Yak8mass_{0}".format(massPoint) ,"Y-AK8 mass distribution"         ,100,0.,1000.)


    for i,event in enumerate(tfile.Events):

        # if(i>1000):
        #     break

        if(i%100000==0):
            print("Processing event {0}\n".format(i))

        massPoint = getYGenMassPoint(event)


        higgsPt     = getHigssPt(event)
        YPt         = getYPt(event)
        matchedHidx = doHiggsMatching(event)
        matchedYidx = doYMatching(event)
        if(matchedHidx==-1):
            failedH_histograms[str(massPoint)].Fill(higgsPt)
        else:
            matchedH_histograms[str(massPoint)].Fill(higgsPt)
            Hak8MassHistos[str(massPoint)].Fill(event.FatJet_mass[matchedHidx])
        if(matchedYidx==-1):
            failedY_histograms[str(massPoint)].Fill(YPt)
        else:
            matchedY_histograms[str(massPoint)].Fill(YPt)  
            Yak8MassHistos[str(massPoint)].Fill(event.FatJet_mass[matchedYidx])      

    for massPoint in massPoints:
        HefficienciesHistos[massPoint].Divide(matchedH_histograms[massPoint],failedH_histograms[massPoint]+matchedH_histograms[massPoint])
        YefficienciesHistos[massPoint].Divide(matchedY_histograms[massPoint],failedY_histograms[massPoint]+matchedY_histograms[massPoint])

    writehistlist([failedH_histograms,failedY_histograms,matchedH_histograms,matchedY_histograms,HefficienciesHistos,YefficienciesHistos,Hak8MassHistos,Yak8MassHistos],"test.root")


def processSingleYMassPoint(infile,massPoint):
    tfile = r.TFile.Open(infile)

    print("Number of entries: {0}".format(tfile.Events.GetEntriesFast()))


    HfailedMatch_Hpt    = r.TH1F("failedMatchH","Higgs with failed DR matching",100,0.,2000.)
    YfailedMatch_Ypt    = r.TH1F("failedMatchY","Y with failed DR matching"    ,100,0.,2000.)
    HpassedMatch_Hpt    = r.TH1F("passedMatchH","Higgs with passed DR matching",100,0.,2000.)
    YpassedMatch_Ypt    = r.TH1F("passedMatchY","Y with passed DR matching"    ,100,0.,2000.)
    HptEff_Hpt          = r.TH1F("effMatchH"   ,"Higgs DR matching efficiency" ,100,0.,2000.)
    YptEff_Ypt          = r.TH1F("effMatchY"   ,"Y DR matching efficiency"     ,100,0.,2000.)

    HfailedMatch_Hpt.SetXTitle("Higgs Pt [GeV]")
    HpassedMatch_Hpt.SetXTitle("Higgs Pt [GeV]")
    YpassedMatch_Ypt.SetXTitle("Y Pt [GeV]")
    YfailedMatch_Ypt.SetXTitle("Y Pt [GeV]")

    for i,event in enumerate(tfile.Events):

        if(i%100000==0):
            print("Processing event {0}\n".format(i))

        # if(i>10000):
        #    break

        massPointVeto = getattr(event,"GenModel_YMass_{0}".format(massPoint))
        if(massPointVeto==0):
           continue
        higgsPt     = getHigssPt(event)
        YPt         = getYPt(event)
        matchedHidx = doHiggsMatching(event)
        matchedYidx = doYMatching(event)
        if(matchedHidx==-1):
            HfailedMatch_Hpt.Fill(higgsPt)
        else:
            HpassedMatch_Hpt.Fill(higgsPt)
        if(matchedYidx==-1):
            YfailedMatch_Ypt.Fill(YPt)
        else:
            YpassedMatch_Ypt.Fill(YPt)

    plotRootHistogram(HfailedMatch_Hpt,YfailedMatch_Ypt,HpassedMatch_Hpt,YpassedMatch_Ypt,"Pass_fail_{0}.png".format(massPoint))
    HptEff_Hpt.Divide(HpassedMatch_Hpt,HfailedMatch_Hpt+HpassedMatch_Hpt)
    YptEff_Ypt.Divide(YpassedMatch_Ypt,YfailedMatch_Ypt+YpassedMatch_Ypt)
    HptEff_Hpt.SetXTitle("Higgs Pt [GeV]")
    YptEff_Ypt.SetXTitle("Y Pt [GeV]")
    plotRootHistogram(HptEff_Hpt,HptEff_Hpt,YptEff_Ypt,YptEff_Ypt,"Efficienies_{0}.png".format(massPoint))


def analyzeFile(infile,outPrefix):
    tfile = r.TFile.Open(infile)

    print("Number of entries: {0}".format(tfile.Events.GetEntriesFast()))
    matchedHiggs        = 0
    matchedY            = 0
    matchedBoth         = 0
    matchedHiggsMasses  = []
    matchedHiggsPts     = []
    matchedYMasses      = []
    matchedYPts         = []
    histHiggsAK8Mass    = r.TH1F( "hMass", "H matched AK8 jet mass", 100, 0., 500. )
    histYAK8Mass        = r.TH1F( "YMass", "Y matched AK8 jet mass", 100, 0., 500. )
    histHiggsAK8Pt      = r.TH1F( "hPt"  , "H matched AK8 jet pt"  , 100, 0., 2000. )
    histYAK8Pt          = r.TH1F( "YPt"  , "Y matched AK8 jet pt"  , 100, 0., 2000. )

    for i,event in enumerate(tfile.Events):
        # if(i>100):
        #     break

        if(i%100000==0):
            print("Processing event {0}\n".format(i))

        higgsPhiEta         = getHigssPhiEta(event)
        YPhiEta             = getYPhiEta(event)
        b1PhiEta,b2PhiEta   = getBFromHiggsPhiEta(event)
        b3PhiEta,b4PhiEta   = getBFromYPhiEta(event)
        matchedHiggsJetIdxs = []
        matchedYJetIdxs     = []
        hDeltaRs            = []
        YDeltaRs            = []
        matchedHiggsFlag    = False
        matchedYFlag        = False

        for fatJetIdx in range(event.nFatJet):
            fatJetPhiEta = event.FatJet_phi[fatJetIdx],event.FatJet_eta[fatJetIdx]

            h_JetDR  = deltaR(fatJetPhiEta,higgsPhiEta)
            b1_JetDR = deltaR(fatJetPhiEta,b1PhiEta)
            b2_JetDR = deltaR(fatJetPhiEta,b2PhiEta)

            Y_JetDR  = deltaR(fatJetPhiEta,YPhiEta)
            b3_JetDR = deltaR(fatJetPhiEta,b3PhiEta)
            b4_JetDR = deltaR(fatJetPhiEta,b4PhiEta)        

            if (h_JetDR<0.8 and b1_JetDR<0.8 and b2_JetDR<0.8):
                matchedHiggsJetIdxs.append(fatJetIdx)
                hDeltaRs.append(h_JetDR)
                matchedHiggsFlag=True
                mass = event.FatJet_mass[fatJetIdx]
                pt   = event.FatJet_pt[fatJetIdx]
                histHiggsAK8Mass.Fill(mass)
                histHiggsAK8Pt.Fill(pt)
                matchedHiggsMasses.append(mass)
                matchedHiggsPts.append(pt)

            if (Y_JetDR<0.8 and b3_JetDR<0.8 and b4_JetDR<0.8):
                matchedYJetIdxs.append(fatJetIdx)
                YDeltaRs.append(Y_JetDR)
                mass        = event.FatJet_mass[fatJetIdx]
                pt          = event.FatJet_pt[fatJetIdx]
                histYAK8Mass.Fill(mass)
                histYAK8Pt.Fill(pt)
                matchedYFlag=True
                matchedYMasses.append(mass)
                matchedYPts.append(pt)


        if(len(matchedHiggsJetIdxs)>1):
            print("Matched more than one AK8 to Higgs")
            print("Higgs phi {0}, eta {1}".format(*higgsPhiEta))
            for j,idx in enumerate(matchedHiggsJetIdxs):
                print("Jet{0} - pt {1}, mass {2}, phi {3}, eta {4}".format(j,event.FatJet_mass[idx],event.FatJet_pt[idx],event.FatJet_phi[idx],event.FatJet_eta[idx],))
            print("DeltaRs (AK8-Higgs) {0},{1}".format(*hDeltaRs))
            print('\n')


        if(len(matchedYJetIdxs)>1):
            print("Matched more than one AK8 to Y")
            print("Y phi {0}, eta {1}".format(*YPhiEta))
            for j,idx in enumerate(matchedYJetIdxs):
                print("Jet{0} - pt {1}, mass {2}, phi {3}, eta {4}".format(j,event.FatJet_mass[idx],event.FatJet_pt[idx],event.FatJet_phi[idx],event.FatJet_eta[idx],))
            print("DeltaRs (AK8-Y) {0},{1}".format(*YDeltaRs))
            print('\n')

        if matchedHiggsFlag:
            matchedHiggs+=1

        if matchedYFlag:
            matchedY+=1

        if matchedYFlag and matchedHiggsFlag:
            matchedBoth+=1

    print(matchedHiggs)
    print(matchedY)
    print(matchedBoth)

    plotRootHistogram(histHiggsAK8Mass,histYAK8Mass,histHiggsAK8Pt,histYAK8Pt,"allhistos.png")

    #plotHistogram(matchedHiggsMasses,outPrefix+"_FatJetMass_fromHiggs.png","AK8 from H mass histogram","Mass [GeV]",0.,600.)
    #plotHistogram(matchedYMasses,outPrefix+"_FatJetMass_fromY.png","AK8 from Y mass histogram","Mass [GeV]",0.,600.)
    #plotHistogram(matchedHiggsPts,outPrefix+"_FatJetPt_fromHiggs.png","AK8 from H pt histogram","Pt [GeV]",0.,2500.)
    #plotHistogram(matchedYPts,outPrefix+"_FatJetPt_fromY.png","AK8 from Y pt histogram","Pt [GeV]",0.,2500.)


if __name__ == '__main__':
    #analyzeFile("E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root","mx2000")
    massPoints = ["90","100","125","150","200","250","300","400","500","600","700","800","900","1000","1200","1400","1600","1800"]
    # for massPoint in massPoints:
    #     processSingleYMassPoint("E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root",massPoint)
    processAllYMassPoints("E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root")