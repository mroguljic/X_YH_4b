import os

#for year in ["16","17","18","RunII"]:
for year in ["17","18"]:
	for region in ["L","T"]:
		combineCmd 	= "combine -M FitDiagnostics CR_{0}_{1}.txt --saveNormalization --saveShapes --saveWithUncertainties".format(region,year)
		mvCmd 		= "mv fitDiagnostics.root fitDiagnostics_{0}_{1}.root".format(region,year)
		print(combineCmd)
		os.system(combineCmd)
		print(mvCmd)
		os.system(mvCmd)