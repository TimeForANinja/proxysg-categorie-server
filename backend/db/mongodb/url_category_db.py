from typing import List, Mapping, Any, Tuple
from pymongo.synchronous.database import Database

from db.url_category import UrlCategoryDBInterface
from db.mongodb.base_category_db import MongoDBBaseCategory


class MongoDBURLCategory(UrlCategoryDBInterface, MongoDBBaseCategory):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        super().__init__(db, 'urls', 'URL')

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        return self.get_categories_by_item(url_id)

    def add_url_category(self, url_id: str, category_id: str) -> None:
        self.bulk_add_url_category([(url_id, category_id)])

    def bulk_add_url_category(self, sets: List[Tuple[str, str]]) -> None:
        self.bulk_add_item_category(sets)

    def delete_url_category(self, url_id: str, category_id: str) -> None:
        self.delete_item_category(url_id, category_id)
