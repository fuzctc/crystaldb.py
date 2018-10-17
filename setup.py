# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2018-10-06 12:33:04

from setuptools import setup
import os

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
try:
    readme = f.read()
    f.close()
except:
    readme = "a little orm"

setup(
    name='crystaldb',
    description='a little orm',
    long_description=readme,
    author='Zhichang Fu',
    author_email='fuzctc@gmail.com',
    url='https://github.com/CrystalSkyZ/crystaldb.py',
    version=__import__('crystaldb').__version__,
    packages=['crystaldb'],
    include_package_data=True,
    exclude_package_date={'': ['.gitignore']},
    install_requires=[],
)
