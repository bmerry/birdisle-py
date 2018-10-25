# birdisle-py

[![Build Status](https://travis-ci.org/bmerry/birdisle-py.svg?branch=master)](https://travis-ci.org/bmerry/birdisle-py)
[![Coverage Status](https://coveralls.io/repos/github/bmerry/birdisle-py/badge.svg)](https://coveralls.io/github/bmerry/birdisle-py)
[![Documentation Status](https://readthedocs.org/projects/birdisle/badge/?version=latest)](https://birdisle.readthedocs.io/en/latest/?badge=latest)

Birdisle (an anagram of "lib redis") is a modified version of
[redis](https://redis.io) that runs as a library inside another process. The
primary aim is to simplify unit testing by providing a way to run tests
against what appears to be a redis server, but without the hassle of starting a
separate process and ensuring that it is torn down correctly.

Birdisle-py is Python bindings for Birdisle. Documentation can be found at
[readthedocs](https://birdisle.readthedocs.io/).
