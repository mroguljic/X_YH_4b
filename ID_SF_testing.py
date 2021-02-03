import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

print("Compiling")
CompileCpp('TIMBER/Framework/src/TH2_SF.cc')
print("Instantiating")
CompileCpp('TH2_SF idSF = TH2_SF("TIMBER/TIMBER/data/OfficialSFs/Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root","NUM_TightID_DEN_TrackerMuons_abseta_pt_efficiencyData"); \n RVec<float>sf = idSF.eval(50.0,1.4);')