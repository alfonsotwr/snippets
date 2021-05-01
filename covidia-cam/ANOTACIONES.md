# ANOTACIONES #

+ Los ficheros `pdf` descargados y los ficheros csv creado se guardan en el
mismo directorio donde está el script `descarga_cam.py`, a no ser que exista el
directorio, `data/pdf/`, en cuyo caso los pdf se guardan en `data/pdf/` y los
fichero csv creados en `data/`.

+ El script `comprueba-cam.py` sirve para dibujar todas las series guardadas.
Necesita de las bibliotecas pandas y matplotlib.

+ Los ficheros pdf se descargan de
<https://www.comunidad.madrid/servicios/salud/coronavirus#datos-situacion-actual>.
Si falla la descarga porque han puesto un nombre de fichero distinto al usado
habitualmente, se puede bajar el fichero manualmente desde la página web,
guardándolo con los demás ficheros y asegurándose que el nombre del fichero es
de la forma: `YYMMDD_cam_covid19.pdf`.

+ También, si se quiere que lo encuentre sin tener que descargarlo
manualmente, se puede añadir en el script `descarga_cam.py` el código para que
encuentre el fichero correcto, en el apartado casos especiales, como:

                elif current == dt.date(2021, 4, 28):  # casos especiales
                    url = url.replace('/doc/', '/aud/')
                    changed = True

+ La expresión regular `expacum` de `descarga_cam.py` debe coincidir con los
casos acumulados de los tres primeros días de la serie consolidada.
Afortunadamente hace ya mucho tiempo que no hace falta cambiarla:

		expacum = re.compile(r'\n(1|2) \n(5|6|7|8) \n(9|10|11|12|13) \n[\d \n]+(/)?')

+ Otras veces ha fallado el script porque el formato cambia o hay páginas
distintas o hacen falta más páginas para la serie consolidada: ya es más
complicado arreglarlo.

+ Otro fallo más desconcertante es que aunque el PDF parece el mismo formato,
los .txt creados a partir del pdf por la biblioteca pdfminer.six son
ligeramente distintos, y a veces es lioso arreglarlo, porque además hay que
mantener la compatibilidad con los días anteriores.
