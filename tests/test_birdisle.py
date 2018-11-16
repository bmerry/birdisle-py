import time
import threading
import locale
import resource
import signal

import redis
import birdisle
import birdisle.redis
import pytest


@pytest.fixture
def server():
    server = birdisle.Server()
    yield server
    server.close()


@pytest.fixture
def r(server):
    redis = birdisle.redis.StrictRedis(server=server)
    yield redis


@pytest.fixture
def limit_fds():
    """Reduce the maximum allowed file descriptors."""
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    new_soft = min(hard, 128)
    resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
    yield new_soft
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))


@pytest.fixture
def profile_timer():
    def call(interval, handler):
        old_handler = signal.signal(signal.SIGALRM, handler)
        old_delay, old_interval = signal.setitimer(signal.ITIMER_REAL, interval, interval)
        cleanup.append((old_delay, old_interval, old_handler))

    cleanup = []
    yield call
    if cleanup:
        signal.setitimer(signal.ITIMER_REAL, cleanup[0][0], cleanup[0][1])
        signal.signal(signal.SIGALRM, cleanup[0][2])


def test_simple(r):
    r.set('hello', 'world')
    assert r.get('hello') == b'world'


def test_repr(r):
    repr(r)


def test_use_after_closed(server):
    server.close()
    with pytest.raises(RuntimeError):
        server.connect()
    with pytest.raises(RuntimeError):
        server.add_connection(0)


def test_locale():
    try:
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    except locale.Error:
        pytest.skip()
    # Confirm that this is a locale which doesn't use the decimal point
    assert locale.format('%g', 1.5) == '1,5'
    r = birdisle.redis.StrictRedis()
    r.set('foo', b'1.5')
    r.incrbyfloat('foo', b'0.25')
    assert r.get('foo') == b'1.75'
    # Check that birdisle hasn't overridden this thread's locale
    assert locale.format('%g', 1.5) == '1,5'


def test_lua(r):
    r.set('foo', 'bar')
    script = r.register_script("return redis.call('GET', KEYS[1])")
    result = script(['foo'])
    assert result == b'bar'


def test_info(r):
    """Test that the INFO command works"""
    r.info()


def test_blocking(r):
    def worker(r):
        time.sleep(0.1)
        r.rpush('foo', 'bar')

    thread = threading.Thread(target=worker, args=(r,))
    thread.start()
    result = r.blpop('foo')
    assert result == (b'foo', b'bar')
    thread.join()


def test_pubsub(r):
    ps = r.pubsub()
    ps.subscribe('channel')
    r.publish('channel', 'hello')
    msg = ps.get_message(timeout=10)   # Subscribe message
    msg = ps.get_message(timeout=10)
    assert msg == {'channel': b'channel', 'pattern': None,
                   'type': 'message', 'data': b'hello'}


def test_disabled_bgsave(r):
    with pytest.raises(redis.ResponseError) as excinfo:
        r.bgsave()
    assert 'birdisle' in str(excinfo.value)


def test_disabled_bgrewriteaof(r):
    with pytest.raises(redis.ResponseError) as excinfo:
        r.bgrewriteaof()
    assert 'birdisle' in str(excinfo.value)


def test_enable_aof(r):
    with pytest.raises(redis.ResponseError) as excinfo:
        r.config_set('appendonly', 'yes')
    assert 'birdisle' in str(excinfo.value)


def test_config_string():
    server = birdisle.Server('dbfilename birdisletest.rdb')
    r = birdisle.redis.StrictRedis(server=server)
    dbfilename = r.config_get('dbfilename')['dbfilename']
    assert dbfilename == 'birdisletest.rdb'
    server.close()


def test_fd_leak(limit_fds):
    """Servers must not leak file descriptors"""
    for i in range(limit_fds + 1):
        server = birdisle.Server()
        client = server.connect()
        server.close()
        client.close()


def test_shared_server(server):
    a = birdisle.redis.StrictRedis(server=server)
    b = birdisle.redis.StrictRedis(server=server)
    a.flushall()
    b.flushall()
    a.set('foo', 'bar')
    assert b.get('foo') == b'bar'


@pytest.mark.skipif(redis.__version__ >= '3.0.0', reason="removed in redis-py 3.0")
def test_non_strict(server):
    r = birdisle.redis.Redis(server=server)
    r.zadd('foo', 'bar', 3)
    assert r.zrange('foo', 0, -1, withscores=True) == [(b'bar', 3)]


def test_signals(r, profile_timer):
    """Test that signal delivery doesn't interfere with birdisle"""
    def handler(signum, frame):
        pass

    profile_timer(1e-4, handler)
    data = b'?' * 10000
    for i in range(10000):
        r.set('foo', data)


def test_bad_config():
    with pytest.raises(RuntimeError):
        birdisle.Server('not a valid config file')
