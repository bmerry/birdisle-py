from __future__ import absolute_import

import warnings

import redis
import redis.connection

import birdisle


class LocalSocketConnection(redis.connection.Connection):
    """Socket connection to a Birdisle server"""

    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    def repr_pieces(self):
        pieces = [
            ('db', self.db)
        ]
        if self.client_name:
            pieces.append(('client_name', self.client_name))
        return pieces

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
            return "Error %s connecting to local redis: %s." % \
                (exception.args[0], exception.args[1])


class RedisMixin(object):
    def __init__(self, server=None, host='localhost', port=6379,
                 db=0, password=None, socket_timeout=None,
                 socket_connect_timeout=None,
                 socket_keepalive=None, socket_keepalive_options=None,
                 connection_pool=None, unix_socket_path=None,
                 encoding='utf-8', encoding_errors='strict',
                 charset=None, errors=None,
                 decode_responses=False, retry_on_timeout=False,
                 ssl=False, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs='required', ssl_ca_certs=None,
                 ssl_check_hostname=False,
                 max_connections=None, single_connection_client=False,
                 health_check_interval=0, client_name=None, username=None):
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
                'username': username,
                'password': password,
                'socket_timeout': socket_timeout,
                'encoding': encoding,
                'encoding_errors': encoding_errors,
                'decode_responses': decode_responses,
                'retry_on_timeout': retry_on_timeout,
                'max_connections': max_connections,
                'health_check_interval': health_check_interval,
                'client_name': client_name,
                'connection_class': LocalSocketConnection,
                'server': server
            }
            connection_pool = redis.connection.ConnectionPool(**kwargs)
        super().__init__(
            host, port, db, password, socket_timeout, socket_connect_timeout,
            socket_keepalive, socket_keepalive_options, connection_pool,
            unix_socket_path, encoding, encoding_errors, charset, errors,
            decode_responses, retry_on_timeout,
            ssl, ssl_keyfile, ssl_certfile, ssl_cert_reqs, ssl_ca_certs,
            ssl_check_hostname, max_connections, single_connection_client,
            health_check_interval, client_name, username)


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
