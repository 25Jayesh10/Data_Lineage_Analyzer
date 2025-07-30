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
    try:
    # Load Tool 1 (index.json)
        with open(index_file) as f:
            index_data = json.load(f)

        # Load Tool 2 (ast.json)
        with open(ast_file) as f:
            ast_data = json.load(f)
    except Exception as e:
        print(f"Exception occured while opening the files {e}\n")

    # Store lineage relationships with metadata
    lineage = defaultdict(lambda: {"type": "", "calls": set()})

    print('\033[91m'+ str(type(ast_data))+'\033[0m')
    print("ast_data-\n",ast_data)
    

    # Track all known procedures and tables
    all_procedures = set()
    for item in ast_data:
         all_procedures.add(item.get("proc_name","not_defined"))  # handle error if proc_name is not found in an object. decide whether it is to be reported to the user or handled implictly
    another_set= set(index_data.keys())
    for item in another_set:
        all_procedures.add(item)

    print('\033[91m'+'\n'+ str(all_procedures) +'\033[0m')
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
    # New AST format: list of dicts, each with proc_name, statements, etc.
    # Build a mapping: proc_name -> ast_dict
    ast_proc_map = {}
    for proc_ast in ast_data:
        proc_name = proc_ast.get("proc_name")
        if proc_name:
            ast_proc_map[proc_name] = proc_ast
            lineage[proc_name]["type"] = "procedure"

    # For each procedure, analyze statements for table usage and procedure calls
    # We'll also build a usage map for tables
    table_usage = defaultdict(lambda: defaultdict(list))  # table_usage[table][proc] = ["read", "write"]

    for proc, ast in ast_proc_map.items():
        for stmt in ast.get("statements", []):
            stmt_type = stmt.get("type", "").upper()

            # Detect procedure calls (EXECUTE_PROCEDURE)
            if stmt_type == "EXECUTE_PROCEDURE":
                called_proc = stmt.get("procedure")
                # Only add if it's a procedure name, not a SQL statement
                if called_proc and called_proc.isidentifier():
                    lineage[proc]["calls"].add(called_proc)
                    lineage[called_proc]["type"] = "procedure"

            # Detect SELECT_INTO or SELECT (read)
            if stmt_type in ("SELECT_INTO", "SELECT"):
                query = stmt.get("query", "")
                # crude table detection: look for FROM <table>
                tokens = query.replace(",", " ").split()
                for i, token in enumerate(tokens):
                    if token.upper() == "FROM" and i + 1 < len(tokens):
                        table = tokens[i + 1].strip(';')
                        if not table.startswith("@"):  # skip variables
                            lineage[table]["type"] = "table"
                            lineage[table]["calls"].add(proc)
                            table_usage[table][proc].append("read")

            # Detect INSERT (write)
            if stmt_type == "EXECUTE_PROCEDURE":
                proc_sql = stmt.get("procedure", "")
                if proc_sql.upper().startswith("INSERT INTO"):
                    tokens = proc_sql.replace(",", " ").split()
                    if len(tokens) >= 3:
                        table = tokens[2].strip('();')
                        if not table.startswith("@"):  # skip variables
                            lineage[table]["type"] = "table"
                            lineage[table]["calls"].add(proc)
                            table_usage[table][proc].append("write")

            # Detect UPDATE (write)
            if stmt_type == "UPDATE":
                table = stmt.get("table")
                if table:
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append("write")

            # Detect DELETE (write)
            if stmt_type == "DELETE":
                table = stmt.get("table")
                if table:
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append("write")

    # Convert sets to sorted lists for output
    formatted_lineage = {}
    for key, value in lineage.items():
        formatted_lineage[key] = {
            "type": value["type"],
            "calls": sorted(value["calls"])
        }
        # Add usage info for tables
        if value["type"] == "table" and key in table_usage:
            formatted_lineage[key]["usage"] = {proc: sorted(set(ops)) for proc, ops in table_usage[key].items()}

    # Save output
    with open(output_file, "w") as f:
        json.dump(formatted_lineage, f, indent=2)

    print(f"✅ Lineage written to {output_file}")

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

    print(f"Lineage written to {output_file}")
