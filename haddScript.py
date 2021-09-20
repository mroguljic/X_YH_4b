import os

directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
if("semilep" in os.getcwd().lower()):
    semil      = True
    semiRes    = False
    variations = ["nom","sfUp","sfDown","jesUp","jesDown","jerUp","jerDown"] #CR
elif("semiRes" in os.getcwd()):
    semil      = False
    semiRes    = True
    variations = [""]
else:
    semil      = False
    semiRes    = False
    variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown"]
for d in directories:
    for variation in variations:
        if(semil):
            if(variation!="nom" and ("Single" in d or "EGamma" in d)):
                continue
        elif(semiRes):
            if("MX" in d):
                cmd = "mv {0}/{0}_0.root {0}.root".format(d)
            else:
                cmd = "hadd -f {0}.root {0}/*root".format(d)
        else:
            if(variation!="nom" and not ("TTbar" in d or "MX" in d)):
                continue
            if("MX" in d):
                #cmd = "mv {0}/{0}_0_{1}.root {0}_{1}.root".format(d,variation)
                cmd = "cp {0}/{0}_0_{1}.root {0}_{1}.root".format(d,variation)
            else:
                cmd = "hadd -f {0}_{1}.root {0}/*{1}*root".format(d,variation)
        print(cmd)
        os.system(cmd)
