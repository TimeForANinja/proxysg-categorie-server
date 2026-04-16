from datetime import datetime
from typing import List

from model.types.category import Category
from model.types.mappings import TokenCategoryMapping, URLCategoryMapping
from model.types.token import Token
from model.types.url import URL


def build_localdb(
        token: Token,
        urls: List[URL],
        categories: List[Category],
        cat_mappings: List[TokenCategoryMapping],
        url_mappings: List[URLCategoryMapping]
) -> str:
    cat_lut = {cat.id: cat for cat in categories}
    url_lut = {url.id: url for url in urls}

    token_cats = [
        cat_lut[cmap.category_id]
        for cmap in cat_mappings
        if cmap.token_id == token.id
    ]

    # use response var to track the returned database string
    response = ''
    # write a header with some generic info
    response += '; Generated Categorisation File\n'
    response += f'; Generated on {datetime.now()}\n\n'

    for cat in token_cats:
        # header for the category
        response += f'; Category: {cat.name}\n'
        response += f'define category "{cat.name}"\n'

        # fill in URLs that are part of the category
        for umap in url_mappings:
            if umap.category_id == cat.id:
                url = url_lut[umap.url_id]
                response += f'  {url.url}\n'

        # end of category
        response += f'  ; end of {cat.name}\n'
        response += 'end category\n\n'

    return response
