# -*- coding: utf-8 -*-

"""Requiere las bibliotecas Python: requests, pdfminer.six, pandas; Módulo: descargabib.py  # noqa: E501

Informes de:

https://www.comunidad.madrid/servicios/salud/coronavirus#datos-situacion-actual
"""

import os.path as pth
import datetime as dt
import time
from glob import glob
import re
import pandas as pd

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

from pathlib import Path
Path("my/directory").mkdir(parents=True, exist_ok=True)

from descargabib import descarga

expnumber = re.compile(r'^ *(\d+(?: ?\. ?\d+)*)(?:[^\d/]|\s|\(|$|\.[^\d/]|\.\s|\.$)', re.M)  # noqa: E501

expfecha = re.compile(r'(\d\d)/(\d\d)/(\d\d\d\d)')
expacum = re.compile(r'\n(1|2) \n(5|6|7|8) \n(9|10|11|12|13) \n[\d \n]+(/)?')
expnumber2 = re.compile(r'\d\d\d\d\d+')

exppoint = re.compile(r'(?<=\d)\.(?=\d)')


URL_TPL = 'https://www.comunidad.madrid/sites/default/files/doc/sanidad/{:02d}{:02d}{:02d}_cam_covid19.pdf'  # noqa: E501
FN_TPL = '{:02d}{:02d}{:02d}_cam_covid19.pdf'



