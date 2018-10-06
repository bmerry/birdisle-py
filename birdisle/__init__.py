import socket
import os
import warnings
import threading

import redis
import redis.connection

from . import _birdisle


_singleton_server = None
_singleton_lock = threading.Lock()


class Server(object):
    def __init__(self):
        self._handle = _birdisle.lib.birdisleStartServer()
        if self._handle == _birdisle.ffi.NULL:
            raise OSError(_birdisle.ffi.errno,
                          "Failed to create birdisle server")

    def add_connection(self, fd):
        if self._handle is None:
            raise RuntimeError("Server is already closed")
        _birdisle.lib.birdisleAddConnection(self._handle, fd)

    def connect(self):
        if self._handle is None:
            raise RuntimeError("Server is already closed")
        socks = list(socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM))
        # Python owns the FD within the socket, so to give ownership to
        # birdisle we have to duplicate it.
        fd = None
        try:
            fd = os.dup(socks[0].fileno())
            self.add_connection(fd)
            fd = None   # birdisle owns it now
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

    def close(self):
        if self._handle is None:
            raise RuntimeError("Server is already closed")
        ret = _birdisle.lib.birdisleStopServer(self._handle)
        self._handle = None
        if ret != 0:
            raise RuntimeError('birdisle server had exit code {}'.format(ret))

    def __del__(self):
        if self._handle is not None:
            self.close()


class LocalSocketConnection(redis.connection.Connection):
    description_format = "LocalSocketConnection<db=%(db)s>"

    def __init__(self, server, db=0, password=None,
                 socket_timeout=None, encoding='utf-8',
                 encoding_errors='strict', decode_responses=False,
                 retry_on_timeout=False,
                 parser_class=redis.connection.DefaultParser,
                 socket_read_size=65536):
        # This code is mostly copied from redis.connection.UnixConnection
        self.pid = os.getpid()
        self.db = 0
        self.password = password
        self.socket_timeout = socket_timeout
        self.retry_on_timeout = retry_on_timeout
        self.encoder = redis.connection.Encoder(
            encoding, encoding_errors, decode_responses)
        self._server = server
        self._sock = None
        self._parser = parser_class(socket_read_size=socket_read_size)
        self._description_args = {
            'db': self.db
        }
        self._connect_callbacks = []

    def _connect(self):
        """Create a connection to in-process redis server"""
        sock = self._server.connect()
        sock.settimeout(self.socket_timeout)
        return sock

    def _error_message(self, exception):
        # args for socket.error can either be (errno, "message")
        # or just "message"
        if len(exception.args) == 1:
            return "Error connecting to local redis: %s." % \
                (exception.args[0])
        else:
            return "Error %s connecting to local redis: %s. %s." % \
                (exception.args[0], exception.args[1])


class RedisMixin(object):
    def __init__(self, host='localhost', port=6379,
                 db=0, password=None, socket_timeout=None,
                 socket_connect_timeout=None,
                 socket_keepalive=None, socket_keepalive_options=None,
                 connection_pool=None, unix_socket_path=None,
                 encoding='utf-8', encoding_errors='strict',
                 charset=None, errors=None,
                 decode_responses=False, retry_on_timeout=False,
                 ssl=False, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs=None, ssl_ca_certs=None,
                 max_connections=None, server=None, singleton=True):
        if not connection_pool:
            # Adapted from redis-py
            if charset is not None:
                warnings.warn(DeprecationWarning(
                    '"charset" is deprecated. Use "encoding" instead'))
                encoding = charset
            if errors is not None:
                warnings.warn(DeprecationWarning(
                    '"errors" is deprecated. Use "encoding_errors" instead'))
                encoding_errors = errors

            if server is None:
                if singleton:
                    global _singleton_server
                    with _singleton_lock:
                        if _singleton_server is None:
                            _singleton_server = Server()
                        server = _singleton_server
                else:
                    server = Server()
            kwargs = {
                'db': db,
                'password': password,
                'socket_timeout': socket_timeout,
                'encoding': encoding,
                'encoding_errors': encoding_errors,
                'decode_responses': decode_responses,
                'retry_on_timeout': retry_on_timeout,
                'max_connections': max_connections,
                'connection_class': LocalSocketConnection,
                'server': server
            }
            connection_pool = redis.connection.ConnectionPool(**kwargs)
        super(RedisMixin, self).__init__(
            host, port, db, password, socket_timeout, socket_connect_timeout,
            socket_keepalive, socket_keepalive_options, connection_pool,
            unix_socket_path, encoding, encoding_errors, charset, errors,
            decode_responses, retry_on_timeout,
            ssl, ssl_keyfile, ssl_certfile, ssl_cert_reqs, ssl_ca_certs,
            max_connections)


class StrictRedis(RedisMixin, redis.StrictRedis):
    pass


class Redis(RedisMixin, redis.Redis):
    pass
