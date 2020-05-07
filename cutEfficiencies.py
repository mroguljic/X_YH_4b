import ROOT as r
import matplotlib.pyplot as plt
from optparse import OptionParser



def getCutEfficienciesSig(filename,YmassPoint = "90"):
    f       = r.TFile.Open(filename)
    nTotal  = f.Get("total_Y{0}".format(YmassPoint)).GetEntriesFast()
    nPresel = f.Get("preselection_Y{0}".format(YmassPoint)).GetEntriesFast()
    nSel1   = f.Get("selection1_Y{0}".format(YmassPoint)).GetEntriesFast()
    nSel2   = f.Get("selection2_Y{0}".format(YmassPoint)).GetEntriesFast()

    print("File: {0} - YMass = {1}".format(filename,YmassPoint))
    print("Total: {0}, 1, 1".format(nTotal))
    print("Preselection: {0}, {1:.3f}, {2:.3f}".format(nPresel, nPresel/nTotal, nPresel/nTotal))
    print("Selection1: {0}, {1:.3f}, {2:.3f}".format(nSel1, nSel1/nTotal, nSel1/nPresel))
    print("Selection2: {0}, {1:.3f}, {2:.3f}".format(nSel2, nSel2/nTotal, nSel2/nSel1))

    return nTotal,nPresel,nSel1,nSel2

def getCutEfficienciesBkg(filename):
    f       = r.TFile.Open(filename)
    nTotal  = f.Get("total").GetEntriesFast()
    nPresel = f.Get("preselection").GetEntriesFast()
    nSel1   = f.Get("selection1").GetEntriesFast()
    nSel2   = f.Get("selection2").GetEntriesFast()

    print("File: {0}".format(filename))
    print("Total: {0}, 1, 1".format(nTotal))
    print("Preselection: {0}, {1:.3f}, {2:.3f}".format(nPresel, nPresel/nTotal, nPresel/nTotal))
    print("Selection1: {0}, {1:.3f}, {2:.3f}".format(nSel1, nSel1/nTotal, nSel1/nPresel))
    print("Selection2: {0}, {1:.3f}, {2:.3f}".format(nSel2, nSel2/nTotal, nSel2/nSel1))

    return nTotal,nPresel,nSel1,nSel2

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                    default   =   '',
                    dest      =   'input',
                    help      =   'A root file or text file with multiple root file locations to analyze')
    parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                    default   =   'output.root',
                    dest      =   'output',
                    help      =   'Output file name.')

    parser.add_option('-s',"--sig", action="store_true",  dest="isSignal")
    parser.add_option('-b',"--bkg", action="store_false", dest="isSignal")

    (options, args) = parser.parse_args()



    x = ["Total","Preselection","One jet all H","2nd jet loose"]
    #markers = ["o","v","^","*","H","X","D","<",">","d","x","s"] 
    #colors   = ["black","gray","r","sandybrown","olivedrab","dodgerblue","darkblue","gold","purple"] 
    if(options.isSignal):
        YmassPoints = ["90","100","125","150","200","250","300","400","500","600","700"]
        for i,point in enumerate(YmassPoints):
            outFile = options.output+"_Y_"+point+".png"
            #marker = markers[i%len(markers)]
            #color = colors[i%len(colors)]
            nTotal,nPresel,nSel1,nSel2 = getCutEfficienciesSig(options.input,YmassPoint=point)
            y = [nTotal/nTotal,nPresel/nTotal,nSel1/nPresel,nSel2/nSel1] #n-1 plot
            plt.scatter(x,y,label="Y_M = "+ point,s=90,alpha=1)

            plt.ylabel("Yield")
            plt.title("n-1 cuts efficiencies plot")
            plt.legend()
            plt.gca().yaxis.grid(True)
            plt.savefig(outFile)
            print("Saved output in "+outFile)
            plt.cla()
            plt.clf()


    else:
        outFile = options.output+".png"
        nTotal,nPresel,nSel1,nSel2 = getCutEfficienciesBkg(options.input)
        y = [nTotal/nTotal,nPresel/nTotal,nSel1/nPresel,nSel2/nSel1] #n-1 plot
        plt.scatter(x,y,label=options.input,s=90,alpha=1)

        plt.ylabel("Yield")
        plt.title("n-1 cuts efficiencies plot")
        plt.legend()
        plt.yscale('log')
        plt.gca().yaxis.grid(b=True, which='major', color='black', linestyle='-')
        plt.gca().yaxis.grid(b=True, which='minor', color='gray', linestyle='--',alpha=0.5)
        plt.savefig(outFile)
        print("Saved output in "+outFile)
        plt.cla()
        plt.clf()





