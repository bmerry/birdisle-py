#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='birdisle',
    version='0.1',
    author='Bruce Merry',
    author_email='bmerry@gmail.com',
    description='Python bindings for birdisle',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bmerry/birdisle-py',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Testing'
    ],
    license='BSD',
    packages=find_packages(),
    package_data={'birdisle': ['.libs/libbirdisle.so.*']},
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0'],
    extras_require={
        'redis': 'redis'
    },
    tests_require=['pytest', 'pytest-forked'],
    cffi_modules=['builder.py:ffibuilder']
)
