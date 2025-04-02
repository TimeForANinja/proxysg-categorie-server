from typing import Optional, List, Mapping
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.url import URLDBInterface, MutableURL, URL


def _build_url(row: Mapping[str, any]) -> URL:
    return URL(
        id=row["_id"],
        hostname=row["hostname"],
        is_deleted=row["is_deleted"],
        categories=[
            x['cat']
            for x in row.get("categories", [])
            if x['is_deleted'] == 0
        ],
    )


class MongoDBURL(URLDBInterface):
    def __init__(self, db: Database[Mapping[str, any] | any]):
        self.db = db
        self.collection = self.db['urls']

    def create_table(self) -> None:
        pass

    def add_url(self, mut_url: MutableURL) -> URL:
        result = self.collection.insert_one({
            "hostname": mut_url.hostname,
            "is_deleted": 0,
            "categories": []
        })

        return URL(
            id=str(result.inserted_id),
            hostname=mut_url.hostname,
            is_deleted=0,
            categories=[]
        )

    def get_url(self, url_id: str) -> Optional[URL]:
        query = {"_id": ObjectId(url_id), "is_deleted": 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_url(row)

    def update_url(self, url_id: str, mut_url: MutableURL) -> URL:
        query = {"_id": ObjectId(url_id), "is_deleted": 0}
        update_fields = {
            "hostname": mut_url.hostname,
        }

        result = self.collection.update_one(query, {"$set": update_fields})

        if result.matched_count == 0:
            raise ValueError(f"URL with ID {url_id} not found or is deleted.")

        return self.get_url(url_id)

    def delete_url(self, url_id: str) -> None:
        query = {"_id": ObjectId(url_id), "is_deleted": 0}
        update = {"$set": {"is_deleted": 1}}
        result = self.collection.update_one(query, update)

        if result.matched_count == 0:
            raise ValueError(f"URL with ID {url_id} not found or already deleted.")

    def get_all_urls(self) -> List[URL]:
        rows = self.collection.find({ "is_deleted": 0 })
        return [
            _build_url(row)
            for row in rows
        ]
