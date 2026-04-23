import re
import ipaddress
from typing import List, Tuple, cast, Dict, Any


CACHE: Dict[str, Any] ={}


def get_tld_list() -> Tuple[List[str], str]:
    global CACHE
    if "TLD_LIST" not in CACHE:
        # load list
        with open("./dist/tlds-alpha-by-domain.txt", "r") as f:
            raw_list = [
                line.strip() for line in f.readlines()
            ]
            CACHE["TLD_COMMENT"] = raw_list[0][1:].strip()
            CACHE["TLD_LIST"] = raw_list[1:]
    return cast(List[str], CACHE["TLD_LIST"]), cast(str, CACHE["TLD_COMMENT"])


def is_public_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_global:
            return True
    except ValueError:
        pass
    # default to false for everything else
    return False


def get_su_list() -> Tuple[List[str], str]:
    global CACHE
    if "SU_LIST" not in CACHE:
        # load list
        with open("./dist/special-use-domain.csv", "r") as f:
            raw_list = [
                cast(re.Match[str], re.match(r"(^\S+)\.", line.strip())).group(1)
                for line in f.readlines()[1:]
                if re.match(r"(^\S+)\.", line)
            ]
            CACHE["SU_LIST"] = raw_list[1:]
    return cast(List[str], CACHE["SU_LIST"]),  "RFC6761 Special-Use Domain Names"
