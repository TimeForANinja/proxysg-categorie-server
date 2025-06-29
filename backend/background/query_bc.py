import requests
from dataclasses import dataclass
from typing import List

from db.db_singleton import get_db
from db.dbmodel.url import NO_BC_CATEGORY_YET, FAILED_BC_CATEGORY_LOOKUP
from log import log_info, log_error


@dataclass
class ServerCredentials:
    """Utility Class to store all credentials for querying the Proxy server"""
    server: str
    user: str
    password: str
    verifySSL: bool

    def base_url(self):
        """Build a base URL which includes basic auth"""
        return f'https://{self.user}:{self.password}@{self.server}:8082'

def is_unknown_category(bc_cats: List[str]) -> bool:
    """
    Method to check if a list of BlueCoat Categories is unknown

    A Category is unknown if:
    * no cat is set
    * only the NO_BC_CATEGORY_YET category is set
    * only 'unavailable' cat is set

    :param bc_cats: The list of BlueCoat Categories to check
    :return: True if the list is unknown, False otherwise
    """
    if len(bc_cats) == 0:
        return True
    if len(bc_cats) == 1 and bc_cats[0] == NO_BC_CATEGORY_YET:
        return True
    # TODO: decide on how to continue with this (currently disabled by the 'false and')
    # Unavailable is used a) when BC Cat Services are offline
    # and b) when the URL / FQDN is not ratable (e.g. IP)
    if False and len(bc_cats) == 1 and bc_cats[0] == FAILED_BC_CATEGORY_LOOKUP:
        return True
    return False

def query_all(creds: ServerCredentials, unknown_only: bool):
    """
    Method to query all URLs in the DB for their BlueCoat Categories

    :param creds: The credentials to use for the request
    :param unknown_only: If True, only URLs with unknown BlueCoat Categories will be queried
    """
    db_if = get_db()

    urls = db_if.urls.get_all_urls()

    scheduled_urls = [
        url for url in urls
        # if unknown_only is set, we only want to check not yet looked up / where the prev lookup failed
        if not unknown_only or is_unknown_category(url.bc_cats)
    ]

    for url in scheduled_urls:
        # query the proxy for the categories
        bc_cats = do_query(creds, url.hostname)

        # if they changed -> push to the database
        if set(bc_cats) != set(url.bc_cats):
            db_if.urls.set_bc_cats(url.id, bc_cats)

    log_info('background','Updated BlueCoat categories', {
        'mode': 'only_unknown' if unknown_only else 'all',
        'total': len(urls),
        'updated': len(scheduled_urls),
    })

def do_query(creds: ServerCredentials, url: str) -> List[str]:
    """
    Perform a basic request against the Database on a Bluecoat Proxy

    :param creds: The credentials to use for the request
    :param url: The URL to query
    :return: A list of strings representing the categories of the URLs
    """

    # URL endpoint for the request
    req_url = f'{creds.base_url()}/ContentFilter/TestUrl/{url}'

    try:
        response = requests.get(req_url, verify=creds.verifySSL)
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
            {'url': url, 'response': raw_content }
        )
        return []
    except requests.RequestException as e:
        # TODO: this logs user/password as part of the request URL
        log_error(
            'background',
            'Error fetching BlueCoat Categories',
            {'url': url, 'error': str(e)}
        )
        return []
