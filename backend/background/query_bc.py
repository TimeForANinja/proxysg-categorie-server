import time
import requests
from dataclasses import dataclass
from typing import List

from db.dbmodel.url import NO_BC_CATEGORY_YET, FAILED_BC_CATEGORY_LOOKUP, FAILED_LOOKUP
from db.middleware.abc.db import MiddlewareDB
from log import log_info, log_error, log_debug


@dataclass
class ServerCredentials:
    """Utility Class to store all credentials for querying the Proxy server"""
    server: str
    user: str
    password: str
    verifySSL: bool

    def query(self, url: str):
        """Build a base URL which includes basic auth"""
        return f'https://{self.user}:{self.password}@{self.server}:8082/ContentFilter/TestUrl/{url}'

    def sanitized_query(self, url: str):
        """Build a base URL which does not include the password"""
        return f'https://{self.user}@{self.server}:8082/ContentFilter/TestUrl/{url}'

def is_unknown_category(bc_cats: List[str]) -> bool:
    """
    Method to check if a list of BlueCoat Categories is unknown

    A Category is unknown if:
    * no cat is set
    * only the NO_BC_CATEGORY_YET category is set
    * only 'unavailable' category is set
    * only 'query failed' category is set

    :param bc_cats: The list of BlueCoat Categories to check
    :return: True if the list is unknown, False otherwise
    """
    if len(bc_cats) == 0:
        return True
    if len(bc_cats) == 1 and bc_cats[0] == NO_BC_CATEGORY_YET:
        return True
    if len(bc_cats) == 1 and bc_cats[0] == FAILED_LOOKUP:
        return True
    # TODO: decide on how to continue with this (currently disabled by the 'false and')
    # Unavailable is used a) when BC Cat Services are offline
    # and b) when the URL / FQDN is not ratable (e.g.: IP)
    if False and len(bc_cats) == 1 and bc_cats[0] == FAILED_BC_CATEGORY_LOOKUP:
        return True
    return False

def query_all(db_if: MiddlewareDB, credentials: ServerCredentials, ttl: int):
    """
    Method to query all URLs in the DB for their BlueCoat Categories

    :param db_if: The DBInterface to use for the DB operations
    :param credentials: The credentials to use for the request
    :param ttl: The max TTL after which to force-refresh the rating
    """
    urls = db_if.urls.get_all_urls(bypass_cache=True)

    # calculate the cutoff time, after which we must refresh the item
    max_age = int(time.time()) - ttl

    # filter out all URLs that need an update
    scheduled_urls = [
        url for url in urls
        # check all URLs that have either not been (successfully) looked up,
        # or where the lookup was done before the TTL
        if is_unknown_category(url.bc_cats) or url.bc_last_set < max_age
    ]
    log_debug('background','planning update of BlueCoat categories', {
        'total': len(urls),
        'planned': len(scheduled_urls),
    })

    for url in scheduled_urls:
        # query the proxy for the categories
        bc_cats = do_query(credentials, url.hostname)

        if not (len(bc_cats) == 1 and bc_cats[0] == FAILED_LOOKUP):
            # since we update the TTL, we need to push even unchanged categories to the DB
            db_if.urls.set_bc_cats(url.id, bc_cats)

    log_info('background','Updated BlueCoat categories', {
        'total': len(urls),
        'updated': len(scheduled_urls),
    })

def do_query(credentials: ServerCredentials, url: str) -> List[str]:
    """
    Perform a basic request against the Database on a Bluecoat Proxy

    :param credentials: The credentials to use for the request
    :param url: The URL to query
    :return: A list of strings representing the categories of the URLs
    """

    try:
        response = requests.get(credentials.query(url), verify=credentials.verifySSL)
        response.raise_for_status()

        raw_content = response.text

        # the Category is a ';' separated list beginning with 'Blue Coat:'
        # There is a second one starting with the same name, which would include groups
        for line in raw_content.splitlines():
            if 'Blue Coat:' in line:
                categories = line.split('Blue Coat:')[1].strip().split('; ')
                return categories
        log_error(
            'background',
            'BlueCoat Category not found in Response',
            {'url': url, 'query': credentials.sanitized_query(url), 'response': raw_content }
        )
        return [FAILED_LOOKUP]
    except requests.RequestException as e:
        # TODO: this logs user/password as part of the request URL
        log_error(
            'background',
            'Error fetching BlueCoat Categories',
            {'url': url, 'query': credentials.sanitized_query(url), 'error': str(e)}
        )
        return [FAILED_LOOKUP]
