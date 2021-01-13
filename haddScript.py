import os

directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
variations = ["nom","jesUp","jesDown","jerUp","jerDown","jmsUp","jmsDown","jmrUp","jmrDown"]
for d in directories:
    for variation in variations:
        cmd = "hadd -f {0}_{1}.root {0}/*{1}*root".format(d,variation)
        print(cmd)
        os.system(cmd)
