#!/usr/bin/env python
import os
import re
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

with open(os.path.join('birdisle', '_version.py'), 'r') as f:
    match = re.search('__version__ = "([^"]+)"', f.read())
    version = match.group(1)

tests_require = [
    'pytest', 'pytest-forked', 'redis',
    'pytest-asyncio; python_version >= "3.5"',
    'async-generator; python_version >= "3.5"',
    'aioredis; python_version >= "3.5"'
]

setup(
    name='birdisle',
    version=version,
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
        'redis': 'redis',
        'aioredis': 'aioredis',
        'test': tests_require
    },
    tests_require=tests_require,
    cffi_modules=['builder.py:ffibuilder']
)
