import ROOT as r
from array import array
import deltaRMatching as dr

sourceFile  = r.TFile("test.root","update")
sourceTree  = sourceFile.Get("Events")
matchHIndex = array('i',[0])
matchYIndex = array('i',[0])
matchHIndexBranch = sourceTree.Branch("matchHIndex",matchHIndex,"matchHIndex/I")
matchYIndexBranch = sourceTree.Branch("matchYIndex",matchYIndex,"matchYIndex/I")
print(sourceTree.GetEntriesFast())
for i,event in enumerate(sourceTree):
    if(i%100000==0):
        print(i)
    matchHIndex = dr.doHiggsMatching(event)
    matchYIndex = dr.doYMatching(event)

    matchHIndexBranch.Fill()
    matchYIndexBranch.Fill()

sourceTree.Write()
sourceFile.Close()