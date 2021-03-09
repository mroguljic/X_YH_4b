import os

directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown"]
#variations = ["nom","sfUp","sfDown","jesUp","jesDown","jerUp","jerDown"] #CR
for d in directories:
    for variation in variations:
        if("JetHT" in d and variation!="nom"):
            continue
        if("SingleMuon" in d and variation!="nom"):
            continue
        if("MX" in d):
            cmd = "cp {0}/{0}_0_{1}.root {0}_{1}.root".format(d,variation)
        else:
            cmd = "hadd -f {0}_{1}.root {0}/*{1}*root".format(d,variation)
        print(cmd)
        os.system(cmd)
