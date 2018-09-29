import locale

import redis
import birdisle
import pytest


def test_simple():
    r = birdisle.StrictRedis()
    r.set('hello', 'world')
    assert r.get('hello') == b'world'


def test_repr():
    r = birdisle.StrictRedis()
    repr(r)


def test_locale():
    try:
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    except locale.Error:
        pytest.skip()
    # Confirm that this is a locale which doesn't use the decimal point
    assert locale.format('%g', 1.5) == '1,5'
    r = birdisle.StrictRedis()
    r.set('foo', b'1.5')
    r.incrbyfloat('foo', b'0.25')
    assert r.get('foo') == b'1.75'
    # Check that birdisle hasn't overridden this thread's locale
    assert locale.format('%g', 1.5) == '1,5'
