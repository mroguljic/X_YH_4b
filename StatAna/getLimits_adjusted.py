#!/usr/bin/env python

import os, sys, re
import math, ROOT
import subprocess
import shutil

ROOT.gROOT.SetBatch() 

class GetLimits:

  def __init__(self, carddir, templates, combine_years):
    self.templates = templates
    self.carddir = carddir
    self.combine_years = combine_years

    print(self.templates)

    self.years = [re.search('20[0-9]*(?!.*20[0-9]*)', f).group() for f in self.templates]
    self.year_template = dict(zip(self.years, self.templates))

    self.MX = [1600]
    self.MY = [100]
    self.CAT = ['LL', 'TT']

  def make_card(self, year):

    rtfile = ROOT.TFile.Open(self.year_template[year], 'READ')

    w = ROOT.RooWorkspace('w', 'w')
    w.factory('mJY[60, 360]')
    w.factory('mJJ[1000, 3000]')
    w.var('mJY').setBins(15)
    w.var('mJJ').setBins(20)
    obs = ROOT.RooArgSet(w.var('mJY'), w.var('mJJ'))
    vars = ROOT.RooArgList(obs)

    with open('datacard.tpl') as f:
      datacard_template = f.read()

    for cat in self.CAT:
      hdata  = rtfile.Get('data_obs_mJY_mJJ_{}'.format(cat))
      hqcd   = rtfile.Get('QCD_mJY_mJJ_{}'.format(cat))
      httbar = rtfile.Get('TTbar_mJY_mJJ_{}'.format(cat))
      data_obs = ROOT.RooDataHist('data_obs_{}'.format(cat), 'data_obs_{}'.format(cat), vars, hdata)
      data_ttbar = ROOT.RooDataHist('TTbar_{}'.format(cat), 'TTbar_{}'.format(cat), vars, httbar)
      data_qcd = ROOT.RooDataHist('QCD_{}'.format(cat), 'QCD_{}'.format(cat), vars, hqcd)
      getattr(w, 'import')(data_obs)
      getattr(w, 'import')(data_ttbar)
      getattr(w, 'import')(data_qcd)
      for mx in self.MX:
        for my in self.MY: 
          if not rtfile.GetListOfKeys().Contains('MX{1}_MY{2}_mJY_mJJ_{0}'.format(cat, mx, my)):
            continue
          hsig = rtfile.Get('MX{1}_MY{2}_mJY_mJJ_{0}'.format(cat, mx, my))
          #hsig.Scale(0.01)
          data_sig = ROOT.RooDataHist('MX{0}_MY{1}_{2}'.format(mx, my, cat), 'MX{0}_MY{1}_{2}'.format(mx, my, cat), vars, hsig)
          getattr(w, 'import')(data_sig)

          datacard_name = 'datacard_{3}_MX{0}_MY{1}_{2}.txt'.format(mx, my, cat, year)
          shapesfile_name = "roohists_{0}.root".format(year)
          card = open(os.path.join(self.carddir, datacard_name), 'w')
          card_content = re.sub('TYPE',cat,datacard_template)
          card_content = re.sub('ROOTFILENAME', os.path.join(self.carddir, shapesfile_name),card_content)
          card_content = re.sub('CAT',cat,card_content)
          card_content = re.sub('MASSX',str(mx),card_content)
          card_content = re.sub('MASSY',str(my),card_content)
          card_content = re.sub('OBS' ,str(round(data_obs.sumEntries(),3)),card_content)
          card_content = re.sub('NSIG',str(round(data_sig.sumEntries(),3)),card_content)
          card_content = re.sub('NQCD',str(round(data_qcd.sumEntries(),3)),card_content)
          card_content = re.sub('NTT' ,str(round(data_ttbar.sumEntries(),3)),card_content)
          if cat == 'LL':
            card_content = re.sub('pnetSf             lnN    1.10/0.90                   -             1.10/0.90', 'pnetSf             lnN    0.90/1.10                   -             0.90/1.10', card_content)
          card.write(card_content)
          card.close()

    getattr(w, 'writeToFile', w)(os.path.join(self.carddir, shapesfile_name))

  def make_cards(self):
    for year in self.years:
      self.make_card(year) 

  def combine_cards(self):

    for year in self.years:

      for mx in self.MX:
        for my in self.MY: 

          w = ROOT.TFile(os.path.join(self.carddir, "roohists_{0}.root".format(year)), 'read').Get('w')
          if w.obj('MX{0}_MY{1}_{2}'.format(mx, my, 'LL')) == None:
            continue

          combcard_args = ['combineCards.py']
          for cat in self.CAT:
            card = 'datacard_{3}_MX{0}_MY{1}_{2}.txt'.format(mx, my, cat, year)
            combcard_args.append('{0}={1}'.format(cat, card))
          allcats = '_'.join(self.CAT)
          comb_card = 'datacard_{3}_MX{0}_MY{1}_{2}.txt'.format(mx, my, allcats, year)

          thisdir = os.path.abspath(os.getcwd())
          os.chdir(os.path.abspath(self.carddir))
          with open(comb_card, 'w') as out:
            subprocess.call(combcard_args, stdout=out)
          os.chdir(thisdir)

    if self.combine_years:

      for mx in self.MX:
        for my in self.MY: 
          if not os.path.isfile(os.path.join(self.carddir, 'datacard_2016_MX{0}_MY{1}_LL.txt'.format(mx, my))):
            continue
  
          combcard_args = ['combineCards.py']
          for year in self.years:
            card = 'datacard_{2}_MX{0}_MY{1}_LL_TT.txt'.format(mx, my, year)
            combcard_args.append('Y{0}={1}'.format(year, card))
          comb_card = 'datacard_2016_2017_2018_MX{0}_MY{1}_LL_TT.txt'.format(mx, my)

          thisdir = os.path.abspath(os.getcwd())
          os.chdir(os.path.abspath(self.carddir))
          with open(comb_card, 'w') as out:
            subprocess.call(combcard_args, stdout=out)
          os.chdir(thisdir)

  def run_limit(self, years):
    
    if isinstance(years, list):
      year = years[0]
      years = '_'.join(years)
    else:
      year = years

    for mx in self.MX:
      for my in self.MY: 

        w = ROOT.TFile(os.path.join(self.carddir, "roohists_{0}.root".format(year)), 'read').Get('w')
        if w.obj('MX{0}_MY{1}_{2}'.format(mx, my, 'LL')) == None:
          continue

        comb_cmd = ['combine']
        comb_cmd.append('-M AsymptoticLimits')
        comb_cmd.append('-m 125')
        comb_cmd.append('-n _{3}_MX{0}_MY{1}_{2}'.format(mx, my, 'LL_TT', years))
        comb_cmd.append('-d {}'.format(os.path.join(self.carddir, 'datacard_{3}_MX{0}_MY{1}_{2}.txt'.format(mx, my, 'LL_TT', years))))

        if not os.path.exists(os.path.abspath(os.path.join(self.carddir, 'AsymptoticLimits'))):
          os.mkdir(os.path.abspath(os.path.join(self.carddir, 'AsymptoticLimits')))
        print('>>>> Calculating limit for MX={0} MY={1} for year={2}'.format(mx, my, years))
        print(' '.join(comb_cmd))
        subprocess.call(' '.join(comb_cmd), shell=True)
        shutil.move('higgsCombine_{3}_MX{0}_MY{1}_{2}.AsymptoticLimits.mH125.root'.format(mx, my, 'LL_TT', years), os.path.abspath(os.path.join(self.carddir, 'AsymptoticLimits/higgsCombine_{3}_MX{0}_MY{1}_{2}.AsymptoticLimits.mH125.root'.format(mx, my, 'LL_TT', years))))

  def run_limits(self):

    map(self.run_limit, self.years)
    if self.combine_years:
      self.run_limit(self.years)




def main():

  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--dir', '-d', dest='dir', type=str,                     
            help='Directory to store datacards and workspaces')
  parser.add_argument('--files', '-f', dest='files', type=str, nargs='+',            
            help='List of input ROOT files')
  parser.add_argument('--make_cards', '-m', dest='make_cards', action='store_true', 
      help='If true, make cards from scratch')
  parser.add_argument('--combine_cards', '-c', dest='combine_cards', action='store_true', 
      help='If true, combine card from categories')
  parser.add_argument('--combine_year', '-y', dest='combine_year', action='store_true', 
      help='If true, combine limits for all years 2016-2018 ')
  parser.add_argument('--limits', '-l', dest='limits', action='store_true', 
      help='If true, calculate limits')
  args = parser.parse_args()

  getlims = GetLimits(args.dir, args.files, args.combine_year)
  if args.make_cards: 
    getlims.make_cards()
  if args.combine_cards: 
    getlims.combine_cards()
  if args.limits: 
    getlims.run_limits()

if __name__ == "__main__":
  main()
