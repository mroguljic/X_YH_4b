import ROOT as r


for year in ["16","17","18"]:
    #files   = ["ST{0}.root".format(year),"WJets{0}.root".format(year),"TTbar{0}.root".format(year)]
    files   = ["ST{0}.root".format(year),"TTbar{0}.root".format(year)]
    outFile = "Other{0}.root".format(year)
    path    = "/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_semileptonic/muon/20{0}/scaled/".format(year)
    h_dict = {}
    for file in files:
        if("TTbar" in file):
            procs = ["TTbar_unmatched","TTbar_qq"]
        else:
            procs = [file.split(year)[0]]
        tempFile = r.TFile.Open(path+file)
        print(file, procs)
        for proc in procs:
            for key in tempFile.GetListOfKeys():
                h = key.ReadObj()
                hName = h.GetName()
                if(proc in hName):
                    h.SetDirectory(0)
                    hNewName = hName.replace(proc,"Other")
                    if not hNewName in h_dict:
                        h.SetName(hNewName)
                        h_dict[hNewName] = h
                    else:
                        h_dict[hNewName].Add(h)
        tempFile.Close()

    f = r.TFile.Open(path+outFile,"RECREATE")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()
    print(path+outFile+" created")


for year in ["16","17","18"]:
    files   = ["ST{0}.root".format(year),"TTbar{0}.root".format(year)]
    outFile = "Other{0}.root".format(year)
    path    = "/afs/cern.ch/work/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_semileptonic/electron/20{0}/scaled/".format(year)
    h_dict = {}
    for file in files:
        if("TTbar" in file):
            procs = ["TTbar_unmatched","TTbar_qq"]
        else:
            procs = [file.split(year)[0]]
        tempFile = r.TFile.Open(path+file)
        print(file, procs)
        for proc in procs:
            for key in tempFile.GetListOfKeys():
                h = key.ReadObj()
                hName = h.GetName()
                if(proc in hName):
                    h.SetDirectory(0)
                    hNewName = hName.replace(proc,"Other")
                    if not hNewName in h_dict:
                        h.SetName(hNewName)
                        h_dict[hNewName] = h
                    else:
                        h_dict[hNewName].Add(h)
        tempFile.Close()

    f = r.TFile.Open(path+outFile,"RECREATE")
    f.cd()
    for key in h_dict:
        histo = h_dict[key]
        histo.Write()
    f.Close()
    print(path+outFile+" created")


# for year in ["16"]:
#     file    = "TTbar{0}.root".format(year)
#     outFile = "Other{0}.root".format(year)
#     path    = "/afs/cern.ch/user/m/mrogulji/UL_X_YH/X_YH_4b/results/templates_hadronic/20{0}/scaled/".format(year)

#     h_dict = {}
#     procs = ["TTbar_unm","TTbar_qq"]
#     tempFile = r.TFile.Open(path+file)
#     for proc in procs:
#         for key in tempFile.GetListOfKeys():
#             h = key.ReadObj()
#             hName = h.GetName()
#             if(proc in hName):
#                 h.SetDirectory(0)
#                 hNewName = hName.replace("unm","Other")
#                 hNewName = hNewName.replace("qq","Other")
#                 if not hNewName in h_dict:
#                     h.SetName(hNewName)
#                     h_dict[hNewName] = h
#                 else:
#                     h_dict[hNewName].Add(h)
#     tempFile.Close()

#     f = r.TFile.Open(path+outFile,"RECREATE")
#     f.cd()
#     for key in h_dict:
#         histo = h_dict[key]
#         histo.Write()
#     f.Close()
#     print(path+outFile+" created")