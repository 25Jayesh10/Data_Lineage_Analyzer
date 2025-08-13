# import json
# import os
# import re

# def sanitize_for_mermaid(node_name):
#     """
#     Sanitizes a string to be a valid Mermaid.js node ID.
#     It replaces any character that is not a letter, number, or underscore
#     with an underscore. It also handles leading special characters.

#     Args:
#         node_name (str): The input string to sanitize.

#     Returns:
#         str: A sanitized string suitable for use as a Mermaid node ID.
#     """
#     if not isinstance(node_name, str):
#         return ""
#     # Replace any sequence of invalid characters with a single underscore
#     return re.sub(r'[^a-zA-Z0-9_]+', '_', node_name)

# def generate_mermaid_with_columns(lineage_path, output_path):
#     """
#     Generates a Mermaid.js diagram from a lineage JSON file,
#     representing tables as subgraphs that contain their accessed columns.
#     This version sanitizes all node names and deduplicates columns to prevent syntax errors.

#     Args:
#         lineage_path (str): The path to the input lineage.json file.
#         output_path (str): The path to the output .md file for the Mermaid diagram.
#     """
#     # Load the lineage.json content
#     try:
#         # Explicitly open with UTF-8 encoding to handle potential character issues
#         with open(lineage_path, "r", encoding="utf-8") as f:
#             lineage = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: The file '{lineage_path}' was not found.")
#         return
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON from '{lineage_path}'. Check for syntax errors or encoding issues.")
#         return

#     # Start building the Mermaid diagram with a Top-Down orientation
#     lines = ["graph TD\n"]

#     # Define styles for different node types for better visual distinction
#     lines.append("    %% Node styles\n")
#     lines.append("    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;\n")
#     lines.append("    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;\n")
#     lines.append("    classDef column fill:#fff,stroke:#333,stroke-width:1px,color:#000,font-style:italic;\n\n")

#     edges = set() # Use a set to automatically handle duplicate relationships
#     node_definitions = {} # Use a dictionary to avoid duplicate node definitions

#     # First, define all nodes, subgraphs, and collect the relationships (edges)
#     for name, meta in lineage.items():
#         node_type = meta.get("type")
#         sanitized_name = sanitize_for_mermaid(name)

#         if not sanitized_name:
#             continue

#         if node_type == "procedure":
#             # Define the stored procedure node using its sanitized ID and original name as label
#             node_definitions[sanitized_name] = f'    {sanitized_name}("{name}");\n    class {sanitized_name} stored_proc;\n'

#             # Collect edges that show this procedure accessing tables
#             for table_accessed in meta.get("tables", []):
#                 if table_accessed in lineage:
#                     sanitized_table = sanitize_for_mermaid(table_accessed)
#                     if sanitized_table:
#                         edges.add(f"    {sanitized_name} --> {sanitized_table};\n")

#         elif node_type == "table":
#             # Start the definition for the table subgraph, using original name as label
#             table_lines = [f'\n    subgraph {sanitized_name}["{name}"]\n']
            
#             # --- FIX: Deduplicate columns ---
#             unique_columns = {col_info['name']: col_info for col_info in meta.get("columns", [])}.values()

#             if unique_columns:
#                 for col_info in unique_columns:
#                     column_name = col_info.get("name")
#                     if not column_name:
#                         continue
                    
#                     # Sanitize the column name for its node ID
#                     sanitized_col_id = sanitize_for_mermaid(f"{name}_{column_name}")
                    
#                     table_lines.append(f'        {sanitized_col_id}("{column_name}");\n')
#                     table_lines.append(f"        class {sanitized_col_id} column;\n")
#             else:
#                 # If a table is listed but has no columns specified, add a placeholder
#                 placeholder_id = f"{sanitized_name}_placeholder"
#                 table_lines.append(f'        {placeholder_id}["(no columns specified)"];\n')
#                 table_lines.append(f"        class {placeholder_id} column;\n")

#             table_lines.append("    end\n")
#             # Store the complete subgraph definition
#             node_definitions[sanitized_name] = "".join(table_lines)

#     # Write all unique node and subgraph definitions to the main lines
#     lines.extend(sorted(node_definitions.values()))

#     # Add all collected edges to the diagram at the end for clarity
#     if edges:
#         lines.append("\n    %% Relationships\n")
#         lines.extend(sorted(list(edges)))

#     # Ensure the output directory exists
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     # Write the completed Mermaid lines into the output file
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.writelines(lines)

#     print(f"Mermaid diagram with column details saved to {output_path}")


# if __name__ == "__main__":
#     # Define paths relative to the script's location
#     # For local execution, create 'data' and 'diagrams' directories
#     project_root = os.path.dirname(os.path.abspath(__file__))
#     lineage_path = os.path.join(project_root, "data", "lineage.json")
#     mermaid_output_path = os.path.join(project_root, "diagrams", "lineage_diagram.md")

#     # Create dummy directories and file if they don't exist for the example to run
#     if not os.path.exists(os.path.dirname(lineage_path)):
#         os.makedirs(os.path.dirname(lineage_path))
#     if not os.path.exists(lineage_path):
#         with open(lineage_path, "w") as f:
#             f.write("{}") # Write empty json to prevent error on first run

