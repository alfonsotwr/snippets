Contiene el fichero `informes_ministerio_sanidad.csv` (separador tabulador, codificado en UTF-16 con BOM para abrirse directamente con Microsoft Excel) con datos de las [actualizaciones](https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/situacionActual.htm) que publica el Ministerio de Sanidad.

En el `informes_ministerio_sanidad.csv` están incluidos los datos de la Tabla 2 desde el 25 de mayo y no aseguro su actualización.

Los datos de los informes se refieren hasta el día anterior de la fecha del informe y son consolidados a las 12:00 de la fecha del informe. 

El fichero contiene las siguientes columnas:

`informe`: número del informe del ministerio.

`fecha`: fecha del informe.

`ccaa`: código [ISO 3166-2:ES](https://es.wikipedia.org/wiki/ISO_3166-2:ES) de la comunidad autónoma.

`hospitalizados`: casos que han precisado hospitalización (total).

`hospitalizados7`: casos que han precisado hospitalización (con fecha de ingreso en los últimos 7 días).

`uci`: casos que han ingresado en UCI (total).

`uci7`: casos que han ingresado en UCI (con fecha de ingreso en los últimos 7 días).

`fallecidos`: fallecidos (total).

`fallecidos7`: fallecidos (con fecha de defunción en los últimos 7 días).
