# ANOTACIONES #

+ Los ficheros `pdf` descargados se guardan en el subdirectorio `data/` y los csv 
se generan en el mismo directorio donde está el script `descarga_cam.py`.

+ El script `comprueba-cam.py` sirve para dibujar todas las series guardadas.
Necesita de las bibliotecas pandas y matplotlib.

+ Para encontrar errores al generar los ficheros de datos ayuda revisar el
_diff_ del _commit_ en github.

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

+ Normalmente los informe pdf de la CAM se publican algo después de las 17:00
a diario pero los fines de semana y festivos se pueden retrasar más. Si no
cambian el formato del nombre, los ficheros se pueden descargar antes incluso
antes de que publiquen el enlace.

+ Cuando por festivo no se publica un informe, conviene indicarlo en el script
`descarga_cam.py` en el apartado _Días sin datos_, donde hay que añadir una
nueva fecha:

        # Días sin informe
        if current in [dt.date(2020, 10, 12),
                       dt.date(2020, 12, 25),
                       dt.date(2021, 1, 1),
                       dt.date(2021, 1, 6)]:
            current += dt.timedelta(1)
            continue

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
