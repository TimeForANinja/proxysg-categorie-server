from typing import Optional, List, Mapping, Any
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.abc.url import MutableURL, URL, NO_BC_CATEGORY_YET, URLDBInterface


def _build_url(row: Mapping[str, Any]) -> URL:
    """build a URL object from a MongoDB document"""
    return URL(
        id=str(row['_id']),
        hostname=row['hostname'],
        description=row['description'],
        is_deleted=row['is_deleted'],
        categories=[
            x['cat']
            for x in row.get('categories', [])
            if x['is_deleted'] == 0
        ],
        bc_cats=row['bc_cats'],
    )


class MongoDBURL(URLDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['urls']

    def add_url(self, mut_url: MutableURL, url_id: str) -> URL:
        self.collection.insert_one({
            '_id': ObjectId(url_id),
            'hostname': mut_url.hostname,
            'description': mut_url.description,
            'is_deleted': 0,
            'categories': [],
            'bc_cats': [NO_BC_CATEGORY_YET],
        })

        return URL(
            id=url_id,
            hostname=mut_url.hostname,
            description=mut_url.description,
            is_deleted=0,
            categories=[],
            bc_cats=[NO_BC_CATEGORY_YET],
        )

    def get_url(self, url_id: str) -> Optional[URL]:
        query = {'_id': ObjectId(url_id), 'is_deleted': 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_url(row)

    def update_url(self, url_id: str, mut_url: MutableURL) -> URL:
        query = {'_id': ObjectId(url_id), 'is_deleted': 0}
        update_fields = {
            'hostname': mut_url.hostname,
            'description': mut_url.description,
        }

        result = self.collection.update_one(query, {'$set': update_fields})

        if result.matched_count == 0:
            raise ValueError(f'URL with ID {url_id} not found or is deleted.')

        return self.get_url(url_id)

    def set_bc_cats(self, url_id: str, bc_cats: List[str]) -> None:
        query = {'_id': ObjectId(url_id), 'is_deleted': 0}
        update = {'$set': {'bc_cats': bc_cats}}
        result = self.collection.update_one(query, update)

        if result.matched_count == 0:
            raise ValueError(f'URL with ID {url_id} not found or already deleted.')

    def delete_url(self, url_id: str) -> None:
        query = {'_id': ObjectId(url_id), 'is_deleted': 0}
        update = {'$set': {'is_deleted': 1}}
        result = self.collection.update_one(query, update)

        if result.matched_count == 0:
            raise ValueError(f'URL with ID {url_id} not found or already deleted.')

    def get_all_urls(self) -> List[URL]:
        rows = self.collection.find({ 'is_deleted': 0 })
        return [
            _build_url(row)
            for row in rows
        ]
