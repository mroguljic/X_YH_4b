import ROOT
import time, os, re
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Tools.Common import *
from TIMBER.Analyzer import *
import sys
import subprocess
import json

if("2016" in sys.argv[1]):
    year = "2016"
elif("2017" in sys.argv[1]):
    year = "2017"
elif("2018" in sys.argv[1]):
    year = "2018"
else:
    "No year"
    sys.exit()

filename = 'skimInfo.json'
with open(filename, 'r') as f:
    data = json.load(f)

    with open(sys.argv[1], 'r') as config_file:
        config = json.load(config_file)
        for sample, sample_cfg in config.items():
            print(sample)
            das_query = "dasgoclient -query='file dataset={0} instance=prod/phys03'".format(sample_cfg["dataset"].split(",")[0])
            file     = subprocess.check_output(das_query, shell=True).split()[0].decode("utf-8")
            print(file)

            a = analyzer("root://cms-xrd-global.cern.ch//"+file)
            sumgenw = a.DataFrame.Sum("genWeight").GetValue()
            nEvt    = a.DataFrame.Count().GetValue()
            avgW    = sumgenw/nEvt

            data[year][sample]['avgW'] = avgW


os.remove(filename)
with open(filename, 'w') as f:
    json.dump(data, f, indent=4)