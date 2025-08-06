import json
import os

def generate_markdown(proc_name, details):
    md = []
    md.append(f"# Stored Procedure:\n**{proc_name}**\n\n---\n")

    # Parameters
    md.append("## Parameters\n")
    md.append("| Name | Type |\n|------|------|")
    for param in details.get("params", []):
        md.append(f"| {param['name']} | {param['type']} |")
    md.append("\n---\n")

    # Tables
    md.append("## Tables\n")
    for table in details.get("tables", []):
        md.append(f"- {table}")
    md.append("\n---\n")

    # Called Procedures
    md.append("## Called Procedures\n")
    for proc in details.get("calls", []):
        md.append(f"- {proc}")
    md.append("\n---\n")

    # Call Graph - Mermaid
    md.append("## Call Graph\n")
    md.append("```mermaid\ngraph TD")
    for proc in details.get("calls", []):
        md.append(f"    {proc_name} --> {proc}")
    for table in details.get("tables", []):
        md.append(f"    {proc_name} --> {table}")
    md.append("```\n\n---\n")

    # No 'description' in schema, so placeholder
    md.append("## Business Logic\n")
    md.append("No description provided.\n")

    # Separator between procedures
    md.append("\n---\n\n")

    return "\n".join(md)

def generate_docs(json_path, output_dir="docs", output_file="procedures.md"):
    with open(json_path) as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    all_markdown = []
    for proc_name, details in data.items():
        markdown = generate_markdown(proc_name, details)
        all_markdown.append(markdown)

    # Join all procedure docs and write to a single file
    full_doc = "\n".join(all_markdown)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w") as f:
        f.write(full_doc)

    print(f"Generated: {output_path}")

# Run it
generate_docs("index.json")
