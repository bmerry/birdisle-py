from __future__ import absolute_import

import socket
import os

from . import _birdisle


class Server(object):
    def __init__(self, config=None):
        if config is None:
            config = ""
        if not isinstance(config, bytes):
            config = config.encode()
        self._handle = _birdisle.lib.birdisleStartServer(config)
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
