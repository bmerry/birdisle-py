#!/usr/bin/env python
import birdisle.redis

r = birdisle.redis.StrictRedis()
r.zadd('foo', bar=2, baz=3)
print(r.zcard('foo'))
