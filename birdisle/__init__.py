from __future__ import absolute_import

import socket
import os
import threading

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

    @staticmethod
    def singleton():
        global _singleton_server
        with _singleton_lock:
            if _singleton_server is None:
                _singleton_server = Server()
            return _singleton_server

    def __del__(self):
        # During interpreter shutdown, _birdisle may have been reset
        # to None.
        if self._handle is not None and _birdisle is not None and _birdisle.lib is not None:
            self.close()
