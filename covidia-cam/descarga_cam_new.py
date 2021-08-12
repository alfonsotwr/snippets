# -*- coding: utf-8 -*-

"""Requiere las bibliotecas Python: requests, pdfminer.six, pandas; Módulo: descargabib.py  # noqa: E501

Informes de:

https://www.comunidad.madrid/servicios/salud/coronavirus#datos-situacion-actual
"""

from os import path as os_pth, chdir as os_chdir
from shutil import copy as shutil_copy

import datetime as dt
import time
from glob import glob
import re
import pandas as pd

from os import  chdir as os_chdir, path as os_path
from glob import glob
from  numpy import r_ as np_r
import pandas as pd
import fitz
from  sys import argv as sys_argv

from io import StringIO

from pathlib import Path

from descargabib import descarga


os_chdir(str(Path(__file__).parent))

pdfdir  = 'data/'
datadir = ''

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

    try:
       Path(pdfdir).mkdir(parents=True, exist_ok=True)
    except:
        print(f"ERROR: No puedo crear directorio para PDFs {pdfdir}")


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
                       dt.date(2021, 1, 6),
                       dt.date(2021, 5, 8)]:
            current += dt.timedelta(1)
            continue

        fn = pdfdir + FN_TPL.format(current.year % 100, current.month, current.day) 
        url = URL_TPL.format(current.year % 100, current.month, current.day)

        paths_posibles=[('covid19','covid-19'), ('doc','aud'),
                        ('doc/sanidad', 'aud/empleo'),
                        ('doc/sanidad', 'doc/sanidad/rrhh'),
                        ('cam_covid19', 'cam_covid'),
                        ('/doc/sanidad/', '/aud/empleo/')]

        ret = False

        if not os_pth.exists(fn):
            ret = descarga(url, fn, isbinary=True)
            time.sleep(1)

            while not ret:
                for caso in paths_posibles:
                    url= url.replace(caso[0], caso[1] )
                    ret = descarga(url, fn, isbinary=True)
                    time.sleep(1)
                    if ret: break


        if ret:
            print(f"descargado: {fn}")

        current += dt.timedelta(1)


#############
# Creamos el csv con los datos PCR actuales.
# Se recrea la tabla completa cada día.

def tabla_PCR_actual(pdf ):
    lista = []
    
    doc=fitz.open(pdf)

    for pagina in range(2,7):  # Páginas del pdf con tablas de datos PCR
        df = pd.DataFrame.from_dict(  doc.get_page_text(pno=pagina, option='blocks'))
        df2 = df[4].str.split(' \n', expand=True)   

        #print (pagina, df2.shape, df2.shape[1])# 
        columnas = df2.shape[1]

        # Tenemos 3 columnas de datos en el PDF con 3 campos cada columna.
        # Los partimos y concatenamos
        lista.append(df2.iloc[:,0:3].set_axis(['Fecha_Notif', 'diario', 'PCR+'], axis=1))
        if columnas > 6 : lista.append(df2.iloc[:,4:7].set_axis(['Fecha_Notif', 'diario', 'PCR+'], axis=1))
        if columnas > 9 : lista.append(df2.iloc[:,8:11].set_axis(['Fecha_Notif', 'diario', 'PCR+'], axis=1))

    df_temp=pd.concat(lista, ignore_index=True)

    df_limpio = df_temp.loc[(df_temp['Fecha_Notif'].str.len()== 10) & ~df_temp['PCR+'].isnull()] #
    
    df_limpio.insert(loc=0, column='Fecha', value=pd.to_datetime(df_limpio['Fecha_Notif'], dayfirst=True).astype('str'))
    
    df_limpio = df_limpio.drop(columns=['Fecha_Notif','diario'])# drop colums no usadas

    df_limpio=df_limpio.sort_values(by='Fecha', ascending=True) # 

    df_limpio.to_csv('madrid-pcr.csv', index=False, encoding='utf-8' ) 


