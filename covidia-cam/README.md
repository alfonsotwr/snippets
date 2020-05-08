El *script* de Python `descarga_cam.py` es para **descargar** los informes diarios pdf de la Consejería de Salud de la Comunidad de Madrid datos sobre covidia de la Consejería de Salud de la Comunidad de Madrid y **procesarlos** para crear el fichero `madrid-series.csv`. `descarga_cam.py` necesita el módulo de Python `descargabib.py` que también está disponible en este directorio.

Requiere las bibliotecas Python: requests, pdfminer, pandas

Los informes PDF de la Consejería de Salud de la Comunidad de Madrid se pueden descargar de:

https://www.comunidad.madrid/servicios/salud/2019-nuevo-coronavirus#situacion-epidemiologica-actual
