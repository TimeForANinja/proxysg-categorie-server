from typing import List, Mapping, Any, Optional
from pymongo.synchronous.database import Database

from db.backend.abc.url_category import UrlCategoryDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.base_category_db import MongoDBBaseCategory


class MongoDBURLCategory(UrlCategoryDBInterface, MongoDBBaseCategory):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        super().__init__(db, 'urls', 'URL')

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        return self.get_categories_by_item(url_id)

    def add_url_category(self, url_id: str, category_id: str, session: Optional[MyTransactionType] = None):
        self.add_item_category(url_id, category_id, session=session)

    def delete_url_category(self, url_id: str, category_id: str, session: Optional[MyTransactionType] = None):
        self.delete_item_category(url_id, category_id, session=session)
