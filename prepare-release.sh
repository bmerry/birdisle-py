#!/bin/bash

# Release process
# - Update birdisle/_version.py
# - Update doc/changelog.rst
# - Run this script
# - Push to Github
# - Download sdist and wheels from Github Actions
# - Upload the source dist and wheels to PyPI
# - Create a git tag and push it

set -e -u

make -C doc clean
make -C doc html
flake8
pytest --forked
