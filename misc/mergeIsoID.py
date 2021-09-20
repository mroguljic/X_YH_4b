import ROOT as r
import numpy as np

def mergeSFs(hIso,hId,hName):
    hRes = hIso.Clone(hName)
    for i in range(1,hIso.GetNbinsX()+1):
        for j in range(1,hIso.GetNbinsY()+1):
            val         = hIso.GetBinContent(i,j)*hId.GetBinContent(i,j)
            relErrIso   = hIso.GetBinError(i,j)/(hIso.GetBinContent(i,j)+0.000001)
            relErrId    = hId.GetBinError(i,j)/(hId.GetBinContent(i,j)+0.0000001)
            err         = val*np.sqrt(relErrIso*relErrIso+relErrId*relErrId)
            hRes.SetBinContent(i,j,val)
            hRes.SetBinError(i,j,err)
    hRes.SetDirectory(0)
    return hRes


#2016#
IdFile1   = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_2016_legacy_rereco_rootfiles_RunBCDEF_SF_ID.root"   
IdName1   = "NUM_TightID_DEN_genTracks_eta_pt"
IdFile2   = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_2016_legacy_rereco_rootfiles_RunGH_SF_ID.root"   
IdName2   = "NUM_TightID_DEN_genTracks_eta_pt"
IsoFile1  = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_2016_legacy_rereco_rootfiles_RunBCDEF_SF_ISO.root"
IsoName1  = "NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt"
IsoFile2  = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_2016_legacy_rereco_rootfiles_RunGH_SF_ISO.root"
IsoName2  = "NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt"

lumiBCDEF = 19.961
lumiGH    = 16.227

IdFile1   = r.TFile.Open(IdFile1)
IsoFile1  = r.TFile.Open(IsoFile1)
hID1      = IdFile1.Get(IdName1)
hIso1     = IsoFile1.Get(IsoName1)
hSF1      = mergeSFs(hIso1,hID1,"TightID_TightRelISO_SF_eta_pt")
IdFile1.Close()
IsoFile1.Close()


IdFile2   = r.TFile.Open(IdFile2)
IsoFile2  = r.TFile.Open(IsoFile2)
hID2      = IdFile2.Get(IdName2)
hIso2     = IsoFile2.Get(IsoName2)
hSF2      = mergeSFs(hIso2,hID2,"TightID_TightRelISO_SF_eta_pt_temp")

hSF1.Scale(lumiBCDEF/(lumiBCDEF+lumiGH))
hSF2.Scale(lumiGH/(lumiBCDEF+lumiGH))
hSF1.Add(hSF2)

f = r.TFile.Open("2016_ReReco_muon_TightIsoTightID_SF.root","RECREATE")
f.cd()
hSF1.Write()
f.Close()

#2017#
IdFile    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2017_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root"
IdName    = "NUM_TightID_DEN_TrackerMuons_abseta_pt"
IsoFile   = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2017_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2017_UL_ISO.root"
IsoName   = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt"

IdFile   = r.TFile.Open(IdFile)
IsoFile  = r.TFile.Open(IsoFile)
hID      = IdFile.Get(IdName)
hIso     = IsoFile.Get(IsoName)
hSF      = mergeSFs(hIso,hID,"TightID_TightRelISO_SF_eta_pt")
IdFile.Close()
IsoFile.Close()

f = r.TFile.Open("2017_UL_muon_TightIsoTightID_SF.root","RECREATE")
f.cd()
hSF.Write()
f.Close()


#2018#
IdFile    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2018_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.root"
IdName    = "NUM_TightID_DEN_TrackerMuons_abseta_pt"    
IsoFile   = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/EfficienciesStudies_UL2018_DEN_TrackerMuons_rootfiles_Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.root"
IsoName   = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt"

IdFile   = r.TFile.Open(IdFile)
IsoFile  = r.TFile.Open(IsoFile)
hID      = IdFile.Get(IdName)
hIso     = IsoFile.Get(IsoName)
hSF      = mergeSFs(hIso,hID,"TightID_TightRelISO_SF_eta_pt")
IdFile.Close()
IsoFile.Close()

f = r.TFile.Open("2018_UL_muon_TightIsoTightID_SF.root","RECREATE")
f.cd()
hSF.Write()
f.Close()