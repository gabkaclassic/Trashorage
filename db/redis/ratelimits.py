from .redis_client import RedisClient, databases
from datetime import datetime as dt, timedelta as td
from asyncio import run


class Ratelimits(RedisClient):
    __max_rpm = 30
    __timerange = td(minutes=1)
    __format = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        super().__init__(databases['ratelimits'])

    @classmethod
    async def create(cls):
        instance = cls()
        # if not await instance.connect.ping():
        #     exit(1)
        return instance

    @staticmethod
    def __get_now(to_string=False) -> dt | str:
        now = dt.now()
        return now.strftime(Ratelimits.__format) if to_string else now

    @staticmethod
    def __parse_date(date_string: str) -> dt:
        return dt.strptime(date_string.strip(), Ratelimits.__format)

    async def __reset_time(self, chat_id: str):

        await self.set(
            chat_id,
            {
                'requests': 1,
                'last_reset': Ratelimits.__get_now(to_string=True)
            }
        )

    async def check_user(self, chat_id: int):

        chat_id = str(chat_id)
        user_requests_info = await self.get(chat_id)
        now = Ratelimits.__get_now()

        if not user_requests_info:
            await self.__reset_time(chat_id)
            return True

        last_reset_str = user_requests_info.get('last_reset')
        last_reset = Ratelimits.__parse_date(last_reset_str)
        requests = int(user_requests_info.get('requests'))

        if now - last_reset > Ratelimits.__timerange:
            await self.__reset_time(chat_id)
            return True

        if requests < Ratelimits.__max_rpm:
            await self.set(
                chat_id,
                {
                    'requests': requests + 1,
                    'last_reset': last_reset_str,
                }
            )
            return True

        return False


ratelimits = run(Ratelimits.create())
