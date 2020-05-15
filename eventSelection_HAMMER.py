import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from HAMMER.Tools import CMS_lumi
from HAMMER.Tools.Common import *
from HAMMER.Analyzer import *

commonc = CommonCscripts()
customc = CustomCscripts()
a = analyzer('QCD_HT2000toInf.root')
out_vars = ['nFatJet','FatJet_pt']
a.GetActiveNode().Snapshot(out_vars,'ex3_out.root','mySnapshot',lazy=False,openOption='RECREATE')