import ROOT as r
import numpy as np

def findNeighbors(h2,i,j,direction="vert"):
    #Return -1 if no bins from which to interpolate
    binLow  = -1
    binHigh = -1
    ny = h2.GetNbinsY()
    nx = h2.GetNbinsY()
    
    if(direction=="vert"):
        for jBin in range(1,j):
            if(h2.GetBinContent(i,jBin)!=0):
                binLow = jBin

        for jBin in range(j,ny+1):
            if(h2.GetBinContent(i,jBin)!=0):
                binHigh = jBin
                break
    else:
        for iBin in range(1,i):
            if(h2.GetBinContent(iBin,j)!=0):
                binLow = iBin

        for iBin in range(i,nx+1):
            if(h2.GetBinContent(iBin,j)!=0):
                binHigh = iBin
                break        
    return binLow,binHigh       

# def logInterpolation(coord,coordLo,coordHi,valLo,valHi):
#     logLo   = np.log(valLo)
#     logHi   = np.log(valHi)
#     logDist = (coord-coordLo)/(coordHi-coordLo)
#     logInt  = (logHi-logLo)*relDist + logLo
#     intVal  = np.exp(logInt)
#     return intVal

def logInterpolation(coord,coordLo,coordHi,valLo,valHi):
    logDist = (np.log(coord)-np.log(coordLo))/(np.log(coordHi)-np.log(coordLo))
    logInt  = (valHi-valLo)*logDist + valLo
    return logInt

def interpolateBin(h2,i,j,binLo,binHi,direction="vert"):
    if(direction=="vert"):
        coord   = h2.GetYaxis().GetBinCenter(j)
        coordLo = h2.GetYaxis().GetBinCenter(binLo)
        coordHi = h2.GetYaxis().GetBinCenter(binHi)

        valLo   = h2.GetBinContent(i,binLo)
        valHi   = h2.GetBinContent(i,binHi)
    else:
        coord   = h2.GetXaxis().GetBinCenter(i)
        coordLo = h2.GetXaxis().GetBinCenter(binLo)
        coordHi = h2.GetXaxis().GetBinCenter(binHi)
        
        valLo   = h2.GetBinContent(binLo,j)
        valHi   = h2.GetBinContent(binHi,j)


    val     = logInterpolation(coord,coordLo,coordHi,valLo,valHi)
    return val


def interpolateHisto(h2,direction="vert",hName=""):
    if(hName):
        h2_inter = h2.Clone(hName)
    else:
        h2_inter = h2.Clone(h2.GetName()+"{0}_int".format(direction))

    nx = h2.GetNbinsX()
    ny = h2.GetNbinsY()

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            if(h2.GetBinContent(i,j)!=0):
                continue
            mx = h2.GetXaxis().GetBinCenter(i)
            my = h2.GetYaxis().GetBinCenter(j)

            if not (mx>(6*min(my, 125) + max(my, 125))):
                #Boosted condition
                continue
            binLow,binHigh = findNeighbors(h2,i,j,direction)
            if(binLow==-1 or binHigh==-1):
                continue
            interVal = interpolateBin(h2,i,j,binLow,binHigh,direction)
            h2_inter.SetBinContent(i,j,interVal)

    h2_inter.SetDirectory(0)
    return h2_inter