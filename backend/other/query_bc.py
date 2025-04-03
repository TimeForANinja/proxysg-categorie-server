import time
import requests
from dataclasses import dataclass
from typing import List

from db.db_singleton import get_db
from db.url import NO_BC_CATEGORY_YET


@dataclass
class ServerCredentials:
    """Utility Class to store all credentials for querying the Proxy server"""
    server: str
    user: str
    password: str
    verifySSL: bool

    def base_url(self):
        """Build a base URL which includes basic auth"""
        return f"https://{self.user}:{self.password}@{self.server}:8082"

def query_all(creds: ServerCredentials, unknown_only: bool):
    db_if = get_db()

    urls = db_if.urls.get_all_urls()

    for url in urls:
        # if unknown_only is set we only want to check elements where
        # no cat is set, or only the NO_BC_CATEGORY_YET cat is set
        no_bc_cats = len(url.bc_cats) == 0
        only_tbd_cats = len(url.bc_cats) == 1 and url.bc_cats[0] == NO_BC_CATEGORY_YET
        if unknown_only and not no_bc_cats and not only_tbd_cats:
            continue

        # query the proxy for the categories
        bc_cats = do_query(creds, url.hostname)

        # if they changed -> push to database
        if set(bc_cats) != set(url.bc_cats):
            db_if.urls.set_bc_cats(url.id, bc_cats)

    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Finished updating BlueCoat categories for all URLs")

def do_query(creds: ServerCredentials, url: str) -> List[str]:
    """
    Perform a basic request against the Database on a Bluecoat Proxy

    :param creds: The credentials to use for the request
    :param url: The URL to query
    :return: A list of strings representing the categories of the URLs
    """

    # URL endpoint for the request
    req_url = f"{creds.base_url()}/ContentFilter/TestUrl/{url}"

    try:
        response = requests.get(req_url, verify=creds.verifySSL)
        response.raise_for_status()

        raw_content = response.text

        # the Category is a ";" separated list beginning with "Blue Coat:"
        # There is a second one starting with the same name, which would include groups
        for line in raw_content.splitlines():
            if "Blue Coat:" in line:
                categories = line.split("Blue Coat:")[1].strip().split("; ")
                return categories
        print("No BlueCoat categories found in Response")
        return []
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []
