import os
import json
import urllib.request
import sys

def main():
    base_url = "http://localhost:8080/openapi.json"
    output_dir = "apidocs"
    routes_dir = os.path.join(output_dir, "routes")
    schemas_dir = os.path.join(output_dir, "schemas")

    # a) creates a folder apidocs/
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(routes_dir, exist_ok=True)
    os.makedirs(schemas_dir, exist_ok=True)

    # b) downloads the openapi.json into it
    print(f"Downloading OpenAPI doc from {base_url}...")
    try:
        with urllib.request.urlopen(base_url) as response:
            if response.status != 200:
                print(f"Error: Received status code {response.status}")
                sys.exit(1)
            openapi_data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error downloading openapi.json: {e}")
        sys.exit(1)

    full_json_path = os.path.join(output_dir, "openapi.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        json.dump(openapi_data, f, indent=2)
    print(f"Saved full doc to {full_json_path}")

    # c) splits the large json into individual files routes/* and schemas/*
    # Split Paths (Routes)
    paths = openapi_data.get("paths", {})
    print(f"Splitting {len(paths)} routes...")
    for path, methods in paths.items():
        # Sanitize path name for filename
        filename = path.strip("/").replace("/", "_") or "root"
        route_path = os.path.join(routes_dir, f"{filename}.json")
        with open(route_path, "w", encoding="utf-8") as f:
            json.dump({path: methods}, f, indent=2)

    # Split Schemas
    components = openapi_data.get("components", {})
    schemas = components.get("schemas", {})
    print(f"Splitting {len(schemas)} schemas...")
    for schema_name, schema_content in schemas.items():
        schema_path = os.path.join(schemas_dir, f"{schema_name}.json")
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump({schema_name: schema_content}, f, indent=2)

    print("Successfully split OpenAPI document into individual files.")

if __name__ == "__main__":
    main()
