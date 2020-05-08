El *script* de Python `descarga_cam.py` es para **descargar** los informes diarios pdf de la Consejería de Salud de la Comunidad de Madrid datos sobre covidia de la Consejería de Salud de la Comunidad de Madrid y **procesarlos** para crear el fichero `madrid-series.csv`. `descarga_cam.py` necesita el módulo de Python `descargabib.py` que también está disponible en este directorio.

Requiere las bibliotecas Python: requests, pdfminer y pandas

En la columna de `hospitalizados_dia` sumo los Hospitalizados ingresados en el día y los de la UCI ingresados en el día, tal como hacía el Ministerio de Sanidad en sus informes: entiendo que los Hospitalizados ingresados en el día de la Consejería de Salud no incluyen a los de la UCI, mientras el Ministerio de Sanidad sí los incluye.

Los informes PDF de la Consejería de Salud de la Comunidad de Madrid están disponibles en:

https://www.comunidad.madrid/servicios/salud/2019-nuevo-coronavirus#situacion-epidemiologica-actual
