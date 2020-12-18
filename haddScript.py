import os

directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
for d in directories:
    cmd = "hadd -f {0}.root {0}/*root".format(d)
    print(cmd)
