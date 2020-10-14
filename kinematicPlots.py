import ROOT as r
from optparse import OptionParser
from time import sleep
import json

def mergeQCDs(histos):
    qcdHistFlag = False
    idxToRemove = []
    for i,h in enumerate(histos):
        if not "QCD" in  h.GetTitle():
            continue
        if not qcdHistFlag:
            hQCDIdx = i
            qcdHistFlag = True
            continue
        histos[hQCDIdx].Add(h)
        idxToRemove.append(i)

    for idx in reversed(idxToRemove):
        histos.pop(idx)
    return histos

def stackHistos(data,region,tagger,outFile):
    if(str(tagger) == "dak8"):
        taggerFull = "DeepAK8"
    elif(str(tagger) == "pnet"):
        taggerFull = "ParticleNet"
    else:
        taggerFull = tagger
        
    hStack       = r.THStack("hs","{0} region, {1} tagger".format(region,taggerFull))
    legend       = r.TLegend(0.5,0.6,0.8,0.8)
    histos       = []
    for sample, sample_cfg in data.items():
        h = getInvMass_h(sample,sample_cfg,region,tagger)
        histos.append(h)

    histos.sort(key=lambda x: x.GetName())
    histos = mergeQCDs(histos)

    c = r.TCanvas("c","c",1500,1000)
    c.SetLogy()
    hSignal = False
    for h in histos:
        print(h.GetTitle())
        if "X" in h.GetName():
            hSignal = h
            hSignal.SetLineWidth(2)
            continue
        hStack.Add(h)
        if "QCD" in h.GetName():
            h.SetLineWidth(1)
            legend.AddEntry(h,"QCD","F")
        if "tt" in h.GetName():
            h.SetLineWidth(1)
            legend.AddEntry(h,"ttbar","F")

    hStack.Draw("hist")
    hStack.GetXaxis().SetLimits(1000., 3000.);
    hStack.SetMinimum(10)
    #hStack.SetMaximum(1300)
    hStack.SetMaximum(130000)
    if(hSignal):
        legend.AddEntry(hSignal,"X: 1600 GeV","L")
        hSignal.Draw("hist same")
    
    hStack.GetXaxis().SetNdivisions(805, r.kTRUE);
    hStack.GetXaxis().SetTitle("m_{jj} [GeV]")
    hStack.GetYaxis().SetTitle("Events / 100 GeV")
    legend.SetFillStyle(0)
    legend.SetLineWidth(0)
    legend.Draw()

    pt = r.TPaveText(0.5,0.55,0.8,0.60,"NDC")
    pt.SetTextSize(0.04)
    pt.SetFillColor(0)
    pt.SetTextAlign(12)
    pt.SetLineWidth(0)
    pt.SetBorderSize(1)
    #pt.AddText("CMS Preliminary")
    pt.AddText("#sigma #bf{( pp #rightarrow X #rightarrow HY #rightarrow b#bar{b}b#bar{b}) = 10 fb}")
    pt.Draw()

    pt2 = r.TPaveText(0.71,0.92,0.9,0.95,"NDC")
    pt2.SetTextSize(0.04)
    pt2.SetFillColor(0)
    pt2.SetTextAlign(12)
    pt2.SetLineWidth(0)
    pt2.SetBorderSize(1)
    pt2.AddText("#bf{137 fb^{-1} (13 TeV)}")
    pt2.Draw()

    c.Update()
    c.SaveAs(outFile)


def getInvMass_h (sample,sample_cfg,region,tagger,luminosity=137000):#inverse pb
    tempFile = r.TFile.Open(sample_cfg["file"])
    hCutFlow = tempFile.Get("hCutFlow_{0}".format(tagger))
    h2d      = tempFile.Get("{0}_mjHY_mjH_{1}_{2}".format(sample,tagger,region))
    nTotal   = hCutFlow.GetBinContent(1)
    nRegion  = h2d.Integral()
    xsec     = sample_cfg['xsec']    
    eff      = nRegion/nTotal
    norm     = eff*luminosity*xsec
    hInvMass = h2d.ProjectionX("{0}_mjHY_{1}_{2}".format(sample,tagger,region))
    hInvMass.Scale(norm/hInvMass.Integral())
    hInvMass.SetTitle("{0}_{1}_{2} HY invariant mass".format(sample,tagger,region))   
    hInvMass.Rebin(10) 
    color    = sample_cfg["color"]

    if "X" in str(sample):
        hInvMass.SetLineColor(color)
        hInvMass.SetLineWidth(3)
    else:
        hInvMass.SetFillColorAlpha(color,0.50)
        hInvMass.SetLineWidth(0)

    hInvMass.SetDirectory(0)#otherwise the histogram is destroyed when file is closed
    tempFile.Close()

    return hInvMass


