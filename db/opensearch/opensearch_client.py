from opensearchpy import AsyncOpenSearch
from settings import opensearch_creds, opensearch_verify, opensearch_url
from uuid import uuid4
from logger import logger
from .decorators import create_index


class OpenSearchClient:

    def __init__(self, index):

        self.connection = AsyncOpenSearch(
            hosts=[opensearch_url],
            verify_certs=opensearch_verify,
            http_auth=opensearch_creds,
        )
        logger.info("Success connect to opensearch")
        self.index = index

    async def index_exists(self):
        try:
            return await self.connection.indices.exists(index=self.index)
        except Exception as e:
            logger.error(f"Error on connection to opensearch: {e}", exc_info=True)
            exit(0)

    async def check_index(self):
        if not await self.index_exists():
            try:
                await self.connection.indices.create(index=self.index)
                logger.info("Creating index...")
            except Exception as e:
                logger.error(f"Error on opensearch index creating: {e}", exc_info=True)

    @create_index()
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

        result = await self.connection.search(index=self.index, body=query)

        result = map(
            lambda document: document['_source'][field],
            result['hits']['hits']
        )
        unpacked_result = set()
        if nested:
            for res in result:
                for r in res:
                    unpacked_result.add(r)
        else:
            unpacked_result = set(result)

        return unpacked_result

    def __prepare_search_query(self, *fields, **matches):
        if not fields and not matches:
            return []

        search_query = {
            'query': {
                'bool': {
                    'must': []
                }
            },
            '_source': fields
        }

        if matches:
            matches = [{'match': {key: value}} for key, value in matches.items()]
            search_query['query']['bool']['must'].extend(matches)
        return search_query

    @create_index()
    async def search_one(self, *fields, **matches):

        search_query = self.__prepare_search_query(*fields, **matches)
        search_query['size'] = 1
        objects = await self.connection.search(index=self.index, body=search_query)
        objects = map(
            lambda document: document['_source'][fields[0]] if len(fields) == 1 else document['_source'],
            objects['hits']['hits']
        )

        return list(objects)[0]

    @create_index()
    async def search(self, *fields, **matches):

        search_query = self.__prepare_search_query(*fields, **matches)
        objects = await self.connection.search(index=self.index, body=search_query)
        objects = map(
            lambda document: document['_source'][fields[0]] if len(fields) == 1 else document['_source'],
            objects['hits']['hits']
        )

        return set(objects)

    @create_index()
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

    @create_index()
    async def create_document(self, document):

        return await self.connection.index(
            index=self.index,
            id=self.__generate_document_id(),
            body=document
        )
