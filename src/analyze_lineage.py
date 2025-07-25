import json
from collections import defaultdict

def analyze_lineage(index_file, ast_file, output_file):
    """
    Build data lineage using Tool 1 and Tool 2 outputs.
    Output format:
    {
      "table_name": [procedures that access it],
      "procedure_name": [procedures it calls]
    }
    """
    # Load Tool 1 (index.json)
    with open(index_file) as f:
        index_data = json.load(f)

    # Load Tool 2 (ast.json)
    with open(ast_file) as f:
        ast_data = json.load(f)

    # Store lineage relationships with metadata
    lineage = defaultdict(lambda: {"type": "", "calls": set()})

    # Track all known procedures and tables
    all_procedures = set(index_data.keys()) | set(ast_data.keys())
    all_tables = set()

    # -------------------------------
    # Use Tool 1 data
    # -------------------------------
    for proc, meta in index_data.items():
        lineage[proc]["type"] = "procedure"
        for table in meta.get("tables", []):
            all_tables.add(table)
            lineage[table]["type"] = "table"
            lineage[table]["calls"].add(proc)
        for called_proc in meta.get("calls", []):
            lineage[proc]["calls"].add(called_proc)
            lineage[called_proc]["type"] = "procedure"
            all_procedures.add(called_proc)

    # -------------------------------
    # Use Tool 2 data (AST-based detection)
    # -------------------------------
    for proc in ast_data:
        lineage[proc]["type"] = "procedure"

    for proc, ast in ast_data.items():
        for stmt in ast.get("statements", []):
            stmt_upper = stmt.upper()

            # Detect procedure calls
            if stmt_upper.startswith("EXEC") or stmt_upper.startswith("EXECUTE"):
                parts = stmt.split()
                if len(parts) >= 2:
                    called_proc = parts[1].strip(';')
                    lineage[proc]["calls"].add(called_proc)
                    lineage[called_proc]["type"] = "procedure"

            # Detect tables in SQL
            tokens = stmt.replace(",", " ").split()
            keywords = {"FROM", "JOIN", "INTO", "UPDATE", "DELETE"}
            for i, token in enumerate(tokens):
                if token.upper() in keywords and i + 1 < len(tokens):
                    next_token = tokens[i + 1].strip(';')
                    # Skip variables (e.g., @product_id)
                    if not next_token.startswith("@"):
                        lineage[next_token]["type"] = "table"
                        lineage[next_token]["calls"].add(proc)

    # Convert sets to sorted lists for output
    formatted_lineage = {}
    for key, value in lineage.items():
        formatted_lineage[key] = {
            "type": value["type"],
            "calls": sorted(value["calls"])
        }

    # Save output
    with open(output_file, "w") as f:
        json.dump(formatted_lineage, f, indent=2)

    print(f"✅ Lineage written to {output_file}")
