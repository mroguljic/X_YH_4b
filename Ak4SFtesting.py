import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

print("Compiling")
CompileCpp('TIMBER/Framework/src/AK4Btag_SF.cc')
print("Instantiating")
CompileCpp('AK4Btag_SF ak4SF = AK4Btag_SF(16, "DeepJet", "reshaping");')