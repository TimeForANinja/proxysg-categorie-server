from datetime import datetime

from apiflask import APIBlueprint

from db.category import Category
from db.db_singleton import get_db

compile_bp = APIBlueprint('compile', __name__)

def find_subcategories(
        current_cat: Category,
        categories_dict: dict[int, Category],
        visited: set[int],
        result: list[Category]
):
    for nested_id in current_cat.nested_categories:
        # resolve category id to category in lookup table
        nested_cat = categories_dict.get(nested_id)

        # make sure we could lookup the nested category
        if not nested_cat:
            continue

        # make sure we did not yet visit the nested category
        # this should prevent infinite loops with circular nested categories
        if nested_cat.id in visited:
            continue

        # store cat in visited and result list
        visited.add(current_cat.id)
        result.append(current_cat)

        # call recursively for the nested cat
        find_subcategories(nested_cat, categories_dict, visited, result)

def calc_sub_cats(cat: Category, categories: list[Category]) -> list[Category]:
    # Create a mapping of category IDs to category objects for quick lookup
    categories_dict = {category.id: category for category in categories}

    # List to store the subcategories
    result = []
    # Set to track already visited categories
    visited = set()

    # Start recursive traversal
    find_subcategories(cat, categories_dict, visited, result)

    return result


@compile_bp.get("/api/compile/<string:token_uuid>")
@compile_bp.doc(summary="Compile Categories", description="Compile Categories for the provided Token")
def handle_compile(token_uuid: str):
    db_if = get_db()
    token = db_if.tokens.get_token_by_uuid(token_uuid)
    if not token:
        return (
            "Token not found",
            404,
            {'Content-Type': 'text/plain'},
        )

    db_if.tokens.update_usage(token.id)

    # load all categories that are part of the token
    categories = db_if.categories.get_all_categories()
    token_cats = [cat for cat in categories if cat.id in token.categories]

    # fetch all URLs
    urls = db_if.urls.get_all_urls()

    # use response var to track the returned database string
    response = ""
    # write a header with some generic info
    response += '; Generated Categorisation File\n'
    response += f'; Generated on {datetime.now()}\n\n'

    for cat in token_cats:
        # calculate subcategories (excluding the "root" cat itself)
        sub_cats = calc_sub_cats(cat, categories)

        # header for the category
        response += f'; Category: {cat.name}\n'
        response += f'; Description: {cat.description}\n'
        response += f'; Sub-Categories: {', '.join([c.name for c in sub_cats])}\n'
        response += f'define category "{cat.name}"\n'

        # fill in URLs that are part of the category
        for url in urls:
            if cat.id in url.categories:
                response += f'  {url.hostname}\n'
            elif any(sub_cat.id in url.categories for sub_cat in sub_cats):
                response += f'  {url.hostname} ; from sub-cat {cat.name}\n'

        # end of category
        response += f'  ; end of {cat.name}\n'
        response += 'end category\n\n'

    return (
        response,
        200,
        {'Content-Type': 'text/plain'},
    )
