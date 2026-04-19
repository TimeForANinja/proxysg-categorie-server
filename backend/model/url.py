from hmac import new
from typing import Optional, cast, List, Dict, Set
from apiflask import APIFlask

from db.abc.db import DBInterface
from model.types.core import Commit
from model.types.mappings import URLCategoryMapping, ChildCategoryMapping
from model.util.error import ModelError, CanError
from model.types.url import URL
from model.util.find import find_in_lists, find_all_in_lists
from model.util.matching import best_match_url, unnest_categories
from model.util.util_query_bc import ServerCredentials, FAILED_LOOKUP, query_url
from routes.types.url import RestTestResult, RestURLDetail, RestConstrainedCategory
from util.branch_names import BRANCH_PROD


class URLModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_urls(self, branch: str) -> List[RestURLDetail]:
        """Fetch a list of all URLs"""
        head_commit = Commit.read_branch(self.backend, branch)

        # Fetch LUTs
        url_lut = head_commit.head.url_lut(self.backend)
        category_lut = head_commit.head.category_lut(self.backend)

        # create base-objects for every URL
        data: Dict[str, RestURLDetail] = {
            url_id: RestURLDetail(
                url=url_lut[url_id],
                categories=[],
            )
            for url_id in url_lut
        }

        # fill our category properties based on our mappings
        mappings = URLCategoryMapping.batch_read(self.backend, head_commit.head.url_category_mappings)
        for mapping in mappings:
            data[mapping.url_id].categories.append(
                RestConstrainedCategory(
                    category=category_lut[mapping.category_id],
                    constraint=mapping.constraint,
                )
            )

        return list(data.values())

    def create_url(self, branch: str, value: str, description: str) -> URL:
        """Create a new URL"""
        commit = Commit.read_branch(self.backend, branch)

        # create url
        new_url = URL.new(value, description)
        new_url_hash = URL.batch_write(self.backend, [new_url])[0]

        # update commit with new url
        commit.head.urls.append(new_url_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)

        return new_url

    def update_url(
            self,
            branch: str, url_id: str,
            value: Optional[str],
            description: Optional[str],
    ) -> CanError[URL]:
        """Update the value of an existing URL"""
        commit = Commit.read_branch(self.backend, branch)

        url, url_hash = find_in_lists(
            URL.batch_read(self.backend, commit.head.urls),
            commit.head.urls,
            lambda u: u.id == url_id
        )
        if not url:
            return None, ModelError("URL not found")

        # update url
        if value:
            url.url = value
        if description:
            url.description = description
        new_url_hash = URL.batch_write(self.backend, [url])[0]

        # update commit with new url
        commit.head.urls.remove(url_hash)
        commit.head.urls.append(new_url_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return url, None

    def delete_url(self, branch: str, url_id: str) -> Optional[ModelError]:
        """Delete a URL by ID"""
        commit = Commit.read_branch(self.backend, branch)

        url, url_hash = find_in_lists(
            URL.batch_read(self.backend, commit.head.urls),
            commit.head.urls,
            lambda u: u.id == url_id
        )
        if not url:
            return ModelError("URL not found")

        # update commit, removing the url
        commit.head.urls.remove(url_hash)
        self._remove_url_related(commit, url_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None

    def _remove_url_related(self, commit: Commit, url_id: str) -> None:
        mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        # filter out all hashes that use this token
        _, keep_hashes = find_all_in_lists(
            mappings,
            commit.head.url_category_mappings,
            lambda m: m.url_id != url_id
        )
        commit.head.url_category_mappings = keep_hashes


    def test_urls(self, app: APIFlask, urls: List[str]) -> List[RestTestResult]:
        # TODO: properly parallelize this to reduce DB load
        return [self._test_url(app, url) for url in urls]

    def _test_url(self, app: APIFlask, url: str) -> RestTestResult:
        # 1) Normalize input to a hostname
        hostname = url.strip().lower()

        # 2) Fetch all URLs and select the best match by comparing the longest suffix that matched
        head_commit = Commit.read_branch(self.backend, BRANCH_PROD)
        url_lut = head_commit.head.url_lut(self.backend)
        best_match = best_match_url(hostname, url_lut.values())

        # 3) Fetch all categories that match the best match
        cat_lut = head_commit.head.category_lut(self.backend)
        matching_cat_ids: Set[str] = set()
        if best_match:
            direct_matching_mappings, _ = find_all_in_lists(
                URLCategoryMapping.batch_read(self.backend, head_commit.head.url_category_mappings),
                head_commit.head.url_category_mappings,
                lambda m: m.url_id == cast(URL, best_match).id
            )
            direct_matching_cats = set(m.category_id for m in direct_matching_mappings)
            matching_cat_ids.update(direct_matching_cats)
            # unnest to also get all Partents of the matched categories
            child_cat_map = ChildCategoryMapping.batch_read(self.backend, head_commit.head.child_category_mappings)
            matching_cat_ids.update([
                parent_cat.id
                for c_id in direct_matching_cats
                for parent_cat in unnest_categories(
                    cat_lut[c_id],
                    cat_lut,
                    child_cat_map,
                    True,
                )
            ])

        # 4) Query BlueCoat category for the provided hostname
        try:
            credentials = ServerCredentials.from_env(app)
            bc_categories = query_url(credentials, hostname)
        except Exception:
            bc_categories = [FAILED_LOOKUP]

        return RestTestResult(
            input=url,
            normalized_input=hostname,
            matched_url=best_match.url if best_match else "N/A",
            local_categories=[cat_lut[cat_id] for cat_id in matching_cat_ids],
            bc_categories=bc_categories,
        )
