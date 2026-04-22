from dataclasses import dataclass
from datetime import datetime
from apiflask.fields import List, Integer, String
from typing import List as tList
from apiflask import APIFlask
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from model.types.core import Core
from model.util.util_query_bc import query_url, ServerCredentials, is_unknown_category
from util.schema import to_field, desc


@dataclass
class BCCategory:
    url_value: str = to_field(String(
        required=True,
        metadata=desc("URL value")
    ))
    categories: tList[str] = to_field(List(
        String(required=True, metadata=desc("Bluecoat Category")),
        required=True,
        metadata=desc("List of all Bluecoat Categories matched for the URL"),
    ))
    last_changed: int = to_field(Integer(
        required=True,
        metadata=desc("timestamp when bc categories where last updated")
    ))
    last_checked: int = to_field(Integer(
        required=True,
        metadata=desc("timestamp when BC categories where last fetched")
    ))

    def needs_refresh(self, ttl: int) -> bool:
        """
        Check if the category needs to be refreshed based on the last change and last check timestamps.

        :param ttl: Time to live in seconds.
        """
        ts_now = int(datetime.now().timestamp())
        max_age = ts_now - ttl
        return self.last_changed < max_age

    @staticmethod
    def batch_read(backend: DBInterface) -> tList['BCCategory']:
        raw_categories = backend.batch_fetch_obj(Core.read(backend).bc_categories)
        return [
            BCCategory(
                url_value=raw_cat["url_value"],
                categories=raw_cat["categories"],
                last_changed=raw_cat["last_changed"],
                last_checked=raw_cat["last_checked"],
            )
            for raw_cat in raw_categories
        ]

    @staticmethod
    def batch_read_lut(backend: DBInterface) -> dict[str, 'BCCategory']:
        return {
            cat.url_value: cat
            for cat in BCCategory.batch_read(backend)
        }

    @staticmethod
    def batch_write(backend: DBInterface, categories: tList['BCCategory']) -> tList[str]:
        return backend.batch_insert_obj([
            {
                "url_value": category.url_value,
                "categories": category.categories,
                "last_changed": category.last_changed,
                "last_checked": category.last_checked
            }
            for category in categories
        ])

    @staticmethod
    def batch_update(backend: DBInterface, app: APIFlask, urls: tList[str]) -> None:
        crds = ServerCredentials.from_env(app)

        # fetch all required data
        new_cats = {
            url: query_url(crds, url)
            for url in urls
        }
        current_cats = BCCategory.batch_read_lut(backend)
        ts_now = int(datetime.now().timestamp())

        for url, new_cat in new_cats.items():
            if is_unknown_category(new_cat):
                continue
            if url not in current_cats:
                current_cats[url] = BCCategory(
                    url_value=url,
                    categories=new_cats[url],
                    last_changed=ts_now,
                    last_checked=ts_now,
                )
            else:
                if set(current_cats[url].categories) != set(new_cat):
                    current_cats[url].last_changed = ts_now
                current_cats[url].categories = new_cat
                current_cats[url].last_checked = ts_now

        hashes = BCCategory.batch_write(backend, list(current_cats.values()))
        core = Core.read(backend)
        core.bc_categories = hashes
        core.write(backend)

bc_category_schema = class_schema(BCCategory)()


@dataclass
class TokenUsage:
    token_id: str
    last_used: int

    @staticmethod
    def new(token_id: str) -> 'TokenUsage':
        return TokenUsage(
            token_id=token_id,
            last_used=int(datetime.now().timestamp()),
        )

    @staticmethod
    def batch_read(backend: DBInterface) -> tList['TokenUsage']:
        raw_usages = backend.batch_fetch_obj(Core.read(backend).token_usages)
        return [
            TokenUsage(
                token_id=ru["token_id"],
                last_used=ru["last_used"],
            )
            for ru in raw_usages
        ]

    @staticmethod
    def batch_read_lut(backend: DBInterface) -> dict[str, 'TokenUsage']:
        return {
            u.token_id: u
            for u in TokenUsage.batch_read(backend)
        }

    @staticmethod
    def batch_write(backend: DBInterface, usages: tList['TokenUsage']) -> tList[str]:
        return backend.batch_insert_obj([
            {
                "token_id": u.token_id,
                "last_used": u.last_used,
            }
            for u in usages
        ])

    @staticmethod
    def track_access(backend: DBInterface, token_id: str):
        # fetch and update token usages
        token_metric_lut = TokenUsage.batch_read_lut(backend)
        token_metric_lut[token_id] = TokenUsage.new(token_id)
        hashes = TokenUsage.batch_write(backend, list(token_metric_lut.values()))
        # update core with new list
        core = Core.read(backend)
        core.token_usages = hashes
        core.write(backend)
