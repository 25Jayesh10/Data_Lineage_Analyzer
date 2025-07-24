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

    all_nodes = set()
    edges = []

    # Iterate over each source node and its target nodes
    for source, targets in lineage.items():
        for target in targets:
            # For each relationship, create a Mermaid edge
            lines.append(f"    {source} --> {target}\n")

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
