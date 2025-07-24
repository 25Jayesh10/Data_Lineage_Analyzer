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

    # Store lineage relationships
    lineage = defaultdict(set)

    # Track all known procedures (from both index and AST)
    all_procedures = set(index_data.keys()) | set(ast_data.keys())

    # -------------------------------
    # Use Tool 1 data
    # -------------------------------
    for proc, meta in index_data.items():
        for table in meta.get("tables", []):
            lineage[table].add(proc)  # Table -> Procedures
        for called_proc in meta.get("calls", []):
            lineage[proc].add(called_proc)
            all_procedures.add(called_proc)

    # -------------------------------
# Use Tool 2 data (AST-based detection)
# -------------------------------

# Ensure all procedures from AST are included
    for proc in ast_data:
        lineage.setdefault(proc, set())

    for proc, ast in ast_data.items():
        for stmt in ast.get("statements", []):
            stmt_upper = stmt.upper()

            # Detect procedure calls
            if stmt_upper.startswith("EXEC") or stmt_upper.startswith("EXECUTE"):
                parts = stmt.split()
                if len(parts) >= 2:
                        called_proc = parts[1].strip(';')
                        lineage[proc].add(called_proc)

            # Detect tables in SQL
            tokens = stmt.replace(",", " ").split()
            keywords = {"FROM", "JOIN", "INTO", "UPDATE", "DELETE"}
            for i, token in enumerate(tokens):
                if token.upper() in keywords and i + 1 < len(tokens):
                    next_token = tokens[i + 1].strip(';')
                    # Skip variables (e.g., @product_id)
                    if not next_token.startswith("@"):
                        lineage[next_token].add(proc)



    # Ensure all known procedures are included as keys (even if empty)
    for proc in all_procedures:
        lineage.setdefault(proc, set())

    # Convert sets to sorted lists for output
    lineage = {k: sorted(v) for k, v in lineage.items()}

    # Save output
    with open(output_file, "w") as f:
        json.dump(lineage, f, indent=2)

    print(f"✅ Lineage written to {output_file}")