def datos_resumen(fecha):
    """
    Extrae los datos resumen de la página 2 del PDF 
    """

    pdf=f"{pdfdir}{dt.datetime.strftime(fecha,'%y%m%d')}_cam_covid19.pdf"

    try :
        doc=fitz.open(pdf)

    except :
        return

    print(pdf)

    fecha_str=f"20{pdf[-22:-20]}-{pdf[-20:-18]}-{pdf[-18:-16]}"

    df_temp = pd.DataFrame.from_records(  doc.get_page_text(pno=1, option='blocks'))

    # Quitamos '24h'
    df_temp = df_temp.loc[df_temp[6]==0, 4].replace('24h','', regex=True)  
    
    # Quitamos saltos de línea y los puntos. Todos los números son enteros.
    df_temp = df_temp.replace('\n','', regex=True).str.replace('.','', regex=False) 
    
    # Quitamos letras y espacios en blanco.
    df_temp = df_temp.replace(r'[A-Za-z]', '', regex=True).str.replace(' ','') 
    
    # Quitamos los paréntesis apertura y cierre.
    df_temp = df_temp.str.replace(r'(','', regex=True).str.replace(r')','',regex=True) 
    
    # Nos quedamos con los enteros
    df_temp = pd.to_numeric(df_temp, errors='coerce', downcast='signed').dropna().astype(int)

    lista_valores = df_temp.tolist()



    df = pd.DataFrame(data={
                 'Fecha': fecha_str,
                 'CASOS_PCR': lista_valores[17],
                 'Hospitalizados': lista_valores[1],
                 'UCI': lista_valores[3],
                 'Fallecidos': lista_valores[9],
                 'Recuperados': lista_valores[7],
                 'domicilio': lista_valores[5],
                 'uci_dia': lista_valores[2],
                 'hospitalizados_dia':lista_valores[0]+lista_valores[2],
                 'domicilio_dia': lista_valores[4],
                 'altas_dia': lista_valores[6],
                 'fallecidos_dia': lista_valores[8],
                 'muertos_hospitales': lista_valores[11],
                 'muertos_domicilios': lista_valores[12],
                 'muertos_centros': lista_valores[10],
                 'muertos_otros': lista_valores[13],
                 'muertos': lista_valores[14]}, index=[0] )


    df.to_csv('madrid-series.csv', index=False, mode='a', header=False, encoding='utf-8')


############################
# PROCESO PRINCIPAL
#
if __name__ == '__main__':

    descargacam()

    # Después de descargar los ficheros.
    # Ejecución para crear el fichero de PCRs, 

    
    ultimo_doc=max( glob(f"{pdfdir}*.pdf"))

    ultimo_doc_dt=dt.datetime.strptime(ultimo_doc[5:11],"%y%m%d").date()

    # El fichero madrid-pcr.csv se crea con los datos consolidados del último pdf publicado
    tabla_PCR_actual(ultimo_doc)

    # El fichero madrid-series.csv se crea con los datos resumen publicados cada día.
    # Leemos el fichero madrid-series.csv y le añadimos los datos de hoy,
    # ó de todos los días descargados desde la última actualización.

    fecha_hoy = dt.date.today()

    try :
        df_madrid_series=pd.read_csv('madrid-series.csv')
        fecha_actual=dt.datetime.strptime( df_madrid_series.Fecha.max(), '%Y-%m-%d').date()

    except :
        print("no existe el fichero madrid-series.csv.")
        print("Lo creamos a partir del fichero madrid-series-2021-04-30.csv")
        print("y añade los datos de los pdf posteriores al 2021-04-30")
        
        try :
            shutil_copy("madrid-series-2021-04-30.csv", "madrid-series.csv")
        
        except :    
            print(f"Error para copiar madrid-series-2021-04-30.csv ==> madrid-series.csv")

        fecha_actual=dt.date(2021, 4, 30 )
        

    print(fecha_actual)
 

    while fecha_actual < fecha_hoy:
        fecha_actual +=dt.timedelta(days=1)
        datos_resumen(fecha_actual)
    

    


    
