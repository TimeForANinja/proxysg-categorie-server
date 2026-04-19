import enum

# for supersets, split by the first N charakters of the hash
KEY_LENGTH = 2

# max size to insert into a single document
MAX_COMPACT_LIST_SIZE = 100

# constants used to store the type of a list in the db
TYPE_KEY = "_type"

class TypeIDs(str, enum.Enum):
    TYPE_ID_LIST_SMALL = "id_list_small@v1"
    TYPE_ID_LIST_LARGE = "id_list_large@v1"
    TYPE_ID_CATEGORY = "id_category@v1"
    TYPE_ID_URL = "id_url@v1"
    TYPE_ID_TOKEN = "id_token@v1"
    TYPE_ID_CORE = "id_core@v1"
    TYPE_ID_COMMIT = "id_commit@v1"
    TYPE_ID_STATE_TREE = "id_state_tree@v1"
    TYPE_ID_TOKEN_CAT_MAP = "id_token_category_map@v1"
    TYPE_ID_URL_CAT_MAP = "id_url_category_map@v1"
