import json
import os

def generate_mermaid(lineage_path, output_path):
    """
    Generates a Mermaid.js diagram file from lineage.json.

    Args:
        lineage_path (str): Path to the lineage.json file.
        output_path (str): Path to save the generated lineage.mmd file.
    """
    # Load the lineage.json content
    with open(lineage_path, "r") as f:
        lineage = json.load(f)

    # Start building Mermaid diagram inside a Markdown code block
    lines = ["graph TD\n"]

    lines.append("    %% Node styles\n")
    lines.append("    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;\n")
    lines.append("    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;\n")

    all_nodes = set()
    edges = []

    # Iterate over each source node and its target nodes
    for source, targets in lineage.items():
        for target in targets:
            # For each relationship, create a Mermaid edge
            lines.append(f"    {source} --> {target}\n")
            all_nodes.add(source)
            all_nodes.add(target)

    # Apply styles to nodes
    tables = [node for node in all_nodes if not node.startswith('sp_')]
    stored_procs = [node for node in all_nodes if node.startswith('sp_')]
    
    if tables:
        lines.append(f"    class {','.join(tables)} table;\n")
    if stored_procs:
        lines.append(f"    class {','.join(stored_procs)} stored_proc;\n")
        
    # Write the lines into the .mmd output file
    with open(output_path, "w") as f:
        f.writelines(lines)

    print(f"✅ Mermaid diagram saved to {output_path}")

if __name__ == "__main__":
    # Define default paths assuming the tool runs from project root
    lineage_path = os.path.join("data", "lineage.json")
    mermaid_output_path = os.path.join("diagrams", "lineage.md")

    # Generate the Markdown file with Mermaid code
    generate_mermaid(lineage_path, mermaid_output_path)
