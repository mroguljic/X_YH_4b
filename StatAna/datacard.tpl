-------------------------------------------------------------------------------
imax 1 number of channels
jmax 2 number of backgrounds
kmax * number of nuisance parameters (sources of systematical uncertainties)
-------------------------------------------------------------------------------
shapes * * ROOTFILENAME w:$PROCESS_$CHANNEL w:$PROCESS_$CHANNEL_$SYSTEMATIC
bin                        CAT 
observation                OBS
-------------------------------------------------------------------------------
bin                        CAT                        CAT             CAT           
process                    MXMASSX_MYMASSY            QCD             TTbar
process                    0                          1               2             
rate                       NSIG                       NQCD            NTT           
-------------------------------------------------------------------------------
lumi               lnN    1.025                       -             1.025
purewt             lnN    1.03                        -             1.03
pdfrewt            lnN    0.990/1.010                 -             1.010
topxsec            lnN    -                           -             0.938/1.061    
pnetSf             lnN    1.10/0.90                   -             1.10/0.90      
higgstagmassJES    lnN    1.02                        1.02          1.02
qcdyield           lnN    -                           1.2           -
ttbaryield         lnN    -                           -             1.0
-------------------------------------------------------------------------------

