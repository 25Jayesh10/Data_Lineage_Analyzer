from src.analyze_lineage import analyze_lineage
from src.generate_mermaid import generate_mermaid
from src.convert_mmd_to_md import convert_mmd_to_md
import json
import os

def main():
    # Define file paths
    input_dir = "data"
    output_dir = "data"
    diagram_dir = "diagrams"
    
    index_path = os.path.join(input_dir, "index.json")   # Tool 1 output
    ast_path = os.path.join(input_dir, "ast.json")       # Tool 2 output
    output_path = os.path.join(output_dir, "lineage.json")  # Tool 4 output
    mermaid_path = os.path.join(diagram_dir, "lineage.mmd") # Mermaid diagram output
    markdown_path = os.path.join(diagram_dir, "lineage.md")    # Mermaid .md file
    
    print("🔍 Starting Data Lineage Analysis...")
    analyze_lineage(index_path, ast_path, output_path)
    print("✅ Data Lineage Analysis complete.")
    with open(output_path, 'r') as f:
        lineage_data = json.load(f)

    # Pretty print to terminal
    print(json.dumps(lineage_data, indent=2))

    print("🖼️ Generating Mermaid diagram...")
    generate_mermaid(output_path, mermaid_path)
    convert_mmd_to_md(mermaid_path, markdown_path)

if __name__ == "__main__":
    main()
