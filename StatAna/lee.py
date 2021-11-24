import ROOT as r
import numpy as np
import ctypes
import os
import numpy

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0000)

def significanceToHistos(output):
    MX = np.array([900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600,2800,3000,3500,4000,4500],dtype='float64')
    MY = np.array([60,70,80,90,100,125,150,200,250,300,350,400,450,500,600,700],dtype='float64')

    h2Ds = []
    for i in range(100):
        h2D = r.TH2D("q_toy_{0}".format(i),"",len(MX)-1,MX,len(MY)-1,MY)
        h2Ds.append(h2D)

    for mx in MX:
        for my in MY:
            if not (mx>(6*min(my, 125) + max(my, 125))):
                continue
            if(mx>4000 or my>600):
                continue
            tempFileName = "limits/lee_pvals/MX{0}_MY{1}.root".format(int(mx),int(my))
            fTemp = r.TFile.Open(tempFileName)
            ttree = fTemp.Get("limit")
            nToys = ttree.GetEntriesFast()
            if(nToys!=100):
                print("n toys != 100")
            for i in range(nToys):
                ttree.GetEntry(i)
                pval = ttree.limit


                if(pval>=0.5):
                    q = 0#q is 2*DeltaNLL
                else:
                    zscore  = r.RooStats.PValueToSignificance(pval)
                    q = zscore**2

                binx = h2Ds[i].GetXaxis().FindBin(mx)
                biny = h2Ds[i].GetYaxis().FindBin(my)
                h2Ds[i].SetBinContent(binx,biny,q)
            fTemp.Close()

    f = r.TFile.Open(output,"RECREATE")
    f.cd()
    for h2D in h2Ds:
        h2D.Write()
    f.Close()

def plotMaps(inputFile,level,N=20):
    f = r.TFile.Open(inputFile)
    c = r.TCanvas("c","",1500,1200)
    c.SetMargin(0.15,0.15,0.15,0.15)
    for i in range(N):
        h2D = f.Get("q_toy_{0}".format(i))
        h2D.SetMinimum(level)
        h2D.Draw("colz")
        c.SaveAs("lee_plots/q_{1}_toy_{0}.png".format(i,level))


def findNeighbours(h2,i,j,q_cutoff):
#Returns bins neighbouring i,j which satisfy q>q_cutoff
#q!=0 condition protects against empty and overflow bins 
#Bins returned as global bin numbers!

    globalBins = []
    #left
    globBin  = h2.GetBin(i-1,j)
    q        = h2.GetBinContent(globBin)
    if (q!=0 and q>q_cutoff):
        globalBins.append(globBin)
    #right
    globBin  = h2.GetBin(i+1,j)
    q        = h2.GetBinContent(globBin)
    if (q!=0 and q>q_cutoff):
        globalBins.append(globBin)
    #top
    globBin  = h2.GetBin(i,j+1)
    q        = h2.GetBinContent(globBin)
    if (q!=0 and q>q_cutoff):
        globalBins.append(globBin)
    #bottom
    globBin  = h2.GetBin(i,j-1)
    q        = h2.GetBinContent(globBin)
    if (q!=0 and q>q_cutoff):
        globalBins.append(globBin)

    return globalBins

def checkForCluster(neighbBins,clusters):
#Checks if any neighbouring bins belong to any clusters
#Returns first matched cluster, False otherwise
    for cluster, bins in clusters.items():
        if any(i in bins for i in neighbBins):
            return cluster
    return False

def updateClusters(clusters,globBin,clusterFlag,usedBins):
#Adds global bin to clusters in clusterList
#If clusterList empty, start a new cluster
    if(clusterFlag):
        clusters[clusterFlag].append(globBin)
    else:
        clusterNumbers = [*clusters]
        clusterNumbers.sort()
        if not clusterNumbers:
            newCluster = 1
            clusters[newCluster] = [globBin]
        else:
            newCluster = clusterNumbers[-1]+1
            clusters[newCluster] = [globBin]
    usedBins.append(globBin)

def initialClusters(h2,clusters,usedBins,q_cutoff):
    NX = h2.GetNbinsX()
    NY = h2.GetNbinsY()
    for i in range(1,NX+1):
        for j in range(1,NY+1):
            q           = h2.GetBinContent(i,j)
            globBin     = h2.GetBin(i,j)
            if(q<q_cutoff):
                continue
            if(globBin in usedBins):
                continue

            neighbBins  = findNeighbours(h2,i,j,q_cutoff)
            clusterFlag = checkForCluster(neighbBins,clusters)
            updateClusters(clusters,globBin,clusterFlag,usedBins)

