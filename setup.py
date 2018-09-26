#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='birdisle',
    version='0.1',
    author_name='Bruce Merry',
    author_email='bmerry@gmail.com',
    packages=find_packages(),
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0', 'redis'],
    cffi_modules=['birdisle/builder.py:ffibuilder']
)
