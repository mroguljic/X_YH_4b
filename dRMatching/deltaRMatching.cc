#include <TFile.h>
#include <TMath.h>
#include <stdio.h>
#include <vector>
#include "FastNanoAOD.h"
#include "FastNanoAOD.C"

UInt_t getHIdx(Int_t* GenPart_pdgId, UInt_t nGenPart);
UInt_t getYIdx(Int_t* GenPart_pdgId, UInt_t nGenPart);
std::vector<int> getBFromHIdxs(Int_t* GenPart_pdgId,Int_t* GenPart_genPartIdxMother, UInt_t nGenPart);
std::vector<int> getBFromYIdxs(Int_t* GenPart_pdgId,Int_t* GenPart_genPartIdxMother, UInt_t nGenPart);
Float_t deltaR(Float_t eta1, Float_t phi1, Float_t eta2, Float_t phi2);

void deltaRMatching(){

TFile*   f    = new TFile("../E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root","READ");
TTree*  tree = (TTree* )f->Get("Events");

FastNanoAOD reader = FastNanoAOD(tree);
Long64_t nEntries = reader.fChain->GetEntriesFast();

UInt_t   nFatJet, nGenPart;
Float_t  *FatJet_phi,*FatJet_eta,*GenPart_phi,*GenPart_eta;  
Int_t    *GenPart_pdgId,*GenPart_genPartIdxMother;


//replace i<10 with nEntries
for(int i=0;i<nEntries;i++){
    if(i%100000==0){
        cout<<i<<"\n";
    }
    reader.GetEntry(i);
    nFatJet = reader.nFatJet;
    nGenPart = reader.nGenPart;
    
    GenPart_pdgId               = reader.GenPart_pdgId;
    GenPart_genPartIdxMother    = reader.GenPart_genPartIdxMother;
    FatJet_phi                  = reader.FatJet_phi;
    FatJet_eta                  = reader.FatJet_eta;

    UInt_t HIdx                 = getHIdx(GenPart_pdgId,nGenPart);
    Float_t HEta                = reader.GenPart_eta[HIdx];
    Float_t HPhi                = reader.GenPart_phi[HIdx];

    UInt_t YIdx                 = getYIdx(GenPart_pdgId,nGenPart);
    Float_t YEta                = reader.GenPart_eta[YIdx];
    Float_t YPhi                = reader.GenPart_phi[YIdx];

    vector<int> BfromHIdxs      = getBFromHIdxs(GenPart_pdgId,GenPart_genPartIdxMother,nGenPart);
    Float_t b1_H_eta            = reader.GenPart_eta[BfromHIdxs[0]];
    Float_t b2_H_eta            = reader.GenPart_eta[BfromHIdxs[1]];
    Float_t b1_H_phi            = reader.GenPart_phi[BfromHIdxs[0]];
    Float_t b2_H_phi            = reader.GenPart_phi[BfromHIdxs[1]];
 
    vector<int> BfromYIdxs      = getBFromYIdxs(GenPart_pdgId,GenPart_genPartIdxMother,nGenPart);
    Float_t b1_Y_eta            = reader.GenPart_eta[BfromYIdxs[0]];
    Float_t b2_Y_eta            = reader.GenPart_eta[BfromYIdxs[1]];
    Float_t b1_Y_phi            = reader.GenPart_phi[BfromYIdxs[0]];
    Float_t b2_Y_phi            = reader.GenPart_phi[BfromYIdxs[1]];

    Int_t YFatJetMatchIdx       = -1;
    Int_t HFatJetMatchIdx       = -1;

    for(int fatJetIdx=0; fatJetIdx<nFatJet;fatJetIdx++){
    
        Float_t fatJetEta = FatJet_eta[fatJetIdx];
        Float_t fatJetPhi = FatJet_phi[fatJetIdx];

        Float_t deltaJetH   = deltaR(fatJetEta,fatJetPhi,HEta,HPhi);
        Float_t deltaJetHb1 = deltaR(fatJetEta,fatJetPhi,b1_H_eta,b1_H_phi);
        Float_t deltaJetHb2 = deltaR(fatJetEta,fatJetPhi,b2_H_eta,b2_H_phi);

        Float_t deltaJetY   = deltaR(fatJetEta,fatJetPhi,YEta,YPhi);
        Float_t deltaJetYb1 = deltaR(fatJetEta,fatJetPhi,b1_Y_eta,b1_Y_phi);
        Float_t deltaJetYb2 = deltaR(fatJetEta,fatJetPhi,b2_Y_eta,b2_Y_phi);

        if(deltaJetH<0.8 && deltaJetHb1<0.8 && deltaJetHb2<0.8){
            HFatJetMatchIdx = fatJetIdx;
        }
        if(deltaJetY<0.8 && deltaJetYb1<0.8 && deltaJetYb2<0.8){
            YFatJetMatchIdx = fatJetIdx;
        }

    }

    //cout<<YFatJetMatchIdx<<" "<<HFatJetMatchIdx<<"\n";


}
    
}

