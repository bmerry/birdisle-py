#!/usr/bin/env python
import birdisle

r = birdisle.StrictRedis()
r.zadd('foo', bar=2, baz=3)
print(r.zcard('foo'))