def descargacam():
    today = dt.date.today()

    current = dt.date(2020, 4, 22)

    pdfdir = 'data/'
    datadir = ''

    try:
       Path(pdfdir).mkdir(parents=True, exist_ok=True)
    except:
	print(f"No puedo crear directorio para PDFs {pdfdir}")


    while current <= today:
        # Durante un periodo no se publicó el informe en fines de semana
        if (dt.date(2020, 7, 1) < current < dt.date(2020, 10, 28) and
                current.weekday() in [5, 6]):
            current += dt.timedelta(1)
            continue

        # Días sin informe
        if current in [dt.date(2020, 10, 12),
                       dt.date(2020, 12, 25),
                       dt.date(2021, 1, 1),
                       dt.date(2021, 1, 6)]:
            current += dt.timedelta(1)
            continue

        fn = pdfdir + FN_TPL.format(current.year % 100, current.month,
                                    current.day)
        url = URL_TPL.format(current.year % 100, current.month, current.day)

        if not pth.exists(fn):
            ret = descarga(url, fn, isbinary=True)
            time.sleep(1)
            if not ret:
                changed = False
                if current == dt.date(2020, 8, 3):  # casos especiales
                    url = url.replace('03_', '03')
                    changed = True
                elif current == dt.date(2020, 8, 14):  # casos especiales
                    url = url.replace('/20', '/2020')
                    changed = True
                elif current == dt.date(2020, 9, 2):  # casos especiales
                    url = url.replace('/doc/sanidad', '')
                    changed = True
                elif current == dt.date(2020, 11, 4):  # casos especiales
                    url = url.replace('/doc/', '/aud/')
                    changed = True
                elif current == dt.date(2020, 12, 3):  # casos especiales
                    url = url.replace('201203_cam_covid19', '3.12.2020_2')
                    changed = True
                elif current == dt.date(2020, 12, 6):  # casos especiales
                    url = url.replace('201206_cam_covid19', '6.12.2020')
                    changed = True
                elif current == dt.date(2020, 12, 8):  # casos especiales
                    url = url.replace('/doc/sanidad/', '/aud/empleo/')
                    changed = True
                elif current == dt.date(2021, 3, 8):  # casos especiales
                    url = url.replace('/210308', '/2103008')
                    changed = True
                elif current == dt.date(2021, 3, 24):  # casos especiales
                    url = url.replace('/doc/sanidad/', '/doc/sanidad/rrhh/')
                    changed = True
                elif current == dt.date(2021, 4, 1):  # casos especiales
                    url = url.replace('/doc/', '/aud/')
                    changed = True
                elif current == dt.date(2021, 4, 22):  # casos especiales
                    url = url.replace('/doc/', '/aud/')
                    changed = True
                elif current == dt.date(2021, 4, 27):  # casos especiales
                    url = url.replace('.pdf', '.pdf.pdf')
                    changed = True
                elif current == dt.date(2021, 4, 28):  # casos especiales
                    url = url.replace('/doc/', '/aud/')
                    changed = True
                elif current == dt.date(2021, 5, 10):  # casos especiales
                    url = url.replace('cam_covid19', 'cam_covid')
                    changed = True    

                if changed:
                    descarga(url, fn, isbinary=True)
                    time.sleep(1)

        current += dt.timedelta(1)

    csvfn = datadir + 'madrid-series.csv'
    df = pd.DataFrame()

    for fn in sorted(glob(pdfdir + '2*_cam_covid19.pdf')):
        datefn = getdatefn(fn)

        fn1 = fn.replace('.pdf', '_1.txt')
        fn2 = fn.replace('.pdf', '_2.txt')
        fn3 = fn.replace('.pdf', '_3.txt')
        fn4 = fn.replace('.pdf', '_4.txt')
        fn5 = fn.replace('.pdf', '_5.txt')
        pagebase = 0
        if datefn >= dt.datetime(2021, 3, 1):
            pagebase += 1
        if not pth.isfile(fn1):
            print('Guardando:', fn1)
            page1 = pdf_to_text(fn, pagenum=pagebase)
            with open(fn1, 'w', encoding='utf-8') as fp:
                fp.write(page1)
        if not pth.isfile(fn2):
            print('Guardando:', fn2)
            page2 = pdf_to_text(fn, pagenum=pagebase + 1)
            with open(fn2, 'w', encoding='utf-8') as fp:
                fp.write(page2)
        if not pth.isfile(fn3):
            print('Guardando:', fn3)
            page3 = pdf_to_text(fn, pagenum=pagebase + 2)
            with open(fn3, 'w', encoding='utf-8') as fp:
                fp.write(page3)
        if not pth.isfile(fn4) and datefn >= dt.datetime(2020, 12, 22):
            print('Guardando:', fn4)
            page4 = pdf_to_text(fn, pagenum=pagebase + 3)
            with open(fn4, 'w', encoding='utf-8') as fp:
                fp.write(page4)
        if not pth.isfile(fn5) and datefn >= dt.datetime(2021, 4, 15):
            print('Guardando:', fn5)
            page5 = pdf_to_text(fn, pagenum=pagebase + 4)
            with open(fn5, 'w', encoding='utf-8') as fp:
                fp.write(page5)

    for fn in sorted(glob(pdfdir + '2*_cam_covid19_1.txt')):
        print(fn)
        date = getdatefn(fn)

        # if date > dt.datetime(2020, 7, 13):
        #     break

        with open(fn, encoding='utf-8') as fp:
            text = fp.read()

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
                # casos = numbers[5]
                domicilio_dia = numbers[8]
                altas_dia = numbers[9]
                fallecidos_dia = numbers[10]
            else:
                hospitalizados_sin_uci_dia = numbers[3]
                pcr = numbers[8]
                uci_dia = numbers[4]
                # casos = numbers[10]
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
            if date < dt.datetime(2020, 5, 20):
                fmt = 0
            elif date < dt.datetime(2020, 12, 10):
                assert len(numbers) == 18, 'Formato no contemplado'
                if numbers[7] < 4500:
                    if numbers[10] > 250000:
                        fmt = 3
                    else:
                        fmt = 1
                else:
                    fmt = 2
            else:
                assert len(numbers) == 18, 'Formato no contemplado'
                fmt = 4

            # print([(ix, jx) for ix, jx in enumerate(numbers)])
            # print(fmt)

            if fmt == 0:
                assert len(numbers) == 20, 'Formato no contemplado'
                pcr = numbers[2]
                hospitalizados_sin_uci_dia = numbers[5]
                hospitalizados = numbers[6]

                uci_dia = numbers[7]
                uci = numbers[8]

                fallecidos_dia = numbers[16]
                fallecidos = numbers[17]

                domicilio_dia = numbers[18]
                domicilio = numbers[19]

                muertos_centros = numbers[9]
                muertos_hospitales = numbers[10]
                muertos_domicilios = numbers[11]
                muertos_otros = numbers[12]
                muertos = numbers[13]

                altas_dia = numbers[14]
                recuperados = numbers[15]
            elif fmt == 1:
                pcr = numbers[2]
                hospitalizados_sin_uci_dia = numbers[3]
                hospitalizados = numbers[4]
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
            elif fmt == 2:
                pcr = numbers[2]
                hospitalizados_sin_uci_dia = numbers[3]
                hospitalizados = numbers[4]
                uci_dia = numbers[5]
                uci = numbers[6]

                fallecidos_dia = numbers[14]
                fallecidos = numbers[15]

                domicilio_dia = numbers[16]
                domicilio = numbers[17]

                muertos_centros = numbers[7]
                muertos_hospitales = numbers[8]
                muertos_domicilios = numbers[9]
                muertos_otros = numbers[10]
                muertos = numbers[11]

                altas_dia = numbers[12]
                recuperados = numbers[13]
            elif fmt == 3:
                pcr = numbers[2]
                hospitalizados_sin_uci_dia = numbers[3]
                hospitalizados = numbers[4]
                uci_dia = numbers[5]
                uci = numbers[6]

                fallecidos_dia = numbers[7]
                fallecidos = numbers[8]

                domicilio_dia = numbers[9]
                domicilio = numbers[10]

                muertos_centros = numbers[11]
                muertos_hospitales = numbers[12]
                muertos_domicilios = numbers[13]
                muertos_otros = numbers[14]
                muertos = numbers[15]

                altas_dia = numbers[16]
                recuperados = numbers[17]
            elif fmt == 4:
                text2 = text.replace('(', ' ')
                text2 = exppoint.sub('', text2).replace('.', ' ')
                text2 = text2.replace('*', ' ')
                text2 = ' '.join(text2.split()).lower()

                # print(text2)

                pcr, _ = getfield(text2, 'casos positivos', 'acumulad')
                hospitalizados_sin_uci_dia, pos1 = getfield(text2, 'pacientes hospitalizados', 'ingresados en el d.a')  # noqa: E501
                hospitalizados, pos2 = getfield(text2, 'pacientes hospitalizados', 'acumulad')  # noqa: E501
                uci_dia, _ = getfield(text2, 'pacientes en uci', 'ingresados en el d.a')  # noqa: E501
                uci, _ = getfield(text2, 'pacientes en uci', 'acumulad')

                if hospitalizados <= uci:
                    uci_dia, _ = getfield(text2[pos1:], '', 'ingresados en el d.a')  # noqa: E501
                    uci, _ = getfield(text2[pos2:], '', 'acumulad')

                if hospitalizados <= uci:
                    hospitalizados, uci = uci, hospitalizados
                    hospitalizados_sin_uci_dia, uci_dia = uci_dia, hospitalizados_sin_uci_dia  # noqa: E501

                fallecidos_dia, _ = getfield(text2, 'fallecidos hospitales', 'en el d.a')  # noqa: E501
                try:
                    fallecidos, _ = getfield(text2, 'fallecidos hospitales', 'acumulado[)]')  # noqa: E501
                except AssertionError:  # informe de 2021-01-24
                    fallecidos, _ = getfield(text2, 'casos positivos', 'acumulado[)]')  # noqa: E501

                try:
                    domicilio_dia, _ = getfield(text2, 'atenci.n primaria', 'seguimiento en el d.a')  # noqa: E501
                except AssertionError:  # informe de 2021-04-23
                    nums = getnumbers(text2, 'atenci.n primaria')
                    assert len(nums) >= 1, 'No numbers para atenci.n primaria'
                    domicilio_dia = nums[0]
                domicilio, _ = getfield(text2, 'atenci.n primaria', 'acumulados')  # noqa: E501

                muertos_centros, _ = getfield(text2, 'mortuoria fallecidos', 'centros sociosanitarios')  # noqa: E501
                muertos_hospitales, _ = getfield(text2, 'mortuoria fallecidos', 'hospitales')  # noqa: E501
                muertos_domicilios, _ = getfield(text2, 'mortuoria fallecidos', 'domicilios')  # noqa: E501
                muertos_otros, _ = getfield(text2, 'mortuoria fallecidos', 'otros lugares')  # noqa: E501
                muertos, _ = getfield(text2, 'mortuoria fallecidos', 'total')

                altas_dia, _ = getfield(text2, 'altas hospitalarias', 'en el d.a')  # noqa: E501
                recuperados, _ = getfield(text2, 'altas hospitalarias', 'acumuladas')  # noqa: E501

                if altas_dia > domicilio_dia:
                    altas_dia, domicilio_dia = domicilio_dia, altas_dia

            else:
                assert False, 'fmt incorrecto'

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

    df = df.astype(int)
    df.index.name = 'Fecha'
    print('Escribiendo', csvfn)
    df.to_csv(csvfn, line_terminator='\r\n')

    # return  # Para no crear serie PCR

    fn2 = sorted(glob(pdfdir + '2*_cam_covid19_2.txt'))[-1]

    sr = getconsol(fn2)
    sr.name = 'PCR+'
    sr.index.name = 'Fecha'
    df2 = sr.to_frame()

    if df.index[-1] != df2.index[-1] + dt.timedelta(1):
        raise RuntimeError('Última fecha de las tablas no coincide')

    # pd.set_option('display.max_rows', None)
    # print(sr)
    # print(sr.diff())
    assert all(sr.diff().dropna() >= 0), 'La serie acumulada no es creciente'
    assert all((sr.index[1:] - sr.index[:-1]).days > 0), 'Fechas no suben'

    csvfn = datadir + 'madrid-pcr.csv'
    print('Escribiendo', csvfn)
    df2.to_csv(csvfn, line_terminator='\r\n')

    print('ESTÁ ACTUALIZADO' if today == df.index[-1].date() else
          '******************* NO ESTÁ ACTUALIZADO')


