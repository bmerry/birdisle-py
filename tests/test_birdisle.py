import redis
import birdisle


def test_simple():
    r = birdisle.StrictRedis()
    r.set('hello', 'world')
    assert r.get('hello') == b'world'


def test_repr():
    r = birdisle.StrictRedis()
    repr(r)
