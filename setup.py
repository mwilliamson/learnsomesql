#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='learnsomesql',
    version='0.1.0',
    description='Website for learnsomesql.com',
    long_description=read("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/learnsomesql',
    packages=['learnsomesql'],
    install_requires=[
        "Flask<=0.10.1,<0.11",
        "sqlexecutor>=0.1.0,<0.2",
    ],
    license='BSD 2-Clause',
)
