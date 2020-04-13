Parser Informe epidemiológico enfermedad por COVID-19
-----
Se obtienen los archivos pdf que corresponden a los `informes epidemiológicos <https://www.minsal.cl/nuevo-coronavirus-2019-ncov/informe-epidemiologico-covid-19/>`_,
luego de estos se obtienen los datos de cada una de las tablas por comuna.

Instalación
-----

Usar requirements.txt y seguir la guía para los pasos extras de `pdftotext <https://pypi.org/project/pdftotext/>`_

Alcances
-----

- Siempre visita la página web para buscar nuevos pdf
- No sobreescribe los archivos csv (-o 1)
- Los archivos csv resultante quedan en resources/output/


Ejecución
-----

::

	$ ./procesar.py -d 1
	procesando: Informe_EPI_GOB_08_04_2020.pdf
	csv: comuna_2020-04-08.csv
	procesando: INFORME_EPI_COVID19_20200330.pdf
	[...]
