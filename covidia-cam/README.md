**covidia-cam** forma parte del proyecto [Escovid19data: Capturando colaborativamente datos de COVID-19 por provincias en España](https://github.com/montera34/escovid19data).

El *script* de Python `descarga_cam.py` es para **descargar** los informes diarios pdf de la Consejería de Salud de la Comunidad de Madrid datos sobre covidia de la Consejería de Salud de la Comunidad de Madrid y **procesarlos** para crear los ficheros `madrid-series.csv` y `madrid-pcr.csv`. `descarga_cam.py` necesita el módulo de Python `descargabib.py` que también está disponible en este directorio. Requiere además las bibliotecas Python: requests, pdfminer.six y pandas

**Fichero `madrid-series.csv`**

En la columna de `hospitalizados_dia` sumo los Hospitalizados ingresados en el día y los de la UCI ingresados en el día, tal como hacía el Ministerio de Sanidad en sus informes: entiendo que los Hospitalizados ingresados en el día de la Consejería de Salud no incluían a los de la UCI, mientras el Ministerio de Sanidad sí los incluye, por lo que he usado la convención del Ministerio de Sanidad en los ficheros de datos.

Los informes PDF de la Consejería de Salud de la Comunidad de Madrid están disponibles en:

https://www.comunidad.madrid/servicios/salud/2019-nuevo-coronavirus#situacion-epidemiologica-actual

**Fichero `madrid-historico.csv`**

Contiene las series con datos que complementan o incluso sustituyen los datos que proporciona la Consejería de Salud en `madrid-series.csv`.

La fecha corresponde a la fecha de publicación del informe, es decir, son los datos del día anterior.

Así las columnas de `Recuperados`, `uci_dia` y `hospitalizados_dia` del fichero `madrid-historico.csv` fueron extraídas de las series publicadas el Instituto de Salud Carlos III (ISCIII) el 26 de abril de 2020.

Las columnas `CASOS_PCR`, `Hospitalizados`, `UCI` y `Fallecidos` del fichero `madrid-historico.csv` corresponden a las series actualizadas por el Instituto de Salud Carlos III (ISCIII) en las series publicadas el 21 de mayo de 2020.

Los datos del fichero `madrid-historico.csv` tienen preferencia a los de `madrid-series.csv`.

**Fichero `madrid-pcr.csv`**

Contiene la serie consolidada de positivos PCR que publica en cada informe la Consejería de Salud de la Comunidad de Madrid. La columna `Fecha` es la fecha de detección y `PCR+` los positivos PCR acumulados para esa fecha.

**NOTA**:

Desde el informe del 6 de octubre de 2020, los informes han cambiado de "Positivos PCR" a "Casos positivos", que indicaría que van a incluir los positivos por tests de antígenos. Por no cambiar el formato de los ficheros, aunque la columna indique PCR, entiéndase que se refieren a los casos positivos que vienen en el informe. 
