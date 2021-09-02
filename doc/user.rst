User guide
==========

Birdisle (an anagram of "lib redis") is a modified version of
`redis`_ that runs as a library inside another process. The
primary aim is to simplify unit testing by providing a way to run tests
against what appears to be a redis server, but without the hassle of starting a
separate process and ensuring that it is torn down correctly.

.. _redis: https://redis.io

Birdisle-py is a Python wrapper that allows Birdisle to be used from Python. It
contains integrations with `redis-py`_ and `aioredis`_ to simplify usage. It
also has a lower-level API that can be used for integration with other client
libraries.

.. _redis-py: https://redis-py.readthedocs.io/
.. _aioredis: https://aioredis.readthedocs.io/

Birdisle is only supported on Linux, and does not currently work with Alpine
(or any distribution that uses musl rather than glibc).

Server class
------------

The documentation refers a number of times to a "server". A server is an instance of
:class:`birdisle.Server`, and is the equivalent of a separate Redis server:
each instance is backed by separate databases. Note that each server also uses
a non-trivial number of resources (including threads and network sockets), so while it is
reasonable to have a few, you will likely run into problems if you try to
create thousands. The resources can be explicitly freed by calling
:meth:`~birdisle.Server.close`.

The class optionally takes the contents of a configuration file. It can be
specified as either :class:`bytes` or :class:`str` (:class:`unicode` in Python
2). In the latter case it will be encoded for consumption by Birdisle. Note
that not all redis features work in birdisle (see a list of `limitations`_),
and trying to use an unsupported feature can lead to undefined behaviour
including crashes.

.. _limitations: https://github.com/bmerry/birdisle#limitations

redis-py integration
--------------------

The redis-py integration is in the module :mod:`birdisle.redis`.
Classes :class:`~birdisle.redis.Redis` or
:class:`~birdisle.redis.StrictRedis` are intended to replace the redis-py
classes of the same names, and are in fact subclasses.

Instead of host and port arguments, they take a `server` keyword argument to
specify the :class:`~birdisle.Server`. If not specified, a new server is
created. Note that this is different behaviour to `fakeredis`_, where the
default is for all instances to be backed by the same data.

.. _fakeredis: https://github.com/jamesls/fakeredis

aioredis integration
--------------------

Within the module :mod:`birdisle.aioredis`, the functions
:func:`~birdisle.aioredis.create_connection`,
:func:`~birdisle.aioredis.create_redis`,
:func:`~birdisle.aioredis.create_pool` and
:func:`~birdisle.aioredis.create_redis_pool` are replacements for the aioredis
functions of the same names. Instead of an address, they take a
:class:`~birdisle.Server` as the first argument. If the argument is omitted, a
new :class:`~birdisle.Server` is created.