def getconsol(fn2):
    datefn = getdatefn(fn2)

    fn3 = fn2.replace('_2.txt', '_3.txt')
    fn4 = fn2.replace('_2.txt', '_4.txt')
    fn5 = fn2.replace('_2.txt', '_5.txt')

    print(fn2)
    with open(fn2, encoding='utf-8') as fp:
        text = fp.read()

    m = expacum.search(text)

    assert m, 'Debe ajustarse expacum con los primeros valores'

    saccum = m.group().split()
    if saccum[-1].endswith('/'):  # Ha leído una fecha
        saccum = saccum[:-1]

    accum = []
    for x in saccum:
        x = int(x)
        if len(accum) == 0 or x >= accum[-1]:
            accum.append(x)
        else:
            break

    dates = []
    for m in expfecha.finditer(text):
        dates.append(dt.datetime(int(m.group(3)), int(m.group(2)),
                                 int(m.group(1))))
    dates = sorted(dates)

    accum2 = sorted(int(x.group()) for x in expnumber2.finditer(text)
                    if int(x.group()) > accum[-1])
    accum += accum2

    assert len(accum) == len(dates), 'La serie acumulada no concuerda para _2'

    print(fn3)
    with open(fn3, encoding='utf-8') as fp:
        text = fp.read()

    dates2 = []
    for m in expfecha.finditer(text):
        dates2.append(dt.datetime(int(m.group(3)), int(m.group(2)),
                                  int(m.group(1))))
    dates += sorted(dates2)

    accum2 = [int(x.group()) for x in expnumber2.finditer(text)]
    accum += sorted(accum2)
    assert len(accum) == len(dates), 'La serie acumulada no concuerda para _3'

    if datefn >= dt.datetime(2020, 12, 22):
        print(fn4)
        with open(fn4, encoding='utf-8') as fp:
            text = fp.read()

        dates2 = []
        for m in expfecha.finditer(text):
            dates2.append(dt.datetime(int(m.group(3)), int(m.group(2)),
                                      int(m.group(1))))
        dates += sorted(dates2)

        accum2 = [int(x.group()) for x in expnumber2.finditer(text)]
        accum += sorted(accum2)
        assert len(accum) == len(dates), 'La serie acumulada no concuerda para _4'  # noqa: E501

    if datefn >= dt.datetime(2021, 4, 15):
        print(fn5)
        with open(fn5, encoding='utf-8') as fp:
            text = fp.read()

        dates2 = []
        for m in expfecha.finditer(text):
            dates2.append(dt.datetime(int(m.group(3)), int(m.group(2)),
                                      int(m.group(1))))
        dates += sorted(dates2)

        accum2 = [int(x.group()) for x in expnumber2.finditer(text)]
        accum += sorted(accum2)
        assert len(accum) == len(dates), 'La serie acumulada no concuerda para _5'  # noqa: E501

    return pd.Series(accum, index=dates).sort_index()


def getdatefn(fn):
    base = pth.basename(fn)
    year = 2000 + int(base[:2])
    month = int(base[2:4])
    day = int(base[4:6])

    return dt.datetime(year, month, day)


def getfield(text, title, name):
    if title:
        m = re.search(title, text)
        assert m is not None, f'Título no encontrado: {title}'
        last = m.end()
    else:
        last = 0

    m = re.compile(r'(\d+)\s+' + name).search(text, last)
    assert m is not None, f'Campo no encontrado: {title}/{name}'

    value = int(m.group(1))

    # print(f'{title}/{name}: {value}')

    return value, m.end()


def getnumbers(text, title):
    m = re.search(title, text)
    assert m is not None, f'Título no encontrado: {title}'
    last = m.end()

    numbers = []
    for x in text[last:].split():
        if ')' in x:
            break
        try:
            v = int(x.strip())
        except ValueError:
            continue
        else:
            numbers.append(v)

    return numbers


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
