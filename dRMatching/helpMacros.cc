#include <TFile.h>
#include <stdio.h>
#include "FastNanoAOD.h"
#include "FastNanoAOD.C"
#include <iostream>

Float_t getYMass(FastNanoAOD &reader, Int_t i){
    UInt_t   nFatJet, nGenPart;
    Float_t  *GenPart_mass;  
    Int_t    *GenPart_pdgId,*GenPart_genPartIdxMother;

    reader.GetEntry(i);

    nFatJet = reader.nFatJet;
    nGenPart = reader.nGenPart;
    GenPart_pdgId = reader.GenPart_pdgId;

    for(Int_t j=0; j<nGenPart; j++){
        if(GenPart_pdgId[j]==35){
            return reader.GenPart_mass[j];
        }
    }
    return -1.;
}

void testMacro(){

    TFile*  f    = new TFile("../E2FC3D3A-4D94-494D-BD56-524A28EF3C3F.root","READ");
    TTree*  tree = (TTree* )f->Get("Events");

    FastNanoAOD reader = FastNanoAOD(tree);
    Long64_t nEntries = reader.fChain->GetEntriesFast();




    //replace i<10 with nEntries
    for(Int_t i=0;i<100000;i++){
        Float_t YMass = getYMass(reader,i);
        std::cout<<YMass<<"\n";
    }

}