import json
import logging
from jsonschema import Draft202012Validator

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Paths to index and schema files
INDEX_PATH = "data/index.json"
SCHEMA_PATH = "data/indexSchema.json"

def load_json_file(path):
    logger.debug(f"Loading JSON file from: {path}")
    try:
        with open(path, "r") as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded: {path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON file {path}: {e}")
        return None

def validate_index(index_data, schema_data):
    logger.debug("Initializing Draft 2020-12 JSON Schema Validator.")
    validator = Draft202012Validator(schema_data)
    errors = sorted(validator.iter_errors(index_data), key=lambda e: e.path)

    if not errors:
        logger.info("✅ Validation successful: index.json conforms to schema.")
        return True
    else:
        logger.error("❌ Validation failed with the following errors:")
        for error in errors:
            path = " → ".join(str(p) for p in error.absolute_path)
            logger.error(f"[{path}] {error.message}")
        return False

def validate():
    logger.info("🔍 Validating index.json against index_schema.json...")
    index_data = load_json_file(INDEX_PATH)
    schema_data = load_json_file(SCHEMA_PATH)

    if index_data is None or schema_data is None:
        logger.error("Aborting validation: Could not load input or schema file.")
        return False

    return validate_index(index_data, schema_data)

if __name__ == "__main__":
    success = validate()
    exit(0 if success else 1)
