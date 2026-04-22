import requests
from dataclasses import dataclass
from typing import List, cast
import urllib3
from apiflask import APIFlask
from pyrad import host

from util.log import log_error


# Value returned by BC if the Category-Service is not working
FAILED_BC_CATEGORY_LOOKUP = "unavailable"
# Value used when a Lookup Failed
FAILED_LOOKUP = "query failed"


@dataclass
class ServerCredentials:
    """Utility Class to store all credentials for querying the Proxy server"""
    server: str
    user: str
    password: str
    http_timeout: int
    verifySSL: bool

    def query(self, url: str):
        """Build a base URL which includes basic auth"""
        return f"https://{self.user}:{self.password}@{self.server}:8082/ContentFilter/TestUrl/{url}"

    def sanitized_query(self, url: str):
        """Build a base URL which does not include the password"""
        return f"https://{self.user}@{self.server}:8082/ContentFilter/TestUrl/{url}"

    @staticmethod
    def from_env(app: APIFlask) -> 'ServerCredentials':
        """Build a ServerCredentials object from a config dict"""
        query_bc_conf: dict = app.config.get("BC", {})

        bc_host = query_bc_conf.get("HOST", None)
        bc_user = query_bc_conf.get("USER", None)
        bc_password = query_bc_conf.get("PASSWORD", None)
        if not bc_host or not bc_user or not bc_password:
            raise ValueError("BC Host, User or Password not set")

        if not query_bc_conf.get("VERIFY_SSL", "true").lower() != "false":
            # hide warnings telling us to enable ssl verification
            urllib3.disable_warnings()

        return ServerCredentials(
            server=cast(str, bc_host),
            user=cast(str, bc_user),
            password=cast(str, bc_password),
            # timeout for the query against the bc proxy. should be below 30 seconds or else the /test api route will timeout
            http_timeout=int(query_bc_conf.get("TIMEOUT", "10")),
            # check for false or not false, so that we default to "true" for all other values
            verifySSL=query_bc_conf.get("VERIFY_SSL", "true").lower() != "false"
        )


def is_unknown_category(bc_cats: List[str]) -> bool:
    """
    Method to check if a list of BlueCoat Categories is unknown

    A Category is unknown if:
    * no cat is set
    * only "unavailable" category is set
    * only "query failed" category is set

    :param bc_cats: The list of BlueCoat Categories to check
    :return: True if the list is unknown, False otherwise
    """
    if len(bc_cats) == 0:
        return True
    if len(bc_cats) == 1 and bc_cats[0] == FAILED_LOOKUP:
        return True
    # TODO: decide on how to continue with this (currently disabled by the "false and")
    # Unavailable is used a) when BC Cat Services are offline
    # and b) when the URL / FQDN is not ratable (e.g.: IP)
    if False and len(bc_cats) == 1 and bc_cats[0] == FAILED_BC_CATEGORY_LOOKUP:
        return True
    return False


def query_url(credentials: ServerCredentials, url: str) -> List[str]:
    """
    Perform a basic request against the Database on a Bluecoat Proxy

    :param credentials: The credentials to use for the request
    :param url: The URL to query
    :return: A list of strings representing the categories of the URLs
    """

    try:
        response = requests.get(
            credentials.query(url),
            verify=credentials.verifySSL,
            timeout=credentials.http_timeout
        )
        response.raise_for_status()

        raw_content = response.text

        # the Category is a ";" separated list beginning with "Blue Coat:"
        # There is a second one starting with the same name, which would include groups
        for line in raw_content.splitlines():
            if "Blue Coat:" in line:
                categories = line.split("Blue Coat:")[1].strip().split("; ")
                return categories

        log_error(
            "MODEL",
            "BlueCoat Category not found in Response",
            {"url": url, "query": credentials.sanitized_query(url), "response": raw_content }
        )
        return [FAILED_LOOKUP]
    except requests.RequestException as e:
        log_error(
            "MODEL",
            "Error fetching BlueCoat Category",
            {"url": url, "query": credentials.sanitized_query(url), "error": str(e)}
        )
        return [FAILED_LOOKUP]
