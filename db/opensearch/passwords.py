from asyncio import run
from .opensearch_client import OpenSearchClient
from crypt import Cipher


class Passwords(OpenSearchClient):

    def __init__(self):
        super().__init__('passwords')

    @classmethod
    async def create(cls):
        instance = cls()
        # await instance.check_index()
        return instance

    async def search_by_login(self, chat_id: int, login: str):
        return Cipher.decrypt(
            await self.search(
                True,
                'password',
                user=chat_id,
                login=login
            )
        )

    async def get_logins(self, chat_id: int):
        return await self.unique_values(
            'login',
            {'user': chat_id}
        )

    async def add_credentials(self, chat_id: int, login: str, password: str):
        return await self.create_document({
            'user': chat_id,
            'login': login,
            'password': Cipher.encrypt(password).decode(),
        })


passwords = run(Passwords.create())
