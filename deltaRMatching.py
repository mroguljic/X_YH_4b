import ROOT as r
import numpy as np
import matplotlib.pyplot as plt
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
    plt.hist(data,100)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid(True)
    plt.savefig(outfile)
    plt.clf()


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

    for i,event in enumerate(tfile.Events):
        # if(i>1000):
        #     break

        if(i%100000==0):
            print(i)

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
                matchedHiggsMasses.append(event.FatJet_mass[fatJetIdx])
                matchedHiggsPts.append(event.FatJet_pt[fatJetIdx])

            if (Y_JetDR<0.8 and b3_JetDR<0.8 and b4_JetDR<0.8):
                matchedYJetIdxs.append(fatJetIdx)
                YDeltaRs.append(Y_JetDR)
                matchedYFlag=True
                matchedYMasses.append(event.FatJet_mass[fatJetIdx])
                matchedYPts.append(event.FatJet_pt[fatJetIdx])


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

    plotHistogram(matchedHiggsMasses,outPrefix+"_FatJetMass_fromHiggs.png","AK8 from H mass histogram","Mass [GeV]",0.,600.)
    plotHistogram(matchedYMasses,outPrefix+"_FatJetMass_fromY.png","AK8 from Y mass histogram","Mass [GeV]",0.,600.)
    plotHistogram(matchedHiggsPts,outPrefix+"_FatJetPt_fromHiggs.png","AK8 from H pt histogram","Pt [GeV]",0.,2500.)
    plotHistogram(matchedYPts,outPrefix+"_FatJetPt_fromY.png","AK8 from Y pt histogram","Pt [GeV]",0.,2500.)


analyzeFile("E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root","mx2000")