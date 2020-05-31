# -*- coding: utf-8 -*-

"""Requiere las bibliotecas Python: requests, pdfminer, pandas; Módulo: descargabib.py

Informes de:

https://www.comunidad.madrid/servicios/salud/2019-nuevo-coronavirus#situacion-epidemiologica-actual
"""

import os.path as pth

from descargabib import descarga
import datetime as dt
import time
from glob import glob

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter #process_pdf
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from io import StringIO
import re
import pandas as pd

expnumber = re.compile(r'^ *(\d+(?: ?\. ?\d+)*)(?:[^\d/]|\s|\(|$|\.[^\d/]|\.\s|\.$)', re.M)

URL_TPL = 'https://www.comunidad.madrid/sites/default/files/doc/sanidad/{:02d}{:02d}{:02d}_cam_covid19.pdf'
FN_TPL = '{:02d}{:02d}{:02d}_cam_covid19.pdf'


def descargacam():
    today = dt.date.today()

    current = dt.date(2020, 4, 22)

    pdfdir = 'data/cam/'
    if pth.isdir(pdfdir):
        datadir = 'data/'
    else:
        pdfdir = ''
        datadir = ''

    while current <= today:
        fn = pdfdir + FN_TPL.format(current.year % 100, current.month, current.day)
        url = URL_TPL.format(current.year % 100, current.month, current.day)

        if not pth.exists(fn):
            descarga(url, fn, isbinary=True)
            time.sleep(1)

        current += dt.timedelta(1)

    csvfn = datadir + 'madrid-series.csv'
    df = pd.DataFrame()

    for fn in sorted(glob(pdfdir + '20*_cam_covid19.pdf')):
        base = pth.basename(fn)
        year = 2000 + int(base[:2])
        month = int(base[2:4])
        day = int(base[4:6])

        date = dt.datetime(year, month, day)

        print(fn)

        text = pdf_to_text(fn, pagenum=0)

        # A partir de aquí debe de ser cambiado si cambia el formato de los
        # informes de la Consejería
        numbers = [int(m.group(0).replace('.', '').replace(' ', ''))
                   for m in expnumber.finditer(text)]

        if date < dt.datetime(2020, 5, 13):
            hospitalizados = numbers[11]
            uci = numbers[12]
            fallecidos = numbers[15]
            recuperados = numbers[14]
            domicilio = numbers[13]
            if numbers[3] > 55000:
                hospitalizados_sin_uci_dia = numbers[6]
                uci_dia = numbers[7]
                pcr = numbers[3]
                casos = numbers[5]
                domicilio_dia = numbers[8]
                altas_dia = numbers[9]
                fallecidos_dia = numbers[10]
            else:
                hospitalizados_sin_uci_dia = numbers[3]
                pcr = numbers[8]
                uci_dia = numbers[4]
                casos = numbers[10]
                domicilio_dia = numbers[5]
                altas_dia = numbers[6]
                fallecidos_dia = numbers[7]

            muertos_hospitales = numbers[16]
            muertos_domicilios = numbers[17]
            muertos_centros = numbers[18]
            muertos_otros = numbers[19]
            muertos = numbers[20]
        else:
            # print(text)
            # print(len(numbers))
            # print(numbers)

            if len(numbers) not in [18, 20]:
                raise RuntimeError('Formato no contemplado')

            pcr = numbers[2]
            # antic = numbers[6]
            # casos = pcr + antic

            hospitalizados_sin_uci_dia = numbers[3]
            hospitalizados = numbers[4]

            if len(numbers) == 20:
                uci_dia = numbers[7]
                uci = numbers[8]

                fallecidos_dia = numbers[9]
                fallecidos = numbers[10]

                domicilio_dia = numbers[11]
                domicilio = numbers[12]

                muertos_centros = numbers[13]
                muertos_hospitales = numbers[14]
                muertos_domicilios = numbers[15]
                muertos_otros = numbers[16]
                muertos = numbers[17]

                altas_dia = numbers[18]
                recuperados = numbers[19]
            elif len(numbers) == 18:
                uci_dia = numbers[5]
                uci = numbers[6]

                fallecidos_dia = numbers[7]
                fallecidos = numbers[8]

                domicilio_dia = numbers[14]
                domicilio = numbers[15]

                muertos_centros = numbers[9]
                muertos_hospitales = numbers[10]
                muertos_domicilios = numbers[11]
                muertos_otros = numbers[12]
                muertos = numbers[13]

                altas_dia = numbers[16]
                recuperados = numbers[17]
            else:
                raise RuntimeError('Caso no contemplado')

        hospitalizados_dia = hospitalizados_sin_uci_dia + uci_dia

        df.loc[date, 'CASOS_PCR'] = pcr
        df.loc[date, 'Hospitalizados'] = hospitalizados
        df.loc[date, 'UCI'] = uci
        df.loc[date, 'Fallecidos'] = fallecidos
        df.loc[date, 'Recuperados'] = recuperados
        df.loc[date, 'domicilio'] = domicilio
        df.loc[date, 'uci_dia'] = uci_dia
        df.loc[date, 'hospitalizados_dia'] = hospitalizados_dia
        df.loc[date, 'domicilio_dia'] = domicilio_dia
        df.loc[date, 'altas_dia'] = altas_dia
        df.loc[date, 'fallecidos_dia'] = fallecidos_dia
        df.loc[date, 'muertos_hospitales'] = muertos_hospitales
        df.loc[date, 'muertos_domicilios'] = muertos_domicilios
        df.loc[date, 'muertos_centros'] = muertos_centros
        df.loc[date, 'muertos_otros'] = muertos_otros
        df.loc[date, 'muertos'] = muertos


    df = df.T.astype(int)

    df2 = df.T
    df2.index.name = 'Fecha'
    print('Escribiendo', csvfn)
    df2.to_csv(csvfn)

    print()
    print('ESTÁ ACTUALIZADO' if today == df.columns[-1].date() else
          '******************* NO ESTÁ ACTUALIZADO')
    print()


# Extract PDF text using PDFMiner. Adapted from
# http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library

def pdf_to_text(pdfname, pagenum=None):

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
            for i, page in enumerate(PDFPage.get_pages(fp)):
                if pagenum is None or pagenum == i:
                    interpreter.process_page(page)

        # Get text from StringIO
        text = sio.getvalue()
    finally:
        # Cleanup
        sio.close()
        if device is not None:
            device.close()

    return text


if __name__ == '__main__':
    descargacam()
