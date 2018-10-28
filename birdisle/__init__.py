from __future__ import absolute_import

import socket
import os

from . import _birdisle
from ._version import __version__     # noqa: F401


class Server(object):
    """Birdisle server instance.

    This is a lower-level interface to Birdisle. Most users will only use the
    constructor directly, and then pass instances to the higher-level
    wrappers.

    :param config: Configuration file content
    :type config: str or bytes
    """
    def __init__(self, config=None):
        if config is None:
            config = ""
        if not isinstance(config, bytes):
            config = config.encode()
        self._handle = _birdisle.lib.birdisleStartServer(config)
        if self._handle == _birdisle.ffi.NULL:
            errno = _birdisle.ffi.errno
            self._handle = None
            if errno:
                raise OSError(errno,
                              "Failed to create birdisle server")
            else:
                raise RuntimeError("Failed to create birdisle server")

    def add_connection(self, fd):
        """Give the server a new client socket.

        Ownership of the given file descriptor is passed to the C code, and
        the Python code must not attempt to close it. In particular, do not
        directly pass the fileno of a :class:`socket.socket` without
        duplicating it.

        This is a low-level function that may be useful to connect Birdisle to
        an existing socket (e.g. a TCP socket). Most users will use
        :meth:`connect` instead.

        :param fd: File descriptor that the server will own
        :type fd: int
        """
        if self._handle is None:
            raise RuntimeError("Server is already closed")
        _birdisle.lib.birdisleAddConnection(self._handle, fd)

    def connect(self):
        """Create a new connection to the server.

        :return: File descriptor for the client end of a socket pair
        :rtype: int
        """
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
        """Shut down the server and free the resources.

        This method can be called multiple times, but no other methods
        should be called after this one.

        :raises RuntimeError: if the server did not shut down cleanly
        """
        if self._handle is None:
            return    # Already closed
        ret = _birdisle.lib.birdisleStopServer(self._handle)
        self._handle = None
        if ret != 0:
            raise RuntimeError('birdisle server had exit code {}'.format(ret))

    def __del__(self):
        # During interpreter shutdown, _birdisle may have been reset
        # to None.
        if (self._handle is not None
                and _birdisle is not None
                and _birdisle.lib is not None):
            self.close()
