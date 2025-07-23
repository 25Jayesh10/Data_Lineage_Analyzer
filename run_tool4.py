from src import analyze_lineage
import json
import os

def main():
    # Define file paths
    input_dir = "data"
    output_dir = "data"
    
    index_path = os.path.join(input_dir, "index.json")   # Tool 1 output
    ast_path = os.path.join(input_dir, "ast.json")       # Tool 2 output
    output_path = os.path.join(output_dir, "lineage.json")

    print("🔍 Starting Data Lineage Analysis...")
    analyze_lineage(index_path, ast_path, output_path)
    print("✅ Data Lineage Analysis complete.")
    with open(output_path, 'r') as f:
        lineage_data = json.load(f)

    # Pretty print to terminal
    print(json.dumps(lineage_data, indent=2))

if __name__ == "__main__":
    main()
