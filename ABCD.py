import ROOT as r

class ABCD():
    """class for handling ABCD method
    A,B are considered sideband failing and passing regions
    C,D are failing and passing  signal regions
    """
    def __init__(self, bkgFiles, bkgSamples, dataFile,dataTag="JetHT"):
        super(ABCD, self).__init__()
        self.bkgFiles   = bkgFiles
        self.bkgSamples = bkgSamples
        self.dataFile   = dataFile
        self.dataTag    = dataTag
        self.regions    = {}#ABCD dict "A":h2_A, "B":h2_B,...
        self.tf         = 0.
        self.h2EstD     = None

    def setRegion(self,region,tag):
        fData  = r.TFile.Open(self.dataFile)
        h2Data = fData.Get("{0}_{1}".format(self.dataTag,tag))
        for i,bkg in enumerate(self.bkgSamples):
            fBkgTemp  = r.TFile.Open(self.bkgFiles[i])
            h2BkgTemp = fBkgTemp.Get("{0}_{1}".format(bkg,tag))
            h2Data.Add(h2BkgTemp,-1)
            fBkgTemp.Close()
        self.regions[region] = h2Data
        self.regions[region].SetDirectory(0)#free histo pointer from root file
        fData.Close()
        print("Region {0} integral: {1:.2f}".format(region,h2Data.Integral()))

    def setABCD(self,tags):
        self.setRegion("A",tags[0])
        self.setRegion("B",tags[1])
        self.setRegion("C",tags[2])
        self.setRegion("D",tags[3])

    def calculateTF(self):
        #First implementation, just a simple yield ratio
        h2B     = self.regions["B"]
        h2A     = self.regions["A"]
        self.tf = h2B.Integral()/h2A.Integral()

    def calculate1DTF(self,projection="X"):
        #First implementation, just a simple yield ratio
        h2B         = self.regions["B"]
        h2A         = self.regions["A"]
        if(projection=="Y"):
            hFail   = h2B.ProjectionY("py_fail",1,-1)#Avoid underflow
            hPass   = h2A.ProjectionY("py_pass",1,-1)
        else:
            hFail   = h2B.ProjectionX("px_fail",1,-1)
            hPass   = h2A.ProjectionX("px_pass",1,-1)

        hTF         = hPass.Clone("hTF")
        hTF.Divide(hFail)
        self.tf     = hTF

    def applyTF(self):
        h2C         = self.regions["C"]
        self.h2EstD = h2C.Clone("esimatedD")
        self.h2EstD.Scale(self.tf)

    def outputEstimated(self,outputFile,hName,mode="RECREATE"):
        f = r.TFile.Open(outputFile,mode)
        f.cd()
        self.h2EstD.SetName(hName)
        self.h2EstD.Write()
        f.Close()

    def runABCD(self,tags):
        self.setABCD(tags)
        self.calculateTF()
        self.applyTF()

regions = ["TT","LL"]
bkgFiles    = ["results/templates/WP_0.8_0.9/2016/scaled/TTbar16.root"]
bkgSamples  = ["TTbar"]
pseudoFile  = "results/templates/WP_0.8_0.9/2016/scaled/pseudo16.root"
dataFile    = "results/templates/WP_0.8_0.9/2016/scaled/JetHT16.root"
#dataTag     = "data_obs"
dataTag     = "JetHT"
fileFlag    = False
for region in regions:
    if(fileFlag):
        mode="UPDATE"
    else:
        mode="RECREATE"
    objABCD = ABCD(bkgFiles,bkgSamples,dataFile,dataTag=dataTag)
    Atag    = "mJY_mJJ_SB_VRF_nom"
    Btag    = "mJY_mJJ_SB_VRP_nom".format(region)
    Ctag    = "mJY_mJJ_SB_AT_nom"
    Dtag    = "mJY_mJJ_SB_{0}_nom".format(region)
    objABCD.runABCD([Atag,Btag,Ctag,Dtag])
    objABCD.outputEstimated("QCD16_ABCD_SB_data.root","QCD_ABCD_{0}".format(region),mode)
    fileFlag=True