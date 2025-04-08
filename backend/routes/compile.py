from datetime import datetime
from apiflask import APIBlueprint

from db.category import Category
from db.db_singleton import get_db


def find_subcategories(
        current_cat: Category,
        categories_dict: dict[str, Category],
        visited: set[str],
        result: list[Category]
):
    """
    This method is used to recursively traverse the nested categories.
    All categories that are in some form a sub category of the provided current_cat will be added to the result list.

    :param current_cat: The current category to start the traversal from
    :param categories_dict: A mapping of category IDs to category objects
    :param visited: A set to track already visited categories
    :param result: A list to store the found subcategories
    """
    for nested_id in current_cat.nested_categories:
        # resolve category id to category in lookup table
        nested_cat = categories_dict.get(nested_id)

        # make sure we could look up the nested category
        if not nested_cat:
            continue

        # make sure we did not yet visit the nested category
        # this should prevent infinite loops with circular nested categories
        if nested_cat.id in visited:
            continue

        # store cat in visited and result list
        visited.add(nested_cat.id)
        result.append(nested_cat)

        # call recursively for the nested cat
        find_subcategories(nested_cat, categories_dict, visited, result)

def calc_sub_cats(cat: Category, categories: list[Category]) -> list[Category]:
    """
    This method calculates all sub categories for the provided category.
    It's a wrapper around the find_subcategories method,
    which provides all variables for the initial call of the recursive func.

    :param cat: The category to calculate sub categories for
    :param categories: A list of all categories in the database
    :return: A list of all sub categories for the provided category
    """
    # Create a mapping of category IDs to category objects for quick lookup
    categories_dict = {category.id: category for category in categories}

    # List to store the subcategories
    result = []
    # Set to track already visited categories
    visited = set()

    # Start recursive traversal
    find_subcategories(cat, categories_dict, visited, result)

    return result


def add_compile_bp(app):
    compile_bp = APIBlueprint('compile', __name__)

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
            response += f'; Sub-Categories: {", ".join([c.name for c in sub_cats])}\n'
            response += f'define category "{cat.name}"\n'

            # fill in URLs that are part of the category
            for url in urls:
                if cat.id in url.categories:
                    response += f'  {url.hostname}\n'
                else:
                    # check if any of the sub-cats includes the url
                    for sub_cat in sub_cats:
                        if sub_cat.id in url.categories:
                            response += f'  {url.hostname} ; from sub-cat {sub_cat.name}\n'
                            break

            # end of category
            response += f'  ; end of {cat.name}\n'
            response += 'end category\n\n'

        return (
            response,
            200,
            {'Content-Type': 'text/plain'},
        )

    app.register_blueprint(compile_bp)
