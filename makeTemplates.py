#To be used with trees from event selection
import ROOT as r
import time, os
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-y', '--year', metavar='year', type='string', action='store',
                default   =   '2016',
                dest      =   'year',
                help      =   'Dataset year')
parser.add_option('-p', '--process', metavar='PROCESS', type='string', action='store',
                default   =   'X1600_Y100',
                dest      =   'process',
                help      =   'Process in the given file')

(options, args) = parser.parse_args()
a = analyzer(options.input)
pnetHLo = 0.0
pnetHHi = 0.8
pnetYWp = 0.8
year    = options.year
histos=[]
if("data" in options.process.lower()):
    isData=True
else:
    isData=False

if not isData:
    triggerCorr = Correction('triggerCorrection',"TIMBER/Framework/src/EffLoader.cc",constructor=['"TIMBER/TIMBER/data/TriggerEffs/TriggerEffs.root"','"triggEff_{0}"'.format(year)],corrtype='weight')
    a.AddCorrection(triggerCorr, evalArgs=['mjjHY'])
a.MakeWeightCols()

a.Define("VRpass","pnetH>{0} && pnetH<{1} && pnetY>{2}".format(pnetHLo,pnetHHi,pnetYWp))#validation region
a.Define("VRfail","pnetH>{0} && pnetH<{1} && pnetY<{2}".format(pnetHLo,pnetHHi,pnetYWp))#validation region
a.Define("SRpass","pnetH>{0} && pnetY>{1}".format(pnetHHi,pnetYWp))#signal region
a.Define("SRfail","pnetH>{0} && pnetY<{1}".format(pnetHHi,pnetYWp))#signal region
checkpoint = a.GetActiveNode()

a.Cut("VRpassCut","VRpass==1")
h2DVRpass  = a.DataFrame.Histo2D(('{0}_pass_VR_mJY_mJJ'.format(options.process),';mJY [GeV];mJJ [GeV];',50,0,500,30,0.,3000.),"mjY","mjjHY","weight__nominal")
hMJVRpass  = a.DataFrame.Histo1D(('{0}_pass_VR_mJY'.format(options.process),';mJY [GeV];;',50,0,500),"mjY","weight__nominal")
hMJJVRpass = a.DataFrame.Histo1D(('{0}_pass_VR_mJJ'.format(options.process),';mJJ [GeV];;',30,0.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DVRpass,hMJVRpass,hMJJVRpass])

a.SetActiveNode(checkpoint)
a.Cut("VRfailCut","VRfail==1")
h2DVRfail  = a.DataFrame.Histo2D(('{0}_fail_VR_mJY_mJJ'.format(options.process),';mJY [GeV];mJJ [GeV];',50,0,500,30,0.,3000.),"mjY","mjjHY","weight__nominal")
hMJVRfail  = a.DataFrame.Histo1D(('{0}_fail_VR_mJY'.format(options.process),';mJY [GeV];;',50,0,500),"mjY","weight__nominal")
hMJJVRfail = a.DataFrame.Histo1D(('{0}_fail_VR_mJJ'.format(options.process),';mJJ [GeV];;',30,0.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DVRfail,hMJVRfail,hMJJVRfail])

a.SetActiveNode(checkpoint)
a.Cut("SRpassCut","SRpass==1")
h2DSRpass  = a.DataFrame.Histo2D(('{0}_pass_SR_mJY_mJJ'.format(options.process),';mJY [GeV];mJJ [GeV];',50,0,500,30,0.,3000.),"mjY","mjjHY","weight__nominal")
hMJSRpass  = a.DataFrame.Histo1D(('{0}_pass_SR_mJY'.format(options.process),';mJY [GeV];;',50,0,500),"mjY","weight__nominal")
hMJJSRpass = a.DataFrame.Histo1D(('{0}_pass_SR_mJJ'.format(options.process),';mJJ [GeV];;',30,0.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DSRpass,hMJSRpass,hMJJSRpass])

a.SetActiveNode(checkpoint)
a.Cut("SRfailCut","SRfail==1")
h2DSRfail  = a.DataFrame.Histo2D(('{0}_fail_SR_mJY_mJJ'.format(options.process),';mJY [GeV];mJJ [GeV];',50,0,500,30,0.,3000.),"mjY","mjjHY","weight__nominal")
hMJSRfail  = a.DataFrame.Histo1D(('{0}_fail_SR_mJY'.format(options.process),';mJY [GeV];;',50,0,500),"mjY","weight__nominal")
hMJJSRfail = a.DataFrame.Histo1D(('{0}_fail_SR_mJJ'.format(options.process),';mJJ [GeV];;',30,0.,3000.),"mjjHY","weight__nominal")
histos.extend([h2DSRfail,hMJSRfail,hMJJSRfail])


out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()
for h in histos:
    h.Write()
out_f.Close()
