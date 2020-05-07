# -*- coding: utf-8 -*-

# Requiere: requests, pdfminer, pandas
#
# Informes de:
#
# https://www.comunidad.madrid/servicios/salud/2019-nuevo-coronavirus#situacion-epidemiologica-actual


import os
import os.path as pth
import datetime as dt
import time
from glob import glob
from collections import OrderedDict
from shutil import copyfile
from io import StringIO
import re
import requests
import pandas as pd


# ALWAYS_UPDATE = False
ALWAYS_UPDATE = True

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter #process_pdf
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams


expnumber = re.compile(r'^ *\d+(?:\.\d+)*(?:$|\s)', re.M)


URL_TPL = 'https://www.comunidad.madrid/sites/default/files/doc/sanidad/{:02d}{:02d}{:02d}_cam_covid19.pdf'
FN_TPL = '{:02d}{:02d}{:02d}_cam_covid19.pdf'


def main():
    today = dt.date.today()

    current = dt.date(2020, 4, 22)

    while current <= today:
        fn = pth.join(FN_TPL.format(current.year % 100, current.month, current.day))
        url = URL_TPL.format(current.year % 100, current.month, current.day)

        if not pth.exists(fn):
            download(url, fn, isbinary=True)
            time.sleep(1)

        current += dt.timedelta(1)

    csvfn = 'madrid-series.csv'
    excelfn = 'madrid-series.xlsx'

    df = pd.DataFrame()

    for fn in sorted(glob('20*_cam_covid19.pdf')):
        base = pth.basename(fn)
        year = 2000 + int(base[:2])
        month = int(base[2:4])
        day = int(base[4:6])

        date = dt.datetime(year, month, day)

        print(fn)

        text = pdf_to_text(fn)

        numbers = [int(m.group().strip().replace('.', ''))
                   for m in expnumber.finditer(text)]

        # print(len(numbers))
        # print(numbers)
        # print(text)

        if len(numbers) != 21:
            raise RuntimeError('Formato no contemplado')

        hospitalizados = numbers[11]
        uci = numbers[12]
        fallecidos = numbers[15]
        recuperados = numbers[14]
        domicilio = numbers[13]
        if numbers[3] > 55000:  # a veces cambia el orden que lee pdfminer
            hospitalizados_sin_uci_dia = numbers[6]
            uci_dia = numbers[7]
            casos = numbers[5]
            uci_dia = uci_dia
            hospitalizados_dia = hospitalizados_sin_uci_dia + uci_dia
            domicilio_dia = numbers[8]
            altas_dia = numbers[9]
            fallecidos_dia = numbers[10]
        else:
            hospitalizados_sin_uci_dia = numbers[3]
            uci_dia = numbers[4]
            casos = numbers[10]
            hospitalizados_dia = hospitalizados_sin_uci_dia + uci_dia
            domicilio_dia = numbers[5]
            altas_dia = numbers[6]
            fallecidos_dia = numbers[7]

        df.loc[date, 'CASOS'] = casos
        df.loc[date, 'Hospitalizados'] = hospitalizados
        df.loc[date, 'UCI'] = uci
        df.loc[date, 'Fallecidos'] = fallecidos
        df.loc[date, 'Recuperados'] = recuperados
        df.loc[date, 'domicilio'] = domicilio
        df.loc[date, 'uci_dia'] = uci_dia
        df.loc[date, 'hospitalizados_dia'] = hospitalizados_sin_uci_dia + uci_dia
        df.loc[date, 'domicilio_dia'] = domicilio_dia
        df.loc[date, 'altas_dia'] = altas_dia

        df.loc[date, 'fallecidos_dia'] = fallecidos_dia
        df.loc[date, 'muertos_hospitales'] = numbers[16]
        df.loc[date, 'muertos_domicilios'] = numbers[17]
        df.loc[date, 'muertos_centros'] = numbers[18]
        df.loc[date, 'muertos_otros'] = numbers[19]
        df.loc[date, 'muertos'] = numbers[20]


    df = df.T

    print('Writing', excelfn)
    with pd.ExcelWriter(excelfn) as writer:
        df.to_excel(writer)

    print('Writing', csvfn)
    df.to_csv(csvfn)

    print()
    print('ESTÁ ACTUALIZADO' if today == df.columns[-1].date() else
          '******************* NO ESTÁ ACTUALIZADO')
    print()


# Extract PDF text using PDFMiner. Adapted from
# http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library

def pdf_to_text(pdfname):

    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    laparams = LAParams()
    device = None
    try:
        device = TextConverter(rsrcmgr, sio, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Extract text
        with open(pdfname, 'rb') as fp:
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)

        # Get text from StringIO
        text = sio.getvalue()
    finally:
        # Cleanup
        sio.close()
        if device is not None:
            device.close()

    return text


def download(url, fn, isbinary=False, isascii=False, isbackup=False,
             prevpage=None):
    today = dt.date.today()

    ret = True

    if pth.isfile(fn):
        modifiedTime = pth.getmtime(fn)
        changed = dt.datetime.fromtimestamp(modifiedTime).date()

        if isbackup:
            basename = pth.basename(fn)
            rootfn, ext = pth.splitext(basename)
            dirname = pth.dirname(fn)
            changedstr = str(changed)

            backupfn = pth.join(dirname, 'backup',
                                rootfn + '-' + changedstr + ext)
            print('Backup: {} -> {}'.format(fn, backupfn))
            copyfile(fn, backupfn)


    if not pth.isfile(fn) or changed != today or ALWAYS_UPDATE:
        print('Downloading:', url)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        with requests.Session() as s:
            if prevpage:
                s.get(prevpage, headers=headers)
            r = s.get(url, headers=headers)
        if r.status_code == requests.codes.ok:
            if isbinary:
                with open(fn, 'wb') as fp:
                    fp.write(r.content)
            elif isascii:
                content = r.content
                text = r.content.decode('ascii', 'ignore')
                with open(fn, 'w', encoding='utf-8') as fp:
                    fp.write(text)
            else:
                with open(fn, 'w', encoding='utf-8') as fp:
                    fp.write(r.text)
        else:
            print('ERROR', r.status_code, 'when downloading:', fn)
            ret = False

    return ret


main()