def nMinusOnePlot(data,cut,outFile,xTitle="",yTitle="",rangeX=[],stackTitle="",sigLabel="Signal"):
    title        = "N-1 plot - {0}".format(cut)
    if(stackTitle!=""):
        title=stackTitle
    hStack       = r.THStack("hs",title)
    legend       = r.TLegend(0.5,0.65,0.8,0.85)
    histos       = []
    for sample, sample_cfg in data.items():
        tempFile = r.TFile.Open(sample_cfg["file"])
        h = tempFile.Get("{0}_nm1_{1}".format(sample,cut))
        h.SetDirectory(0)

        color    = sample_cfg["color"]
        if "X" in str(sample):
            h.SetLineColor(color)
        else:
            h.SetFillColorAlpha(color,0.50)
        histos.append(h)

    c = r.TCanvas("c","c",1500,1000)
    c.SetLogy()
    hSignal = False
    for h in histos:
        if "X" in h.GetName():
            hSignal = h
            hSignal.SetLineWidth(2)
            continue
        hStack.Add(h)
        if "QCD" in h.GetName():
            h.SetLineWidth(1)
            legend.AddEntry(h,"QCD","F")
        if "tt" in h.GetName():
            h.SetLineWidth(1)
            legend.AddEntry(h,"ttbar","F")

    hStack.Draw("hist")
    hStack.SetMinimum(10)
    #hStack.SetMaximum(1300)
    #hStack.SetMaximum(130000)

    if(rangeX!=[]):
        hStack.GetXaxis().SetLimits(rangeX[0],rangeX[1])

    if(hSignal):
        legend.AddEntry(hSignal,sigLabel,"L")
        hSignal.Draw("hist same")
    
    #hStack.GetXaxis().SetNdivisions(805, r.kTRUE);
    hStack.GetXaxis().SetTitle(xTitle)
    hStack.GetYaxis().SetTitle(yTitle)
    legend.SetFillStyle(0)
    legend.SetLineWidth(0)
    legend.Draw()

    pt = r.TPaveText(0.5,0.6,0.8,0.65,"NDC")
    pt.SetTextSize(0.04)
    pt.SetFillColor(0)
    pt.SetTextAlign(12)
    pt.SetLineWidth(0)
    pt.SetBorderSize(1)
    #pt.AddText("CMS Preliminary")
    pt.AddText("#sigma #bf{( pp #rightarrow X #rightarrow HY #rightarrow b#bar{b}b#bar{b}) = 1 pb}")
    pt.Draw()

    pt2 = r.TPaveText(0.71,0.92,0.9,0.95,"NDC")
    pt2.SetTextSize(0.04)
    pt2.SetFillColor(0)
    pt2.SetTextAlign(12)
    pt2.SetLineWidth(0)
    pt2.SetBorderSize(1)
    pt2.AddText("#bf{137 fb^{-1} (13 TeV)}")
    pt2.Draw()

    c.Update()
    c.SaveAs(outFile)




if __name__ == '__main__':
    r.gROOT.SetBatch()
    parser = OptionParser()
    parser.add_option('-j', '--json', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'json',
                help      =   'Json file containing names, paths to histograms, xsecs etc.')
    (options, args) = parser.parse_args()

    with open(options.json) as json_file:
        data = json.load(json_file)
        cuts = ["DeltaEta","ptjH","ptjY","mjH","mjY","pnetH","pnetY"]
        nMinusOnePlot(data,"mjY","mjY.png",rangeX=[0,500],xTitle="mSD Y-jet [GeV]",yTitle="Events / 10 GeV",stackTitle="N-1: mSD for Y-tagged jets",sigLabel="M_X, M_Y = 1600, 100 GeV")
        nMinusOnePlot(data,"mjH","mjH.png",rangeX=[0,500],xTitle="mSD H-jet [GeV]",yTitle="Events / 10 GeV",stackTitle="N-1: mSD for H-tagged jets",sigLabel="M_X, M_Y = 1600, 100 GeV")
        nMinusOnePlot(data,"ptjH","ptjH.png",rangeX=[0,2000],xTitle="pT H-jet [GeV]",yTitle="Events / 20 GeV",stackTitle="N-1: pT for H-tagged jets",sigLabel="M_X, M_Y = 1600, 100 GeV")
        nMinusOnePlot(data,"ptjY","ptjY.png",rangeX=[0,2000],xTitle="pT Y-jet [GeV]",yTitle="Events / 20 GeV",stackTitle="N-1: pT for Y-tagged jets",sigLabel="M_X, M_Y = 1600, 100 GeV")
        nMinusOnePlot(data,"DeltaEta","DeltaEta.png",rangeX=[0,5],xTitle="mSD [GeV]",yTitle="Events/bin",stackTitle="N-1: |eta_{1} - eta_{2}|",sigLabel="M_X, M_Y = 1600, 100 GeV")
        nMinusOnePlot(data,"pnetH","pnetH.png",rangeX=[0,1],xTitle="ParticleNetMD_probXbb score",yTitle="Events/bin",stackTitle="N-1: b-tagger for H-tagged jets",sigLabel="M_X, M_Y = 1600, 100 GeV")
        nMinusOnePlot(data,"pnetY","pnetY.png",rangeX=[0,1],xTitle="ParticleNetMD_probXbb score",yTitle="Events/bin",stackTitle="N-1: b-tagger for Y-tagged jets",sigLabel="M_X, M_Y = 1600, 100 GeV")
        # for cut in cuts:
        #     nMinusOnePlot(data,cut,"{0}.png".format(cut))
        # stackHistos(data,"TT","pnet","TT_pnet.pdf")
        # stackHistos(data,"LL","pnet","LL_pnet.pdf")
        # stackHistos(data,"TT","dak8","TT_dak8.pdf")
        # stackHistos(data,"LL","dak8","LL_dak8.pdf")
