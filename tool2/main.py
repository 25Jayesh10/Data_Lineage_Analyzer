# main.py

import sys
from ast_generator import generate_ast, save_ast
from validator import validate_ast  # ✅ Import validator

def main():
    """
    Main function to run the AST generator from the command line.
    """
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_sql_file> <output_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"🚀 Starting AST generation for: {input_file}")

    try:
        print("📥 Reading input SQL file...")
        ast = generate_ast(input_file)

        if ast is None:
            print("❌ AST generation failed — returned None.")
            sys.exit(1)

        print(f"📤 Saving AST to file: {output_file}")
        save_ast(ast, output_file)
        print(f"✅ AST successfully saved to {output_file}")

        # ✅ Validate the AST
        schema_file = "schema/ast_schema.json"  # Update if in another path
        print(f"🧪 Validating AST against schema: {schema_file}")
        validate_ast(output_file, schema_file)

    except Exception as e:
        print(f"❌ An unexpected error occurred during processing:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
