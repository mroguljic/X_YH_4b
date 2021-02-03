import ROOT

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *

CompileCpp('TIMBER/Framework/src/JMSUncShifter.cc')
CompileCpp('JMSUncShifter jmsShifter = JMSUncShifter();')

a = analyzer("nano_9.root")

small_rdf = a.GetActiveNode().DataFrame.Range(100)
small_node = Node('small',small_rdf)
a.SetActiveNode(small_node)
a.Cut("nFatJet","nFatJet>1")

a.Define("mSDdown",'jmsShifter.shiftMsd(FatJet_msoftdrop[0],"2016",1)') #nom,down,up
a.Define("mSD",'FatJet_msoftdrop[0]') #nom,down,up
a.Define("mSDUp",'jmsShifter.shiftMsd(FatJet_msoftdrop[0],"2016",2)') #nom,down,up

snapshotColumns = ["mSDdown"]
opts = ROOT.RDF.RSnapshotOptions()
opts.fMode = "RECREATE"
a.GetActiveNode().DataFrame.Snapshot("Events","test.root",["mSDdown","mSDUp","mSD"],opts)