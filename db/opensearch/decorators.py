import functools
from opensearchpy.exceptions import NotFoundError


def create_index():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            self = args[0]

            try:
                return await func(*args, **kwargs)
            except NotFoundError:
                await self.check_index()
                return await func(*args, **kwargs)

        return wrapper

    return decorator
