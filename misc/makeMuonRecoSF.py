import ROOT as r
import numpy as np


p_bins = [50,100,150,200,300,400,600,1500,3500]
abseta_bins = [0,1.6,2.4]
sfs_2017 = [[0.9938,0.9950,0.996,0.996,0.994,1.003,0.987,0.9],[1.0,0.993,0.989,0.986,0.989,0.983,0.986,1.01]]
sfs_2018 = [[0.9943,0.9948,0.9950,0.994,0.9914,0.993,0.991,1.0],[1.0,0.993,0.990,0.988,0.981,0.983,0.978,0.98]]

sf_err_17 = [[0.0006,0.0007,0.001,0.001,0.001,0.006,0.003,0.1],[0,0.001,0.001,0.001,0.001,0.003,0.006,0.01]]
sf_err_18 = [[0.0007,0.0007,0.0009,0.001,0.0009,0.002,0.004,0.1],[0,0.001,0.001,0.001,0.002,0.003,0.006,0.03]]

p_bins = np.array(p_bins,dtype='float64')
abseta_bins = np.array(abseta_bins,dtype='float64')

h2_2017 = r.TH2F("reco_sf_17","Reco SF 2017;Muon p[GeV];|#eta|",len(abseta_bins)-1, abseta_bins, len(p_bins)-1, p_bins)
h2_2018 = r.TH2F("reco_sf_18","Reco SF 2018;Muon p[GeV];|#eta|", len(abseta_bins)-1, abseta_bins ,len(p_bins)-1, p_bins)
for abseta_bin in range(len(abseta_bins)-1):
    for p_bin in range(len(p_bins)-1):
        h2_2017.SetBinContent(abseta_bin+1,p_bin+1,sfs_2017[abseta_bin][p_bin])#bin counting starts from 1
        h2_2017.SetBinError(abseta_bin+1,p_bin+1,sf_err_17[abseta_bin][p_bin])

        h2_2018.SetBinContent(abseta_bin+1,p_bin+1,sfs_2018[abseta_bin][p_bin])
        h2_2018.SetBinError(abseta_bin+1,p_bin+1,sf_err_18[abseta_bin][p_bin])

f = r.TFile.Open("UL_17_18_Muon_RecoSF","RECREATE")
f.cd()
h2_2018.Write()
h2_2017.Write()
f.Close()