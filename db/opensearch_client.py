from typing import List
from asyncio import run
from opensearchpy import AsyncOpenSearch
from settings import opensearch_creds, opensearch_verify, opensearch_url
from uuid import uuid4
from itertools import chain


class OpenSearchClient:

    def __init__(self, index):

        self.connection = AsyncOpenSearch(
            hosts=[opensearch_url],
            verify_certs=opensearch_verify,
            http_auth=opensearch_creds,
        )
        print('connection: ', self.connection)
        self.index = index

    async def index_exists(self):
        try:
            return await self.connection.indices.exists(index=self.index)
        except Exception as e:
            print('Connection error: ', e)
            exit(0)

    async def check_index(self):
        if not await self.index_exists():
            try:
                await self.connection.indices.create(index=self.index)
                print('created')
            except Exception as e:
                print(e)
        else:
            print('Already exists')  # TODO

    async def unique_values(self, field, matches=None, nested=False):

        if nested:
            query = {
                "aggs": {
                    "unique_values": {
                        "nested": {
                            "path": field,
                        },
                        "aggs": {
                            "terms_agg": {
                                "terms": {
                                    "field": f"{field}.keyword",
                                }
                            }
                        }
                    }
                }
            }
        else:
            query = {
                'aggs': {
                    'unique_values': {
                        'terms': {
                            'field': f'{field}.keyword'
                        },
                    }
                },
            }
        if matches:
            matches = [{'match': {field: value}} for field, value in matches.items()]
            query.update({
                'query': {
                    'bool': {
                        'must': matches
                    }
                }
            })

        return await self.connection.search(index=self.index, body=query)

    async def search(self, *fields, **matches):

        if not fields and not matches:
            return []

        search_query = {
            'query': {
                'match': matches
            },
            '_source': fields
        }

        objects = await self.connection.search(index=self.index, body=search_query)

        return set(map(
            lambda document: document['_source'][fields[0]] if len(fields) == 1 else document['_source'],
            objects['hits']['hits']
        ))

    async def search_substrings_insensitive(self, field, fields, substrings, **matches):

        if not substrings and not matches:
            return []

        includes = [
            {
                "regexp": {
                    f"{field}.keyword": f".*{substring}.*"
                }
            }
            for substring in substrings
        ]
        matches = [{'match': {key: value}} for key, value in matches.items()]
        search_query = {
            'query': {
                'bool': {
                    'must': []
                }
            },
        }

        if fields:
            search_query['_source'] = fields

        if includes:
            search_query['query']['bool']['must'].extend(includes)
        if matches:
            search_query['query']['bool']['must'].extend(matches)

        objects = await self.connection.search(index=self.index, body=search_query)

        return set(map(
            lambda document: document['_source'][fields[0]] if len(fields) == 1 else document['_source'],
            objects['hits']['hits']
        ))
    def __generate_document_id(self):
        return str(uuid4())

    async def create_document(self, document):

        return await self.connection.index(
            index=self.index,
            id=self.__generate_document_id(),
            body=document
        )


class Usefulness(OpenSearchClient):

    def __init__(self):
        super().__init__('usefulness')

    @classmethod
    async def create(cls):
        instance = cls()
        # await instance.check_index()
        return instance

    async def search_by_category(self, category: str):
        return await self.search('object', category=category)

    async def search_by_tags(self, chat_id: int, tags: List[str], category: str = None):
        filters = {'user': chat_id}
        if category:
            filters['category'] = category
        objects = await self.search_substrings_insensitive('tags', ['object'], tags, **filters)

        return objects
    async def search_by_user(self, chat_id: int):
        return await self.search('object', user=chat_id)

    async def get_categories(self, chat_id: int):
        categories = await self.unique_values('category', {'user': chat_id})
        return set(map(lambda document: document['_source']['category'], categories['hits']['hits']))

    async def get_tags(self, chat_id: int, category: str = None):
        filters = {
            'user': chat_id
        }

        if category:
            filters.update({
                'category': category
            })

        tags = await self.unique_values('tags', filters)

        return set(chain(*map(lambda document: document['_source']['tags'], tags['hits']['hits'])))

    async def add_object(self, chat_id: int, category: str, tags: List[str], object: str):
        return await self.create_document({
            'user': chat_id,
            'category': category,
            'tags': tags,
            'object': object,
        })


storage = run(Usefulness.create())
