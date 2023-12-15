from typing import List
from asyncio import run
from .opensearch_client import OpenSearchClient


class Usefulness(OpenSearchClient):

    def __init__(self):
        super().__init__('usefulness')

    @classmethod
    async def create(cls):
        instance = cls()
        # await instance.check_index()
        return instance

    async def search_by_category(self, category: str):
        return await self.search(False, 'object', category=category)

    async def search_by_tags(self, chat_id: int, tags: List[str], category: str = None):
        filters = {'user': chat_id}
        if category:
            filters['category'] = category
        objects = await self.search_substrings_insensitive('tags', ['object'], tags, **filters)

        return objects

    async def search_by_user(self, chat_id: int):
        return await self.search(False, 'object', user=chat_id, one=False)

    async def get_categories(self, chat_id: int):
        categories = await self.unique_values('category', {'user': chat_id})
        return categories

    async def get_tags(self, chat_id: int, category: str = None):
        filters = {
            'user': chat_id
        }

        if category:
            filters.update({
                'category': category
            })

        tags = await self.unique_values('tags', filters, nested=True)

        return tags

    async def add_object(self, chat_id: int, category: str, tags: List[str], object: str):
        return await self.create_document({
            'user': chat_id,
            'category': category,
            'tags': tags,
            'object': object,
        })


storage = run(Usefulness.create())
