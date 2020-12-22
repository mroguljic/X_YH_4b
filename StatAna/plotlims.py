#!/usr/bin/env python

import os, sys
import uproot4 as rt
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import pandas as pd
import matplotlib
from matplotlib import colors as mcolors

matplotlib.use('qt4agg')

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

np.set_printoptions(threshold=np.inf)
pd.set_option("display.max_rows", None, "display.max_columns", None)

def plot():
  pass

def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--dir', '-d', dest='dir', type=str,
      help='directory where limit ROOT files are located')
  parser.add_argument('--mx', '-x', dest='mx', type=int, nargs='+',
      help='comma-separated list of MX values to plot')
  parser.add_argument('--my', '-y', dest='my', type=int, nargs='+',
      help='comma-separated list of MY values to plot')
  parser.add_argument('--all_years', '-Y', dest='all_years', action='store_true',
      help='Plot expected limits for all years together')
  args = parser.parse_args()

  years = [2016, 2017, 2018]

  fnames = [(int(year), mx, my, os.path.join(args.dir,f'higgsCombine_{year}_MX{mx}_MY{my}_LL_TT.AsymptoticLimits.mH125.root'))
      for year in years for mx in args.mx for my in args.my]
  all_years = '_'.join(str(year) for year in years)

  fnames += [(all_years, mx, my, os.path.join(args.dir,f'higgsCombine_{all_years}_MX{mx}_MY{my}_LL_TT.AsymptoticLimits.mH125.root')) for mx in args.mx for my in args.my]

  #print(f'fnames ={fnames}')

  fin = [(f[0], f[1], f[2], f[3]) for f in fnames if os.path.exists(f[3])]

  #print(f'fin = {fin}')

  lims =  pd.DataFrame(
      [
        np.array([f[0], f[1], f[2]] + np.array(rt.open(f[3]+':limit/limit'), dtype=float).tolist()) 
        for f in fin]
      ,columns=['Year', 'MX[GeV]', 'MY[GeV]', 'Exp-2sig[fb]', 'Exp-1sig[fb]', 'Exp[fb]', 'Exp+1sig[fb]', 'Exp+2sig[fb]', 'Obs[fb]']
      )

  lims.iloc[:, 1:] = lims.iloc[:, 1:].apply(pd.to_numeric)
  lims.iloc[:, 3:] = lims.iloc[:, 3:]*10
  #lims = lims.dropna()

  #print(f'lims = {lims}')

  plt.style.use(hep.style.CMS)
  hep.cms.label(loc=1, year='137 $fb^{-1}$', paper=True, llabel='Simulation WiP')

  plt.xlabel("$M_{X} [GeV]$")
  plt.ylabel(r'$\sigma(pp \rightarrow X \rightarrow HY \rightarrow b\overline{b} b \overline{b})\,[fb]$')
  
  plt.yscale('log')
  #plt.ylim(0.01, 1000)
  plt.ylim(0.05, 5000)

  cols = ['brown', 'darkorange', 'sienna', 'crimson', 'darkolivegreen', 'forestgreen', 'darkslategray', 'steelblue', 'rebeccapurple', 'darkmagenta']
  
  year = all_years
  for my in args.my:
    mx = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==my)]['MX[GeV]'].tolist()
    exp = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==my)]['Exp[fb]'].tolist()
    exp1down = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==my)]['Exp-1sig[fb]'].tolist()
    exp1up = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==my)]['Exp+1sig[fb]'].tolist()
    exp2down = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==my)]['Exp-2sig[fb]'].tolist()
    exp2up = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==my)]['Exp+2sig[fb]'].tolist()

    plt.plot(mx, exp, color=colors[cols[args.my.index(my)]], linewidth='2.4', label=r'$M_Y = {}$'.format(my))
    #plt.fill_between(mx, exp1down, exp1up, color='forestgreen', label='68% expected')
    #plt.fill_between(mx, exp2down, exp2up, color='darkorange', label='95% expected')
    #plt.fill_between(mx, exp1down, exp1up, color='forestgreen', label='_nolegend_')
    #plt.plot(mx, exp, color='black', linewidth='2.4', linestyle='--', label=r'Median expected')
  
  #plt.text(800, 100, r'$M_{Y} = 125\,GeV$')
  plt.legend(loc="upper right"
      , title='95% CL upper limits'
      +'\n(median expected)'
      ,ncol=2
      #,ncol=1
      ,title_fontsize=20
      ,fontsize=20
      )
  
  plt.tight_layout()

  fig = matplotlib.pyplot.gcf()
  fig.set_size_inches(4*2.5, 3*2.5, forward=True)
  
  fig.savefig('Cards_10Nov2020/explim_MX_variousMYs.pdf')
  fig.savefig('Cards_10Nov2020/explim_MX_variousMYs.png')
  #fig.savefig('Cards_10Nov2020/explim_MX_MY125.pdf')
  #fig.savefig('Cards_10Nov2020/explim_MX_MY125.png')

  #mx = [int(x) for x in lims.loc[lims['Year']==year]['MX[GeV]'].unique().tolist()]
  #my = [int(x) for x in lims.loc[lims['Year']==year]['MY[GeV]'].unique().tolist()]
  #lim_exp = lims.loc[(lims['Year']==year)].reset_index().pivot('MX[GeV]', 'MY[GeV]', 'Exp[fb]').to_numpy(dtype=float)
  #print(lims.loc[(lims['Year']==year)].reset_index().pivot('MX[GeV]', 'MY[GeV]', 'Exp[fb]'))


  #im = plt.imshow(lim_exp)
  #plt.axis.set_xticks(np.arange(len(my)))
  #plt.axis.set_yticks(np.arange(len(mx)))

  ##im.ax.set_xticklabels(my)
  ##im.ax.set_yticklabels(mx)

  #cbar = im.ax.figure.colorbar(im, ax=ax)
  ##cbar.ax.set_ylabel(r'Median expected$\,[GeV]$', rotation=-90)

  ##plt.xlabel(r'$M_{Y}\,[GeV]$')
  ##plt.ylabel(r'$M_{X}\,[GeV]$')
  ##im = plt.imshow(lim_exp, extent=(my[0], my[-1], mx[0]-50, mx[-1]+50), interpolation='nearest', aspect = 'auto', origin='lower', norm=mcolors.LogNorm(vmin=0.01, vmax=1000))

  ##cbar = plt.colorbar(im, label=r'Median expected$\,[fb]$')
  ###cbar.ax.set_yticklabels(rotation=90)
  ##plt.clim(0.05, 1000);
  #plt.tight_layout()

  #plt.show()

  #return

  lumi_year = {
      '2016': '35.9',
      '2017': '41.5', 
      '2018': '59.2',
      '2016+2017+2018': '137'
      }

  hep.cms.label(loc=1, year='', paper=True, llabel='Simulation WiP')
  if args.all_years:
    all_years = lims.loc[:,'Year'].unique()
    print(all_years)
    for year in all_years:
      medianexp_by_year = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==125)]['Exp[fb]'].tolist()  
      mx_by_year = lims.loc[(lims['Year']==year) & (lims['MY[GeV]']==125)]['MX[GeV]'].tolist()  
      if isinstance(year, str):
        yr = year.replace('_', '+')
      elif isinstance(year, float):
        yr = str(int(year))
      yr = ''.join([yr, '(', lumi_year[yr], r'$\,fb^{-1}$', ')'])
      plt.plot(mx_by_year, medianexp_by_year, linewidth='2.4', linestyle='--', label=yr)
    plt.text(800, 100, r'$M_{Y} = 125\,GeV$')
    plt.legend(loc="upper right"
        , title='95% CL upper limits'
        +'\n'+'Median expected'
        #,ncol=2
        ,ncol=1
        ,title_fontsize=20
        ,fontsize=20
        )
    plt.tight_layout()
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(4*2.5, 3*2.5, forward=True)
    
    fig.savefig('Cards_10Nov2020/explim_ByYear_MX_MY125.pdf')
    fig.savefig('Cards_10Nov2020/explim_ByYear_MX_MY125.png')



if __name__ == "__main__":
  main()
