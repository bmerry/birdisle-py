# Maintainer wanted

I've ended up not using birdisle and have no interest in maintaining it. If you
would like to take over as maintainer, please let me know by filing a ticket.

# birdisle-py

[![Build Status](https://github.com/bmerry/birdisle-py/actions/workflows/build.yml/badge.svg)](https://github.com/bmerry/birdisle-py/actions/workflows/build.yml)
[![Documentation Status](https://readthedocs.org/projects/birdisle/badge/?version=latest)](https://birdisle.readthedocs.io/en/latest/?badge=latest)

Birdisle (an anagram of "lib redis") is a modified version of
[redis](https://redis.io) that runs as a library inside another process. The
primary aim is to simplify unit testing by providing a way to run tests
against what appears to be a redis server, but without the hassle of starting a
separate process and ensuring that it is torn down correctly.

Birdisle-py is Python bindings for Birdisle. Documentation can be found at
[readthedocs](https://birdisle.readthedocs.io/).
