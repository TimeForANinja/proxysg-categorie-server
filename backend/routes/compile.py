from datetime import datetime

from apiflask import APIBlueprint
from db.db_singleton import get_db

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
        # header for the category
        response += f'; Category: {cat.name}\n'
        response += f'; Description: {cat.description}\n'
        response += f'define category "{cat.name}"\n'

        # fill in URLs that are part of the category
        for url in urls:
            if cat.id in url.categories:
                response += f'  {url.hostname}\n'

        # end of category
        response += f'  ; end of {cat.name}\n'
        response += 'end category\n\n'

    return (
        response,
        200,
        {'Content-Type': 'text/plain'},
    )
