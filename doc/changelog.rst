Release history
===============

0.2.2
-----
- Update ``from_url`` to work with newer versions of redis-py (this might
  break older versions, although it hasn't been tested).
- Test and build wheels for newer Python versions (up to CPython 3.11 and PyPy
  3.9).

0.2.1
-----
- Fix ``from_url``
- Fix a segfault if small integers are stored in the database at shutdown
- Clarify that only Linux with glibc is supported

0.2.0
-----
- Update vendored birdisle to redis 5.0.12
- Drop support for Python versions older than 3.6
- Remove use of async_generator
- Support the latest redis-py, and require at least 3.4.1
- Pin aioredis to versions less than 2 (2.x is not currently supported)
- Build wheels for newer Python versions (up to 3.10)
- Switch from Travis CI to Github Actions
- Remove mkwheel.sh and rely on cibuildwheel instead
- Remove use of loop arguments where Python 3.10 no longer supports them
- Fix a log message with an extraneous %s
- Stop using deprecated ``locale.format_string``

0.1.3
-----
- Update vendored birdisle to redis 5.0.3

0.1.2
-----
- Support redis-py 3.0
- Update vendored birdisle (reduces memory usage)

0.1.1
-----
- Update README.md
- Add coverage measurement with coveralls

0.1
---
This is the first release.