def checkNeighbours(h2,bins1,bins2):
#Returns true if any bin in bins1 is a neghbour of any bin in bins2
#False otherwise
    for bin1 in bins1:
        bin1_i = ctypes.c_int(0)
        bin1_j = ctypes.c_int(0)
        bin1_k = ctypes.c_int(0)
        h2.GetBinXYZ(bin1,bin1_i,bin1_j,bin1_k)
        for bin2 in bins2:
            bin2_i = ctypes.c_int(0)
            bin2_j = ctypes.c_int(0)
            bin2_k = ctypes.c_int(0)
            h2.GetBinXYZ(bin2,bin2_i,bin2_j,bin2_k)
            if(bin1_i.value==bin2_i.value and abs(bin2_j.value-bin1_j.value)==1):
                return True
            if(bin1_j.value==bin2_j.value and abs(bin2_i.value-bin1_i.value)==1):
                return True
    return False

def mergeClusters(h2,clusters):
#Merges clusters, returns true if merged, false if nothing needed merging
    clusterNumbers = [*clusters]
    nClusters      = len(clusterNumbers)
    mergePairs     = []
    for i in range(nClusters-1):
        cluster1   = clusterNumbers[i]
        for j in range(i+1,nClusters):
            cluster2      = clusterNumbers[j]
            neighbourFlag = checkNeighbours(h2,clusters[cluster1],clusters[cluster2])
            if(neighbourFlag):
                mergePairs.append((cluster1,cluster2))#(Receiving cluster,donating cluster)

    if not mergePairs:
        return False

    for pair in reversed(mergePairs):
    #Merge pairs is ordered in receiving and donating cluster indices, exp [(1,2),(3,4),(3,5)]
    #We want to first merge later indices since the receiving cluster merged with later
    #donating cluster may be merged (by donating) with prior receiving cluster
        receivingKey = pair[0]
        donatingKey  = pair[1]
        if not donatingKey in clusters:
        #This may happen if one cluster should be merged with multiple clusters
            continue
        clusters[receivingKey].extend(clusters[donatingKey])
        clusters.pop(donatingKey,None)

    return True

def getNClusters(h2,level):
    clusters = {}
    usedBins = []
    initialClusters(h2,clusters,usedBins,level)
    mergeFlag = True
    while(mergeFlag):   
        mergeFlag = mergeClusters(h2,clusters)
    return(len(clusters))



#significanceToHistos("lee.root")
level1  = 1
level2  = 4
zscore1 = np.sqrt(level1)
zscore2 = np.sqrt(level2)
pval1   = r.RooStats.SignificanceToPValue(zscore1)
pval2   = r.RooStats.SignificanceToPValue(zscore2)

print("q levels: {0}, {1}".format(level1,level2))
print("p-values: {0:.3f}, {1:.3f}".format(pval1,pval2))
#plotMaps("lee.root",level1)
#plotMaps("lee.root",level2)

f = r.TFile.Open("lee.root")
phis_1 = []
phis_2 = []
counter = 0
for i in range(0,100):
    h2D    = f.Get("q_toy_{0}".format(i))
    if(h2D.GetMaximum()>9.56):
        counter+=1
    phi1   = getNClusters(h2D,level1)
    phi2   = getNClusters(h2D,level2)
    phis_1.append(phi1)
    phis_2.append(phi2)
print(counter)


# #print(phis_1)
# #print(phis_2)
E1 = np.mean(phis_1)
E2 = np.mean(phis_2)

print("q>{0}: E[Phi]={1:.2f}+/-{2:.2f}".format(level1,np.mean(phis_1),np.std(phis_1)/np.sqrt(len(phis_1))))
print("q>{0}: E[Phi]={1:.2f}+/-{2:.2f}".format(level2,np.mean(phis_2),np.std(phis_2)/np.sqrt(len(phis_2))))


A = np.array([[np.exp(-level1/2),np.exp(-level1/2)*np.sqrt(level1)],[np.exp(-level2/2),np.exp(-level2/2)*np.sqrt(level2)]])
B = np.array([E1-pval1,E2-pval2])

N1, N2 = np.linalg.solve(A, B)
print("N1: {0:.2f}, N2:{1:.2f}".format(N1, N2))

zmax = 3.06
qmax = zmax*zmax
pmax = r.RooStats.SignificanceToPValue(zmax)

pglobal = pmax+np.exp(-qmax/2.)*(N1+np.sqrt(qmax)*N2)
print("Global significance {0:.2f} (p-value: {1:.3f})".format(r.RooStats.PValueToSignificance(pglobal),pglobal))
