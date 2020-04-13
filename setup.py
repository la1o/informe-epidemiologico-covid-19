# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='informe-epidemiologico-covid-19',
    version='0.0.1',
    description='Parser Informe Epidemiológico COVID19 MINSAL',
    long_description=readme,
    author='Eduardo Cabrera',
    author_email='ecabrera@eof.cl',
    url='https://github.com/la1o/informe-epidemiologico-covid-19',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
