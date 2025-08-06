# validator.py

import json
import sys
from jsonschema import validate, ValidationError

def validate_ast(ast_path, schema_path):
    print(f"📂 Loading AST file: {ast_path}")
    with open(ast_path, 'r') as ast_file:
        ast = json.load(ast_file)

    print(f"📂 Loading Schema file: {schema_path}")
    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)

    print("🔍 Starting schema validation...")

    try:
        validate(instance=ast, schema=schema)
        print("✅ AST is valid according to the schema.")
    except ValidationError as e:
        print("❌ AST validation failed.")
        print(f"📌 Error Message: {e.message}")
        print(f"📍 AST Path: {'/'.join(str(p) for p in e.path)}")
        print(f"📍 Schema Path: {'/'.join(str(p) for p in e.schema_path)}")
        sys.exit(1)