#     # Generate the Markdown file with the detailed Mermaid code
#     generate_mermaid_with_columns(lineage_path, mermaid_output_path)

import json
import os
import re

def sanitize_for_mermaid(node_name):
    if not isinstance(node_name, str):
        return ""
    # Replace any sequence of invalid characters with a single underscore
    return re.sub(r'[^a-zA-Z0-9_]+', '_', node_name)

def generate_mermaid_with_columns(lineage_path, output_path):
    """
    Generates a Mermaid.js diagram from a lineage JSON file,
    representing tables as subgraphs that contain their accessed columns,
    including the type of access (read/write).

    Args:
        lineage_path (str): The path to the input lineage.json file.
        output_path (str): The path to the output .md file for the Mermaid diagram.
    """
    # Load the lineage.json content
    try:
        with open(lineage_path, "r", encoding="utf-8") as f:
            lineage = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{lineage_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{lineage_path}'. Check for syntax errors or encoding issues.")
        return

    # Start building the Mermaid diagram
    lines = ["graph TD\n"]

    # Define styles for different node types
    lines.append("    %% Node styles\n")
    lines.append("    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;\n")
    lines.append("    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;\n")
    # <--- MODIFIED: Added specific styles for read and write columns for better visual feedback
    lines.append("    classDef read_col fill:#d3f8d3,stroke:#2b802b,stroke-width:1px,color:#000;\n")
    lines.append("    classDef write_col fill:#f8d3d3,stroke:#c23b22,stroke-width:1px,color:#000;\n")
    lines.append("    classDef default_col fill:#fff,stroke:#333,stroke-width:1px,color:#000,font-style:italic;\n\n")

    edges = set()
    node_definitions = {}

    # First, define all nodes, subgraphs, and collect edges
    for name, meta in lineage.items():
        node_type = meta.get("type")
        sanitized_name = sanitize_for_mermaid(name)

        if not sanitized_name:
            continue

        if node_type == "procedure":
            # Define the stored procedure node
            node_definitions[sanitized_name] = f'    {sanitized_name}("{name}");\n    class {sanitized_name} stored_proc;\n'

            # Collect edges from procedure to tables it accesses
            for table_accessed in meta.get("tables", []):
                if table_accessed in lineage:
                    sanitized_table = sanitize_for_mermaid(table_accessed)
                    if sanitized_table:
                        # Link the procedure to the table's main subgraph
                        edges.add(f"    {sanitized_name} --> {sanitized_table};\n")

        elif node_type == "table":
            # Start the definition for the table subgraph
            table_lines = [f'\n    subgraph {sanitized_name}["{name}"]\n']
            
            # <--- MODIFIED: We iterate over all column operations, not just unique names
            columns_data = meta.get("columns", [])

            if columns_data:
                # <--- MODIFIED: Loop through all column operations to show each read/write
                for col_info in columns_data:
                    column_name = col_info.get("name")
                    usage = col_info.get("usage", "unknown") # e.g., 'read' or 'write'

                    if not column_name:
                        continue
                    
                    # <--- MODIFIED: Create a unique ID for each column operation to avoid Mermaid syntax errors
                    # e.g., "MyTable_ColumnA_read" and "MyTable_ColumnA_write" are now different
                    sanitized_col_id = sanitize_for_mermaid(f"{name}_{column_name}_{usage}")
                    
                    # <--- MODIFIED: Create a label that includes the usage type
                    node_label = f"{column_name} [{usage.upper()}]"
                    
                    # Define the column node with its new label
                    table_lines.append(f'        {sanitized_col_id}("{node_label}");\n')

                    # <--- MODIFIED: Apply the correct style based on usage
                    style_class = "default_col"
                    if usage == 'read':
                        style_class = 'read_col'
                    elif usage == 'write':
                        style_class = 'write_col'
                    table_lines.append(f"        class {sanitized_col_id} {style_class};\n")

            else:
                # If a table has no columns specified, add a placeholder
                placeholder_id = f"{sanitized_name}_placeholder"
                table_lines.append(f'        {placeholder_id}["(no columns specified)"];\n')
                table_lines.append(f"        class {placeholder_id} default_col;\n")

            table_lines.append("    end\n")
            # Store the complete subgraph definition
            node_definitions[sanitized_name] = "".join(table_lines)

    # Write all unique node and subgraph definitions
    lines.extend(sorted(node_definitions.values()))

    # Add all collected edges at the end
    if edges:
        lines.append("\n    %% Relationships\n")
        lines.extend(sorted(list(edges)))

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the completed Mermaid lines into the output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ Mermaid diagram with column access details saved to {output_path}")


if __name__ == "__main__":
    # Define paths relative to the script's location
    project_root = os.path.dirname(os.path.abspath(__file__))
    lineage_path = os.path.join(project_root, "data", "lineage.json")
    mermaid_output_path = os.path.join(project_root, "diagrams", "lineage_diagram.md")

    generate_mermaid_with_columns(lineage_path, mermaid_output_path)