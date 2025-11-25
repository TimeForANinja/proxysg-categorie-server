from typing import Optional, Dict

from db.backend.abc.db import DBInterface
from db.dbmodel.category import Category
from db.dbmodel.token import Token
from db.dbmodel.url import URL
from db.backend.abc.util.types import MyTransactionType


class SessionCache:
    """
    SessionCache is a cache for requests made against the database.
    It allows for efficient retrieval of objects by ID, without having to query the database multiple times.
    """
    urls: Optional[Dict[str, URL]] = None
    tokens: Optional[Dict[str, Token]] = None
    categories: Optional[Dict[str, Category]] = None

    def __init__(
            self,
            main_db: DBInterface,
            session: MyTransactionType,
    ):
        self._main_db = main_db
        self.session = session


    def get_url(self, url_id: str) -> Optional[URL]:
        if self.urls is None:
            db_urls = self._main_db.urls.get_all_urls(session=self.session)
            self.urls = {x.id: x for x in db_urls}
        return self.urls.get(url_id)

    def update_url(self, url: URL):
        if self.urls is None:
            db_urls = self._main_db.urls.get_all_urls(session=self.session)
            self.urls = {x.id: x for x in db_urls}
        self.urls[url.id] = url


    def get_token(self, token_id: str) -> Optional[Token]:
        if self.tokens is None:
            db_token = self._main_db.tokens.get_all_tokens(session=self.session)
            self.tokens = {x.id: x for x in db_token}
        return self.tokens.get(token_id)

    def update_token(self, token: Token):
        if self.tokens is None:
            db_token = self._main_db.tokens.get_all_tokens(session=self.session)
            self.tokens = {x.id: x for x in db_token}
        self.tokens[token.id] = token


    def get_category(self, category_id: str) -> Optional[Category]:
        if self.categories is None:
            db_cats = self._main_db.categories.get_all_categories(session=self.session)
            self.categories = {x.id: x for x in db_cats}
        return self.categories.get(category_id)

    def update_category(self, category: Category):
        if self.categories is None:
            db_cats = self._main_db.categories.get_all_categories(session=self.session)
            self.categories = {x.id: x for x in db_cats}
        self.categories[category.id] = category
