import argparse
import dbm
import json
from db.abc.constants import TYPE_KEY
from db.util.simple_bson import bson_decode

def dump_db(db_path, filter_type=None):
    try:
        with dbm.open(db_path, 'r') as db:
            print(f"Dumping database: {db_path}" + (f" (filtered by: {filter_type})" if filter_type else ""))
            print("-" * 40)

            # Iterate through all keys in the dbm database
            for key in db.keys():
                value_bytes = db[key]
                try:
                    # Parse data using the project's bson_decode
                    data = bson_decode(value_bytes)

                    # Filter by type if a filter is provided
                    if filter_type:
                        # Some entries might be lists directly, but usually they are dicts with TYPE_KEY
                        if isinstance(data, dict):
                            actual_type = data.get(TYPE_KEY)
                            if actual_type != filter_type:
                                continue
                        else:
                            # If it's not a dict, it doesn't have a TYPE_KEY in the usual way for filtering
                            continue

                    # Convert to string for better display (e.g. JSON)
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                    print(f"Key: {key_str}")
                    print(f"Value: {json.dumps(data, indent=2)}")
                    print("-" * 20)
                except Exception as e:
                    print(f"Error decoding key {key}: {e}")

    except Exception as e:
        print(f"Failed to open database {db_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump the contents of a dbm database.")
    parser.add_argument("--db_path", type=str, nargs="?", default="data/mydatabase.dbm", help="Path to the dbm database file")
    parser.add_argument("--filter_type", type=str, nargs="?", default=None, help="Type ID to filter the output (e.g. id_category@v1)")

    args = parser.parse_args()
    dump_db(args.db_path, args.filter_type)
