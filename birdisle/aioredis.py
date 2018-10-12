import asyncio

import aioredis

import birdisle


async def open_birdisle_connection(server=None, *,
                                   limit, loop=None,
                                   parser=None, **kwargs):
    # XXX: parser is not used (yet). That's inherited from aioredis,
    # not a birdisle deficiency.
    if server is None:
        server = birdisle.Server.singleton()
    sock = server.connect()
    try:
        if loop is None:
            loop = asyncio.get_event_loop()
        reader = aioredis.stream.StreamReader(limit=limit, loop=loop)
        protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
        transport, _ = await loop.create_connection(
            lambda: protocol, sock=sock, **kwargs)
    except Exception:
        sock.close()
        raise
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)
    return reader, writer


async def create_connection(server=None, *, db=None, password=None, ssl=None,
                            encoding=None, parser=None, loop=None,
                            timeout=None, connection_cls=None):
    if timeout is not None and timeout <= 0:
        raise ValueError("Timeout has to be None or a number greater than 0")

    if connection_cls:
        assert issubclass(connection_cls, aioredis.AbcConnection),\
                "connection_class does not meet the AbcConnection contract"
        cls = connection_cls
    else:
        cls = aioredis.RedisConnection

    if loop is None:
        loop = asyncio.get_event_loop()

    aioredis.log.logger.debug("Creating birdisle connection to %r", server)
    reader, writer = await asyncio.wait_for(open_birdisle_connection(
        server, ssl=ssl, limit=aioredis.connection.MAX_CHUNK_SIZE, loop=loop),
        timeout, loop=loop)

    conn = cls(reader, writer, encoding=encoding,
               address=server, parser=parser,
               loop=loop)

    try:
        if password is not None:
            await conn.auth(password)
        if db is not None:
            await conn.select(db)
    except Exception:
        conn.close()
        await conn.wait_closed()
        raise
    return conn


async def create_redis(server=None, *, commands_factory=aioredis.Redis, **kwargs):
    """Creates high-level Redis interface.

    This function is a coroutine.
    """
    conn = await create_connection(server, **kwargs)
    return commands_factory(conn)


class ConnectionsPool(aioredis.ConnectionsPool):
    def _create_new_connection(self, address):
        return create_connection(address,
                                 db=self._db,
                                 password=self._password,
                                 ssl=self._ssl,
                                 encoding=self._encoding,
                                 parser=self._parser_class,
                                 timeout=self._create_connection_timeout,
                                 connection_cls=self._connection_cls,
                                 loop=self._loop)


async def create_pool(server, *, pool_cls=None, **kwargs):
    if pool_cls is None:
        pool_cls = ConnectionsPool
    return await aioredis.create_pool(server, pool_cls=pool_cls, **kwargs)