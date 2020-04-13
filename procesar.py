#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para procesar archivos pdf con información COVID19
"""

__author__ = "Eduardo Cabrera"
__version__ = "0.0.1"
__license__ = "BSD"

import argparse
import os
import sys
import glob
import json

CURRENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, CURRENT_PATH)

LOCAL_CONF = f"{CURRENT_PATH}/resources/conf/conf.json"

from utilidades import *

def parametros():
    """ Distintas opciones """
    parser = argparse.ArgumentParser()

    # imprime debug
    parser.add_argument("-d", "--debug", default=False)

    # sobreescribir archivos csv
    parser.add_argument("-o", "--overwrite", default=False)

    args = parser.parse_args()
    return args

def main():
    """ obtengo los archivos para parsear y escribo csv """
    mip = parametros()
    mir = Reporte(CURRENT_PATH, mip.debug, mip.overwrite)
    pdfs = mir.obtener()
    if pdfs:
        print("Obteniendo nuevos pdf:")
        for pdf in pdfs:
            print(f"* {pdf}")

    for file in glob.glob(f"{CURRENT_PATH}/resources/pdf/*.pdf"):
        data = mir.parser(file)
        mir.escribir(data)

if __name__ == "__main__":
    sys.exit(main())
    