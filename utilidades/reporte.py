# vim: sw=4:expandtab:foldmethod=marker

"""
Modulo para procesar archivos pdf
"""

import re
import csv
import os
import shutil
import urllib3
import pdftotext
from bs4 import BeautifulSoup

def clean_float(num):
    """ Pasa de string a float """
    ntmp = num.replace('.', '').replace(',', '.')
    return float(ntmp)

def clean_integer(num):
    """ Pasa de string a int """
    ntmp = num.replace('.', '')
    return int(ntmp)

class Reporte:
    """ Clase para procesar archivos pdf"""

    def __init__(self, current_path, debug, overwrite):
        self.reporte_url = 'https://www.minsal.cl/nuevo-coronavirus-2019-ncov/informe-epidemiologico-covid-19/'
        self.resources_pdf = f'{current_path}/resources/pdf/'
        self.resources_csv = f'{current_path}/resources/csv/'
        self.resources_output = f'{current_path}/resources/output/'
        self.debug = debug
        self.overwrite = overwrite

    def _debug(self, msg):
        if self.debug:
            print(msg)

    def obtener(self):
        req = urllib3.PoolManager()
        res = req.request('GET', self.reporte_url)
        soup = BeautifulSoup(res.data, features="html.parser")

        pdfs = []
        for link_soup in soup.find_all('a'):
            link = str(link_soup.get('href'))
            regex_pdf = re.compile(r"(informe|reporte)[\w\-]*\.pdf", re.IGNORECASE)
            pdf_match = re.search(regex_pdf, link)
            if pdf_match:
                pdf_file = f'{self.resources_pdf}{os.path.basename(link)}'
                if not os.path.isfile(pdf_file):
                    with req.request('GET', link, preload_content=False) as res, open(pdf_file, 'wb') as pfopen:
                        shutil.copyfileobj(res, pfopen)
                        pdfs.append(os.path.basename(link))

        return pdfs

    def parser(self, pdf_file):
        """ Desde raw pdftotext parsea linea por linea cada tabla"""
        regiones = []
        with open(f"{self.resources_csv}region_codigo.csv", 'r', ) as fprc:
            regiones_csv = csv.reader(fprc, delimiter=';')
            next(regiones_csv)
            for row in regiones_csv:
                regiones.append({'nombre': row[0], 'codigo': row[1], 'comunas': {}})

        #with open('resources/csv/comuna_codigo.csv', 'r', ) as fprc:
        #    comunas_csv = csv.reader(fprc, delimiter=';')
        #    next(comunas_csv)
        #    for c in comunas_csv:
        #        regiones[c[0]]['comunas'][c[1]] = {'codigo': c[2]}
        #    
        #pprint.pprint(regiones)

        self._debug(f"procesando: {os.path.basename(pdf_file)}")

        with open(pdf_file, "rb") as pfopen:
            pdf = pdftotext.PDF(pfopen)

        # obtengo fecha del header de la primera pagina :U 
        text_tmp = pdf[1]
        #self._debug(text_tmp)

        regex_get_date = r'\s+INFORME\s+EPIDEMIOLÓGICO\.\s+COVID-19\.\s+(\d{2})-(\d{2})-(\d{4})\.'
        compile_get_date = re.compile(regex_get_date, re.MULTILINE)
        match = compile_get_date.search(text_tmp)
        report_date = ''
        if match:
            report_date = f'{match.group(3)}-{match.group(2)}-{match.group(1)}'

        # solo reviso el desagregado de este informe
        regex_first_page = r"ANALISIS REGIONAL\s*\.+\s*(\d+)"
        compile_first_page = re.compile(regex_first_page, re.MULTILINE)
        match = compile_first_page.search(text_tmp)
        first_page = 1
        if match:
            first_page = f'{match.group(1)}'

        page_count = int(first_page) - 1
        end = len(pdf)

        '''
        en los 2 primeros informes usaron como header comuna, en vez de region (le llamaron regiones a las comunas)
        y la segunda columna son los confirmados, en algun momento lo revisaran :U
        '''

        regex_title_table1 = r"\s*Región\s+Población\s+"
        compile_title_table1 = re.compile(regex_title_table1)

        regex_title_table2 = r"\s*Comuna\s+N"
        compile_title_table2 = re.compile(regex_title_table2)

        regex_title_table3 = r"\s*Comuna\s+Población"
        compile_title_table3 = re.compile(regex_title_table3)

        regex_total_table = r"\s*Total\s+"
        compile_total_table = re.compile(regex_total_table)

        regex_line_table = r"([A-ZÑ][\w\s\']*)\s{3}\s*((\d+[\d\.,]*)|\-)\s+((\d+[\d\.,]*)|-)\s+((\d+[\d\.,]*)|\-)"
        compile_line_table = re.compile(regex_line_table)

        comunas = []
        count = 1
        flag = False
        header_format = 1

        while page_count < end:
            text_tmp = pdf[page_count]
            #self._debug(text_tmp)

            for line in text_tmp.split("\n"):
                line = line.strip()
                #self._debug(f"** {line}")

                if compile_title_table1.search(line) \
                    or compile_title_table2.search(line) \
                    or compile_title_table3.search(line):
                    flag = True

                    if compile_title_table2.search(line):
                        header_format = 2

                    region_codigo = regiones[count-1]['codigo']
                    region_nombre = regiones[count-1]['nombre']
                    #self._debug(line)

                if compile_total_table.search(line):
                    count += 1
                    flag = False

                if flag:
                    match = compile_line_table.search(line)

                    if match:
                        comuna = match.group(1).strip()

                        poblacion = 0
                        confirmados = 0

                        poblacion_index = 2
                        confirmados_index = 4
                        if header_format == 2:
                            poblacion_index = 4
                            confirmados_index = 2

                        if match.group(poblacion_index) != '-':
                            poblacion = clean_integer(match.group(poblacion_index))

                        if match.group(confirmados_index) != '-':
                            confirmados = clean_integer(match.group(confirmados_index))

                        tasa_incidencia = 0  
                        if match.group(6) != '-':
                            tasa_incidencia = clean_float(match.group(6))

                        data = {
                            'region_nombre': region_nombre,
                            'region_codigo': region_codigo,
                            'comuna': comuna,
                            'poblacion': poblacion,
                            'confirmados': confirmados,
                            'tasa_incidencia': tasa_incidencia,
                            'fecha': report_date
                        }

                        #self._debug(f'{comuna} {poblacion} {confirmados} {tasa_incidencia}')
                        comunas.append(data)

                if count >= 17:
                    break

            page_count += 1

        return comunas

    def escribir(self, data):
        """ Escribe archivo csv"""
        if not data:
            self._debug(f"csv: sin datos que escribir")
            return None

        fecha = data[0]['fecha']
        csv_name = f"{self.resources_output}comuna_{fecha}.csv"

        if os.path.isfile(csv_name) and not self.overwrite:
            self._debug(f"csv: {csv_name} ya existe")
            return fecha

        with open(csv_name, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            first = True
            for row in data:
                if first:
                    csv_writer.writerow(row.keys())
                    first = False
                csv_writer.writerow(row.values())

            self._debug(f"csv: {os.path.basename(csv_name)}")

        return fecha