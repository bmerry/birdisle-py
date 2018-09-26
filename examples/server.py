#!/usr/bin/env python
import contextlib
import socket
import os

import birdisle


def main():
    birdisle.start()
    s = socket.socket()
    s.bind(('127.0.0.1', 6380))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        with contextlib.closing(conn):
            fd = os.dup(conn.fileno())
            birdisle.add_fd(os.dup(conn.fileno()))


if __name__ == '__main__':
    main()
