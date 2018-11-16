from __future__ import absolute_import

import warnings
import os

import redis
import redis.connection

import birdisle


class LocalSocketConnection(redis.connection.Connection):
    """Socket connection to a Birdisle server"""
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
        self._buffer_cutoff = 6000

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
                 max_connections=None, server=None):
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
                server = birdisle.Server()
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
    """Replacement for :class:`redis.StrictRedis` that connects to a birdisle server.

    :param server: Server state (keyword only). If unspecified, a new one is created.
    :type server: :class:`birdisle.Server`
    """
    pass


class Redis(RedisMixin, redis.Redis):
    """Replacement for :class:`redis.Redis` that connects to a birdisle server.

    :param server: Server state (keyword only). If unspecified, a new one is created.
    :type server: :class:`birdisle.Server`
    """
    pass
