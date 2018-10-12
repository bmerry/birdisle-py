from async_generator import yield_, async_generator
import pytest

import birdisle.aioredis


@pytest.fixture
@async_generator
async def server():
    server = birdisle.Server()
    await yield_(server)
    server.close()


@pytest.fixture
@async_generator
async def conn(server):
    conn = await birdisle.aioredis.create_connection(server)
    await yield_(conn)
    conn.close()
    await conn.wait_closed()


@pytest.fixture
@async_generator
async def pool(server):
    pool = await birdisle.aioredis.create_pool(server)
    await yield_(pool)
    pool.close()
    await pool.wait_closed()


@pytest.fixture
@async_generator
async def r(server):
    redis = await birdisle.aioredis.create_redis(server)
    await yield_(redis)
    redis.close()
    await redis.wait_closed()


@pytest.mark.asyncio
async def test_create_connection(conn):
    await conn.execute('set', 'hello', 'create_redis')
    val = await conn.execute('get', 'hello')
    assert val == b'create_redis'


@pytest.mark.asyncio
async def test_create_pool(pool):
    await pool.execute('set', 'hello', 'create_pool')
    val = await pool.execute('get', 'hello')
    assert val == b'create_pool'


@pytest.mark.asyncio
async def test_create_redis(r):
    await r.set('hello', 'world')
    val = await r.get('hello')
    assert val == b'world'
