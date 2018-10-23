#!/usr/bin/env python
import subprocess

from cffi import FFI


subprocess.check_call(['make', '-C', 'src'])


ffibuilder = FFI()
ffibuilder.cdef("""
    typedef struct birdisleServer birdisleServer;

    birdisleServer *birdisleStartServer(const char *config);
    int birdisleStopServer(birdisleServer *handle);
    void birdisleAddConnection(birdisleServer *handle, int fd);
""")

ffibuilder.set_source(
    "birdisle._birdisle", '#include "birdisle.h"\n',
    libraries=['birdisle'],
    include_dirs=['src/src'],
    library_dirs=['src/src'],
    runtime_library_dirs=['$ORIGIN/.libs'])

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
