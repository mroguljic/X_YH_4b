import os

directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
if("semi" in os.getcwd()):
    semil      = True
    variations = ["nom","sfUp","sfDown","jesUp","jesDown","jerUp","jerDown"] #CR
else:
    semil      = False
    variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown","MJYrotUp","MJYrotDown"]
for d in directories:
    if("MX" in d):
        continue
    for variation in variations:
        if("MJYrot" in variation and not "TTbar" in d):
            continue
        if(semil):
            if(variation!="nom" and "Single" in d):
                continue
        else:
            if(variation!="nom" and not ("MX" in d or "TTbar" in d)):
                continue
        if("MX" in d):
            cmd = "mv {0}/{0}_0_{1}.root {0}_{1}.root".format(d,variation)
        else:
            cmd = "hadd -f {0}_{1}.root {0}/*{1}*root".format(d,variation)
        print(cmd)
        os.system(cmd)