Float_t deltaR(Float_t eta1, Float_t phi1, Float_t eta2, Float_t phi2){
    Float_t deltaRSquare = (eta2-eta1)*(eta2-eta1)+(phi2-phi1)*(phi2-phi1);
    Float_t deltaR       = TMath::Sqrt(deltaRSquare);
    return deltaR;
}


UInt_t getHIdx(Int_t* GenPart_pdgId, UInt_t nGenPart){
//Returns the idx at which pdgId=25 (H)
    for(int i=0; i<nGenPart; ++i)
        if(GenPart_pdgId[i]==25)
            return i;

    cout<<"Warning: Couldn't find H\n";
    return -1;
}

UInt_t getYIdx(Int_t* GenPart_pdgId, UInt_t nGenPart){
//Returns the idx at which pdgId=25 (H)
    for(int i=0; i<nGenPart; ++i)
        if(GenPart_pdgId[i]==35)
            return i;

    cout<<"Warning: Couldn't find Y\n";
    return -1;
}

std::vector<int> getBFromHIdxs(Int_t* GenPart_pdgId,Int_t* GenPart_genPartIdxMother, UInt_t nGenPart){
//Returns the indices of 2 b quarks from H decay
    std::vector<int> bIdxs;

    for(int i=0; i<nGenPart; ++i){
        if(GenPart_pdgId[i]==5 || GenPart_pdgId[i]==-5){
            int motherIdx = GenPart_genPartIdxMother[i];
            //cout<<motherIdx<<" "<<GenPart_pdgId[motherIdx]<<"\n";
            if(GenPart_pdgId[motherIdx]==25){
                bIdxs.push_back(i);
            }
        }
        if(bIdxs.size()==2){
            return bIdxs;
        }
    }

    cout<<"Warning: Couldn't find bb from H\n";
    bIdxs = {-1,-1};
    return bIdxs;
}

std::vector<int> getBFromYIdxs(Int_t* GenPart_pdgId,Int_t* GenPart_genPartIdxMother, UInt_t nGenPart){
//Returns the indices of 2 b quarks from H decay
    std::vector<int> bIdxs;

    for(int i=0; i<nGenPart; ++i){
        if(GenPart_pdgId[i]==5 || GenPart_pdgId[i]==-5){
            int motherIdx = GenPart_genPartIdxMother[i];
            //cout<<motherIdx<<" "<<GenPart_pdgId[motherIdx]<<"\n";
            if(GenPart_pdgId[motherIdx]==35){
                bIdxs.push_back(i);
            }
        }
        if(bIdxs.size()==2){
            return bIdxs;
        }
    }

    cout<<"Warning: Couldn't find bb from Y\n";
    bIdxs = {-1,-1};
    return bIdxs;
}