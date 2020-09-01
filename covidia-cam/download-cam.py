# -*- coding: utf-8 -*-

import os
import os.path as pth
import shutil
from descarga_cam import descargacam


# https://www.comunidad.madrid/servicios/salud/2019-nuevo-coronavirus#situacion-epidemiologica-actual


descargacam()
csvfn = 'data/madrid-series.csv'
dstfn = pth.join(r'C:\Users\alfonso\Downloads', pth.basename(csvfn))
if pth.isfile(dstfn):
    print('Removing file in Descargas')
    os.remove(dstfn)
    print()
csvfn2 = 'data/madrid-pcr.csv'
dstfn2 = pth.join(r'C:\Users\alfonso\Downloads', pth.basename(csvfn2))
if pth.isfile(dstfn2):
    print('Removing file in Descargas')
    os.remove(dstfn2)
    print()
print('Copying to Descargas')
shutil.copyfile(csvfn, dstfn)
shutil.copyfile(csvfn2, dstfn2)
print()
