import socket
import threading
import os
import struct

import redis
import redis.connection

from . import _birdisle


_lock = threading.Lock()   # Protects _meta_write
_meta_write = None


def _server(meta_read):
    argv_values = [_birdisle.ffi.new('char[]', b'redis'),
                   _birdisle.ffi.new('char[]', b'--port'),
                   _birdisle.ffi.new('char[]', b'6379')]
    argv = _birdisle.ffi.new("char *[4]", argv_values)
    _birdisle.lib.redisMain(meta_read, 3, argv)


def start():
    """Start the in-process redis server in a thread, if not already running."""
    global _meta_write
    with _lock:
        if _meta_write:
            return    # already running
        read, write = os.pipe()
        write = os.fdopen(write, 'wb')
        thread = threading.Thread(target=_server, args=[read])
        thread.daemon = True
        thread.start()
        _meta_write = write


def add_fd(fd):
    """Add an already-established connection to the redis server.

    The redis server takes ownership of the file descriptor. It should thus
    not belong to an existing Python object such as a socket.socket. If
    necessary, use os.dup.
    """
    with _lock:
        _meta_write.write(struct.pack('i', fd))
        _meta_write.flush()


def connect():
    """Create a connection and return the socket.

    This implicitly starts the server if necessary.
    """
    start()
    socks = list(socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM))
    # Python owns the FD within the socket, so to give ownership to redis
    # we have to duplicate it.
    fd = None
    try:
        fd = os.dup(socks[0].fileno())
        add_fd(fd)
        fd = None   # redis owns it now
        ret = socks[1]
        socks[1] = None   # success, so don't try to close it
        return ret
    finally:
        if socks[0] is not None:
            socks[0].close()
        if socks[1] is not None:
            socks[1].close()
        if fd is not None:
            os.close(fd)


class LocalSocketConnection(redis.connection.Connection):
    description_format = "LocalSocketConnection<db=%(db)s>"

    def __init__(self, db=0, password=None,
                 socket_timeout=None, encoding='utf-8',
                 encoding_errors='strict', decode_responses=False,
                 retry_on_timeout=False,
                 parser_class=redis.connection.DefaultParser, socket_read_size=65536):
        # This code is mostly copied from redis.connection.UnixConnection
        self.pid = os.getpid()
        self.db = 0
        self.password = password
        self.socket_timeout = socket_timeout
        self.retry_on_timeout = retry_on_timeout
        self.encoder = redis.connection.Encoder(encoding, encoding_errors, decode_responses)
        self._sock = None
        self._parser = parser_class(socket_read_size=socket_read_size)
        self._description_args = {
            'db': self.db
        }
        self._connect_callbacks = []

    def _connect(self):
        """Create a connection to in-process redis server"""
        sock = connect()
        sock.settimeout(self.socket_timeout)
        return sock

    def _error_message(self):
        # args for socket.error can either be (errno, "message")
        # or just "message"
        if len(exception.args) == 1:
            return "Error connecting to local redis: %s." % \
                (exception.args[0])
        else:
            return "Error %s connecting to local redis: %s. %s." % \
                (exception.args[0], exception.args[1])


def StrictRedis(*args, **kwargs):
    pool = redis.connection.ConnectionPool(connection_class=LocalSocketConnection)
    kwargs['connection_pool'] = pool
    return redis.StrictRedis(*args, **kwargs)
