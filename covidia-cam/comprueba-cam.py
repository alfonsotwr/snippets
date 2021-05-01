# -*- coding: utf-8 -*-


"""Dibuja todas las series del repositorio. Necesita pandas y matplotlib
"""


import pandas as pd
import matplotlib.pyplot as plt
import os.path as pth


pdfdir = 'data/cam/'
if pth.isdir(pdfdir):
    datadir = 'data/'
else:
    pdfdir = ''
    datadir = ''


data = pd.read_csv(f'{datadir}madrid-series.csv', parse_dates=True,
                   index_col=0)

pcr = pd.read_csv(f'{datadir}madrid-pcr.csv', parse_dates=True, index_col=0,
                  squeeze=True)


with plt.rc_context({'axes.labelsize': 'small',    # medium
                     'xtick.labelsize': 'small',
                     'ytick.labelsize': 'small'}):

    fig, axs = plt.subplots(5, figsize=(12, 6.7), sharex=True)
    fig.subplots_adjust(top=0.98, bottom=0.045, left=0.06, right=0.98,
                        hspace=0.1, wspace=0.2)

    for i in range(4):
        ax = axs.flat[i]
        df = data.iloc[:, i * 4: (i + 1) * 4]
        df /= df.max()
        for x in df:
            ax.plot(df[x], label=x)
        ax.legend(loc='center left')

    ax = axs.flat[4]
    ax.plot(pcr, label=pcr.name)
    ax.legend(loc='center left')


plt.show()
