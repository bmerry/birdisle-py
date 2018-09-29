#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='birdisle',
    version='0.1',
    author='Bruce Merry',
    author_email='bmerry@gmail.com',
    packages=find_packages(),
    package_data={'birdisle': ['.libs/libbirdisle.so.*']},
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0', 'redis'],
    tests_require=['pytest', 'pytest-forked'],
    cffi_modules=['builder.py:ffibuilder']
)
