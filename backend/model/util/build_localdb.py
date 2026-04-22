from datetime import datetime
from typing import List, Dict

from model.types.category import Category
from model.types.mappings import TokenCategoryMapping, URLCategoryMapping
from model.types.token import Token
from model.types.url import URL
from model.types.mappings import ChildCategoryMapping
from model.util.matching import unnest_categories, resolve_url_memberships

MATCH_CAT_ROOT = "root"



def build_localdb(
        token: Token,
        url_lut: Dict[str, URL],
        cat_lut: Dict[str, Category],
        cat_mappings: List[TokenCategoryMapping],
        url_mappings: List[URLCategoryMapping],
        child_cat_mappings: List[ChildCategoryMapping],
) -> str:
    # pre-filter mappings
    url_mappings = [
        m for m in url_mappings
        if not m.deactivated_by_constraint()
    ]

    # get cats for this token
    token_cats = [
        cat_lut[cmap.category_id]
        for cmap in cat_mappings
        if cmap.token_id == token.id
    ]

    # use response var to track the returned database string
    response = ""
    # write a header with some generic info
    response += "; Generated Categorisation File\n"
    response += f"; Generated on {datetime.now()}\n\n"

    for cat in token_cats:
        sub_cats = unnest_categories(cat, cat_lut, child_cat_mappings)

        # header for the category
        response += f"; Category: {cat.name}\n"
        sub_cat_names = [c.name for c in sub_cats if c.id != cat.id]
        response += f"; Nested Categories: {','.join(sub_cat_names)}\n"
        response += f"define category \"{cat.name}\"\n"

        # fill in URLs that are part of the category, or a sup-category
        relevant_urls = resolve_url_memberships(sub_cats, url_mappings)
        for url_id in relevant_urls.keys():
            relevant_cat_ids = relevant_urls[url_id]
            if cat.id in relevant_cat_ids:
                response += f"  {url_lut[url_id].url}\n"
            else:
                relevant_cat_names = [cat_lut[c].name for c in relevant_cat_ids]
                response += f"  {url_lut[url_id].url} ; from {','.join(relevant_cat_names)}\n"

        # end of category
        response += f"  ; end of {cat.name}\n"
        response += "end category\n\n"

    return response
