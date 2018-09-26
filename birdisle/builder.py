#!/usr/bin/env python
import subprocess

from cffi import FFI


subprocess.check_call(['make', '-C', 'src'])


ffibuilder = FFI()
ffibuilder.cdef("""
    int redisMain(int metafd, int argc, char **argv);
""")

ffibuilder.set_source("birdisle._birdisle", """
    #include "birdisle.h"
""",
    libraries=['birdisle'],
    include_dirs=['src/src'],
    library_dirs=['src/src'],
    runtime_library_dirs=['src/src'])

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
