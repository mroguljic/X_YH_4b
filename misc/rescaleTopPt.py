import os
import ROOT as r


def getHadronicScaling(inputFile):
    f           = r.TFile.Open(inputFile)
    hBeforePt   = f.Get("TTbar_mJY_mJJ_AL_L_ptRwtDown")
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_AL_T_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_AL_AL_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_LL_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_TT_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_L_AL_ptRwtDown"))
    hAfterPt    = f.Get("TTbar_mJY_mJJ_AL_L_nom")
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_AL_T_nom"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_AL_AL_nom"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_LL_nom"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_TT_nom"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_L_AL_nom"))
    scale       = hBeforePt.Integral()/hAfterPt.Integral()
    return scale

def getHadronicScalingRwtUp(inputFile):
    f           = r.TFile.Open(inputFile)
    hBeforePt   = f.Get("TTbar_mJY_mJJ_AL_L_ptRwtDown")
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_AL_T_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_AL_AL_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_LL_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_TT_ptRwtDown"))
    hBeforePt.Add(f.Get("TTbar_mJY_mJJ_L_AL_ptRwtDown"))
    hAfterPt    = f.Get("TTbar_mJY_mJJ_AL_L_ptRwtUp")
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_AL_T_ptRwtUp"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_AL_AL_ptRwtUp"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_LL_ptRwtUp"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_TT_ptRwtUp"))
    hAfterPt.Add(f.Get("TTbar_mJY_mJJ_L_AL_ptRwtUp"))
    scale       = hBeforePt.Integral()/hAfterPt.Integral()
    return scale


def scaleHadronicTemplates(inputFile):
    f           = r.TFile.Open(inputFile)
    scalings    = {}
    newHistos   = []
    scale       = getHadronicScaling(inputFile)
    rwtUpScale  = getHadronicScalingRwtUp(inputFile)
    print(scale, rwtUpScale)
    for key in f.GetListOfKeys():
        h       = key.ReadObj()
        hName   = h.GetName()
        h.SetDirectory(0)
        if(("_mJY_mJJ_" in hName or "mJY_pT_" in hName) and not "ptRwt" in hName):
            normBefore = h.Integral()
            h.Scale(scale)
            normAfter  = h.Integral()
            #print("{0}: {1} -> {2}".format(hName,normBefore,normAfter))
            newHistos.append(h)
        elif("ptRwtUp" in hName):
            normBefore = h.Integral()
            h.Scale(rwtUpScale)
            normAfter  = h.Integral()
            #print("{0}: {1} -> {2}".format(hName,normBefore,normAfter))
            newHistos.append(h)
        else:
            newHistos.append(h)    
    f.Close()

    cpCmd = "cp {0} {1}".format(inputFile,inputFile.replace(".root","_backup.root"))
    os.system(cpCmd)

    f = r.TFile.Open(inputFile,"recreate")
    f.cd()
    for h in newHistos:
        h.Write()
    f.Close()

def getSemileptonicScaling(inputFile):
    f           = r.TFile.Open(inputFile)
    print(inputFile)
    hBeforePt   = f.Get("TTbar_mSD_I_ptRwtDown")
    hAfterPt    = f.Get("TTbar_mSD_I_nom")
    scale       = hBeforePt.Integral()/hAfterPt.Integral()
    return scale

def getSemileptonicScalingRwtUp(inputFile):
    f           = r.TFile.Open(inputFile)
    hBeforePt   = f.Get("TTbar_mSD_I_ptRwtDown")
    hAfterPt    = f.Get("TTbar_mSD_I_ptRwtUp")
    scale       = hBeforePt.Integral()/hAfterPt.Integral()
    return scale

def scaleSemileptonicTemplates(inputFile):
    f           = r.TFile.Open(inputFile)
    newHistos   = []
    scaling     = getSemileptonicScaling(inputFile)
    rwtUpScale  = getSemileptonicScalingRwtUp(inputFile)
    print(scaling, rwtUpScale)
    for key in f.GetListOfKeys():
        h       = key.ReadObj()
        hName   = h.GetName()
        h.SetDirectory(0)
        if("_mSD_" in hName and not "ptRwt" in hName):
            h.Scale(scaling)
            newHistos.append(h)
        elif("ptRwtUp" in hName):
            h.Scale(rwtUpScale)
            newHistos.append(h)
        elif("cutflow" in hName or "ptRwtDown" in hName):
            newHistos.append(h)    
        else:
            h.Scale(scaling)
            newHistos.append(h)
    f.Close()

    cpCmd = "cp {0} {1}".format(inputFile,inputFile.replace(".root","_backup.root"))
    os.system(cpCmd)

    f = r.TFile.Open(inputFile,"recreate")
    f.cd()
    for h in newHistos:
        h.Write()
    f.Close()




#scaleHadronicTemplates("../results/templates_hadronic/2016/scaled/TTbar16.root")
scaleHadronicTemplates("../results/templates_hadronic/2017/scaled/TTbar17.root")
#scaleHadronicTemplates("../results/templates_hadronic/2018/scaled/TTbar18.root")

# scaleSemileptonicTemplates("../results/templates_semileptonic/electron/2016/scaled/TTbar16.root")
# scaleSemileptonicTemplates("../results/templates_semileptonic/electron/2017/scaled/TTbar17.root")
# scaleSemileptonicTemplates("../results/templates_semileptonic/electron/2018/scaled/TTbar18.root")
# scaleSemileptonicTemplates("../results/templates_semileptonic/muon/2016/scaled/TTbar16.root")
# scaleSemileptonicTemplates("../results/templates_semileptonic/muon/2017/scaled/TTbar17.root")
# scaleSemileptonicTemplates("../results/templates_semileptonic/muon/2018/scaled/TTbar18.root")
