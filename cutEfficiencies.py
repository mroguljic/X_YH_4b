import ROOT as r
import matplotlib.pyplot as plt



def getCutEfficienciesSig(filename="wp_0.7.root",YmassPoint = "90"):
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

def getCutEfficienciesBkg(filename="QCD_1000to1500_wp_0.7.root"):
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


#YmassPoints = ["90","100","125","150","200","250","300","400","500","600","700"]
YmassPoints = ["90","125","150","200","300","500","700"]

x = ["Total","Preselection","One jet all H","2nd jet loose"]
#markers = ["o","v","^","*","H","X","D","<",">","d","x","s"] 
#colors   = ["black","gray","r","sandybrown","olivedrab","dodgerblue","darkblue","gold","purple"] 

for i,point in enumerate(YmassPoints):
    #marker = markers[i%len(markers)]
    #color = colors[i%len(colors)]
    nTotal,nPresel,nSel1,nSel2 = getCutEfficienciesSig("signal_wp_0.7.root",YmassPoint=point)
    y = [nTotal/nTotal,nPresel/nTotal,nSel1/nPresel,nSel2/nSel1] #n-1 plot
    plt.scatter(x,y,label="Y_M = "+ point,s=90,alpha=1)

    plt.ylabel("Yield")
    plt.title("n-1 cuts efficiencies plot")
    plt.legend()
    plt.gca().yaxis.grid(True)
    plt.savefig("Y_"+point+".png")
    plt.cla()
    plt.clf()



nTotal,nPresel,nSel1,nSel2 = getCutEfficienciesBkg("QCD_1000to1500_wp_0.7.root")
y = [nTotal/nTotal,nPresel/nTotal,nSel1/nPresel,nSel2/nSel1] #n-1 plot
plt.scatter(x,y,label="QCD_HT_1000to1500",s=90,alpha=1)

plt.ylabel("Yield")
plt.title("n-1 cuts efficiencies plot")
plt.legend()
plt.yscale('log')
plt.gca().yaxis.grid(b=True, which='major', color='black', linestyle='-')
plt.gca().yaxis.grid(b=True, which='minor', color='gray', linestyle='--',alpha=0.5)
plt.savefig("QCD_1000to1500.png")
plt.cla()
plt.clf()





