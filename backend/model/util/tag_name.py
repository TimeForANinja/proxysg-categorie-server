TAG_PRODUCTION = "tag_production"


def build_user_tag(user_id: str) -> str:
    return f"tag_user_{user_id}"
