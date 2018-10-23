import sys

# Avoid running aioredis tests on Python < 3.5, where the syntax is invalid
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append('test_aioredis.py')
