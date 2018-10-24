#!/bin/bash

# Release process
# - Update birdisle/_version.py
# - Update doc/changelog.rst
# - Run this script
# - Upload the source dist and wheels to PyPI
# - Create a git tag and push it

set -e -u

python - <<EOF
import sys
if sys.version_info[0] != 3:
    raise RuntimeError("Run in a Python 3 environment")
EOF
pip install setuptools_git
make -C doc clean
make -C doc html
flake8
pytest --forked
./setup.py sdist
./mkwheels.sh
