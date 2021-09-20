import ROOT as r
import numpy as np
import sys
import os.path
from tdrStyle import setTDRStyle
setTDRStyle()
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0000)
r.gROOT.ForceStyle();

def get2DTrigEff(file,effName,outputFile,xTitle="",yTitle="",xLimits=[],yLimits=[],label="",file2="",file2Scale=0.45):

    f   = r.TFile.Open(file)
    eff = f.Get(effName)
    if(file2):
        g = r.TFile.Open(file2)
        temp = g.Get(effName)
        temp.Scale(file2Scale)
        eff.Scale(1.0-file2Scale)
        eff.Add(temp)
    if(xTitle):
        eff.GetXaxis().SetTitle(xTitle)
    if(yTitle):
        eff.GetYaxis().SetTitle(yTitle)
    c = r.TCanvas("a","a",1500,1500)
    c.SetMargin(0.20,0.05,0.15,0.05)
    c.cd()
    eff.SetMaximum(1.0)
    eff.SetMinimum(0.5)
    eff.GetYaxis().SetTitleOffset(1.40)
    eff.GetXaxis().SetTitleSize(.05);
    eff.GetYaxis().SetTitleSize(.05);
    if(xLimits):
        eff.GetXaxis().SetRangeUser(xLimits[0],xLimits[1])
    if(yLimits):
        eff.GetYaxis().SetRangeUser(yimits[0],yLimits[1])
    eff.Draw("col text 45")
    r.gPad.Update()
    r.gStyle.SetPaintTextFormat("1.2f")
    r.gPad.Update()

    #legend = r.TLegend(0.2,0.8,0.6,1.0)
    legend = r.TLegend(0.23,0.8,0.50,1.0)
    legend.SetFillStyle(0)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.04)
    legend.SetHeader(label)
    #legend.AddEntry(eff,label,"L")
    legend.Draw()
    r.gPad.Update()
    c.SaveAs(outputFile)
    c.Close()
    f.Close()

TIMBERDATA    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/TIMBER/TIMBER/data/OfficialSFs/"
trigFile2016  = "EfficienciesAndSF_RunBtoF.root"
trigFile22016 = "EfficienciesAndSF_Period4.root"
trigFile2017  = "EfficienciesStudies_UL2017_Trigger_rootfiles_Efficiencies_muon_generalTracks_Z_Run2017_UL_SingleMuonTriggers.root"
trigFile2018  = "EfficienciesStudies_UL2018_Trigger_rootfiles_Efficiencies_muon_generalTracks_Z_Run2018_UL_SingleMuonTriggers.root"


get2DTrigEff(TIMBERDATA+trigFile2016,"IsoMu24_OR_IsoTkMu24_PtEtaBins/efficienciesDATA/abseta_pt_DATA","muon16Trig.pdf",xTitle="Muon |#eta|",yTitle="Muon p_{T}",label="2016 Muon trigger efficiencies",file2=TIMBERDATA+trigFile22016)
get2DTrigEff(TIMBERDATA+trigFile2017,"NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt_efficiencyData","muon17Trig.pdf",xTitle="Muon |#eta|",yTitle="Muon p_{T}",label="2017 Muon trigger efficiencies")
get2DTrigEff(TIMBERDATA+trigFile2018,"NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt_efficiencyData","muon18Trig.pdf",xTitle="Muon |#eta|",yTitle="Muon p_{T}",label="2018 Muon trigger efficiencies")


trigFileEle = "trigEffs/SingleElectronEfficiencies.root"
get2DTrigEff(trigFileEle,"ele_eff_2016","ele16Trig.pdf",label="2016 Electron trigger efficiencies",xTitle="Electron #eta",yTitle="Electron p_{T}")
get2DTrigEff(trigFileEle,"ele_eff_2017","ele17Trig.pdf",label="2017 Electron trigger efficiencies",xTitle="Electron #eta",yTitle="Electron p_{T}")
get2DTrigEff(trigFileEle,"ele_eff_2018","ele18Trig.pdf",label="2018 Electron trigger efficiencies",xTitle="Electron #eta",yTitle="Electron p_{T}")
