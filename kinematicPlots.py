import ROOT as r
from optparse import OptionParser
from time import sleep

def kinematicPlot(histos,labels,fillColors,title,outfile):
    hStack = r.THStack("hs",title)
    legend = r.TLegend(0.6,0.7,0.9,0.9)
    for i,h in enumerate(histos):
        h.SetFillColor(fillColors[i])
        h.SetLineWidth(0)
        hStack.Add(h)
        legend.AddEntry(h,labels[i])

    c = r.TCanvas("c","c",1000,1000)
    c.SetLogy()
    hStack.Draw("h")
    hStack.SetMinimum(0.01)

    legend.Draw()
    c.Update()
    c.SaveAs(outfile)



def getHistProcess(ProcessFiles,xsections,scale,variable,nbins,xlow,xup,outputFile=False):
    hMaster = r.TH1F("hMaster","hMaster",nbins,xlow,xup)

    for Processfile, xs in zip(ProcessFiles, xsections):
        f = r.TFile.Open(Processfile,"r")
        N = f.Get("total").GetEntriesFast()
        w = scale*xs/N
        selectionTree = f.Get("selection2")
        hTemp = r.TH1F("hTemp","hTemp",nbins,xlow,xup)
        selectionTree.Draw(variable+">>hTemp")
        hMaster.Add(hTemp,w)        
        print("File {0} with xs {1} pb".format(Processfile,xs))
        print("Nevents = {0}    Nselection = {1}    w={2}".format(N,selectionTree.GetEntriesFast(),w))


    if(outputFile):
        c = r.TCanvas("c","c",1000,1000)
        hMaster.Draw()
        c.SaveAs(outputFile)
    return hMaster



def getScaling(file,xsection):
    f = r.TFile.Open(file,"r")
    N = f.Get("total").GetEntriesFast()
    scaling = N/xsection
    return scaling


if __name__ == '__main__':
    r.gROOT.SetBatch()
    #parser = OptionParser()
    #parser.add_option('-i',"--inputFile", dest='inputFile', default='/home/matej/Zbb_SF/ZbbJet/dak8/dak8_M2_2016_May10_tightMatch_ttvetoM_withDDT/data/hbb_dak8MDZHbb_Feb20_tightMatch_ttvetoM_newMassCorr_withDDT_M.root', help='.root with data',metavar='inputFile')
    #(options, args) = parser.parse_args()
    #kinematicPlot("QCD.root","ttbar.root","signal.root","FatJet_pt[0]",0,5000,50)
    #xsections = {}
    QCDfiles    = [
    '/afs/cern.ch/user/m/mrogulji/store/QCD/QCDHT700.root',
    '/afs/cern.ch/user/m/mrogulji/store/QCD/QCDHT1000.root',
    '/afs/cern.ch/user/m/mrogulji/store/QCD/QCDHT1500.root',
    '/afs/cern.ch/user/m/mrogulji/store/QCD/QCDHT2000.root']
    ttbarFiles  = ['/afs/cern.ch/user/m/mrogulji/store/ttbar/ttbar.root']
    signalFiles = ['/afs/cern.ch/user/m/mrogulji/store/mx1600.root']

    QCD_xsections    = [6800,1200.,120.,25.24]#pb
    ttbar_xsections  = [831.8]
    signal_xsections = [0.01]

    variables = [["invariantMass",1000,2000],["deltaEta",-2.,2.],["FatJet_pt[0]",250.,1250.],["FatJet_pt[1]",250.,1250.],
    ["FatJet_msoftdrop[0]",0.,500.],["FatJet_msoftdrop[1]",0.,500.],["FatJet_deepTagMD_ZHbbvsQCD",0.,1.]]


    #variable = "invariantMass"
    scale = getScaling('/afs/cern.ch/user/m/mrogulji/store/QCD/QCDHT1000.root',1200.)
    scale = 5000.#How many events per 1pb
    print("Scaling is {0} events per 1pb".format(scale))
    nbins = 20
    xlow = 1000
    xup = 2000
    for variable in variables:
        histos = []
        histos.append(getHistProcess(signalFiles,signal_xsections,scale,variable[0],nbins,variable[1],variable[2]))#,outputFile='signal.png')
        histos.append(getHistProcess(QCDfiles,QCD_xsections,scale,variable[0],nbins,variable[1],variable[2]))#,outputFile='qcd.png')
        histos.append(getHistProcess(ttbarFiles,ttbar_xsections,scale,variable[0],nbins,variable[1],variable[2]))#,outputFile='ttbar.png')
        labels = ["X->YH","QCD","ttbar"]
        colors = [r.kBlue,r.kViolet,r.kGray]
        kinematicPlot(histos,labels,colors,variable[0],variable[0]+".png")
