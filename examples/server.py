#!/usr/bin/env python

"""Run a redis server equivalent.

Note: don't use this in production! Use an actual redis server, which will do
things like making sure the data is persisted before shutdown.
"""

import contextlib
import socket
import os

import birdisle


def main():
    server = birdisle.Server()
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 6380))
    s.listen(5)
    try:
        while True:
            conn, addr = s.accept()
            with contextlib.closing(conn):
                server.add_connection(os.dup(conn.fileno()))
    except KeyboardInterrupt:
        server.close()


if __name__ == '__main__':
    main()
