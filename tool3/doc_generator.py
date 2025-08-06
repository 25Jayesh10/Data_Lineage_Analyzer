import json
import os
from collections import Counter

def generate_anchor(proc_name):
    anchor = proc_name.lower().replace(" ", "-")
    return f"#stored-procedure-{anchor}"

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

def generate_summary(data):
    total_procedures = len(data)
    
    # Collect unique tables
    all_tables = set()
    for details in data.values():
        all_tables.update(details.get("tables", []))
    total_tables = len(all_tables)

    # Count how many times each proc is called
    call_counter = Counter()
    for details in data.values():
        call_counter.update(details.get("calls", []))

    most_called_proc = call_counter.most_common(1)[0][0] if call_counter else "N/A"

    summary = [
        "## Summary\n",
        f"**Total Procedures**: {total_procedures}  ",
        f"**Total Tables**: {total_tables}  ",
        f"**Most Called Procedure**: `{most_called_proc}`\n",
        "---\n\n"
    ]
    return "\n".join(summary)

def generate_toc(data):
    toc_lines = ["## Table of Contents\n"]
    for proc_name in data:
        anchor = generate_anchor(proc_name)
        toc_lines.append(f"- [{proc_name}]({anchor})")
    toc_lines.append("\n---\n\n")
    return "\n".join(toc_lines)

def generate_docs(json_path, output_dir="docs", output_file="procedures.md"):
    with open(json_path) as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    all_markdown = []

    # Add summary
    all_markdown.append(generate_summary(data))

    # Add TOC
    all_markdown.append(generate_toc(data))

    # Add procedure docs
    for proc_name, details in data.items():
        all_markdown.append(generate_markdown(proc_name, details))

    # Write to file
    full_doc = "\n".join(all_markdown)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w") as f:
        f.write(full_doc)

    print(f"Generated: {output_path}")

# Run the script
generate_docs("index.json")
