#!/bin/bash
set -e

if [ "$1" == "inside" ]; then
    mkdir -p "$HOME/birdisle"
    cp -a /birdisle "$HOME"
    cd "$HOME/birdisle"
    git clean -xdf
    rm -rf wheelhouse
    (cd src && git clean -xdf)
    make -C src -j8
    for PYBIN in /opt/python/*/bin; do
        "$PYBIN/pip" install -r requirements.txt
        "$PYBIN/pip" wheel . -w wheelhouse/
    done

    for whl in wheelhouse/birdisle*.whl; do
        auditwheel repair "$whl" -w /birdisle/wheelhouse
    done
else
    for image in quay.io/pypa/manylinux1_x86_64 quay.io/pypa/manylinux1_i686; do
        sudo docker run --rm -v $PWD:/birdisle "$image" /birdisle/mkwheels.sh inside
    done
fi
