from redis.asyncio import Redis, ConnectionPool
from settings import redis_connection_string
from pickle import loads, dumps

pool = ConnectionPool.from_url(redis_connection_string)
databases = {
    'storage': 0,
    'ratelimits': 1,
}


class RedisClient:

    def __init__(self, database):
        self.connect = Redis(connection_pool=pool, db=database)

    async def get(self, key):
        return loads(await self.connect.get(key))

    async def set(self, key, value):
        return await self.connect.set(key, dumps(value))

    async def delete(self, key):
        return await self.connect.delete(key)


class Ratelimits(RedisClient):

    def __init__(self):
        super().__init__(databases['ratelimits'])


class Storage(RedisClient):

    def __init__(self):
        super().__init__(databases['storage'])

