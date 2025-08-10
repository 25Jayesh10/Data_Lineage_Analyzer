import json
from collections import defaultdict

def analyze_lineage(index_file :str, ast_file :str, output_file :str):
    def extract_table_from_query(query):
        # crude extraction: look for FROM <table>
        if not query:
            return None
        tokens = query.replace(",", " ").upper().split()
        for i, token in enumerate(tokens):
            if token == "FROM" and i + 1 < len(tokens):
                table = tokens[i + 1].strip(';')
                if not table.startswith("@"):
                    return table
        return None

    def extract_columns_from_select_query(query):
        """Crude extraction of column names from a SELECT clause in a raw query string."""
        if not query:
            return ["*"]
        query_upper = query.upper()
        try:
            select_index = query_upper.find("SELECT")
            from_index = query_upper.find("FROM")
            if select_index == -1 or from_index == -1 or from_index < select_index:
                 return ["*"]

            # Extract the string between SELECT and FROM
            cols_str = query[select_index + 6:from_index].strip()
            if not cols_str or cols_str == '*':
                return ["*"]
            
            # Split by comma and clean up names
            return [c.strip() for c in cols_str.split(',')]
        except Exception:
            return ["*"]

    def process_statements(proc: str, stmts: list, table_usage: defaultdict, lineage: defaultdict):
        """Recursively processes AST statements to find table and column usage."""
        if not stmts:
            return

        for stmt in stmts:
            stmt_type = stmt.get("type", "").upper()

            # Handle structured DML statements
            if stmt_type == "SELECT":
                table = stmt.get("from")
                if table:
                    columns = stmt.get("columns", ["*"])
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append({"op": "read", "cols": columns})
            
            elif stmt_type == "SELECT_INTO":
                query = stmt.get("query", "")
                table = extract_table_from_query(query)
                if table:
                    columns = extract_columns_from_select_query(query)
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append({"op": "read", "cols": columns})

            elif stmt_type == "UPDATE":
                table = stmt.get("table")
                if table:
                    # For UPDATE, the columns are the keys of the "set" object
                    columns = list(stmt.get("set", {}).keys()) or ["*"]
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append({"op": "write", "cols": columns})
            
            elif stmt_type == "INSERT": # Corrected from "INSERT_INTO" to match schema
                table = stmt.get("table")
                if table:
                    columns = stmt.get("columns", ["*"])
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append({"op": "write", "cols": columns})
                # Handle the read part of an INSERT...SELECT statement
                if "select_statement" in stmt:
                    process_statements(proc, [stmt["select_statement"]], table_usage, lineage)

            elif stmt_type == "DELETE":
                table = stmt.get("table")
                if table:
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append({"op": "write", "cols": ["*"]})

            # Recursively process all possible nested statement blocks
            for key in ["then", "else", "body"]:
                if key in stmt and isinstance(stmt.get(key), list):
                    process_statements(proc, stmt[key], table_usage, lineage)
            
            if stmt_type == "WITH_CTE":
                for cte in stmt.get("cte_list", []):
                    if "query" in cte:
                        process_statements(proc, [cte["query"]], table_usage, lineage)
                if "main_query" in stmt:
                    process_statements(proc, [stmt["main_query"]], table_usage, lineage)
            
            if stmt_type == "CASE":
                for when_clause in stmt.get("when_clauses", []):
                    if "then" in when_clause and isinstance(when_clause.get("then"), list):
                        process_statements(proc, when_clause["then"], table_usage, lineage)

            if "catch" in stmt:
                for handler in stmt.get("catch", []):
                    if "body" in handler and isinstance(handler.get("body"), list):
                        process_statements(proc, handler["body"], table_usage, lineage)

    # Load input files
    try:
        with open(index_file) as f:
            index_data = json.load(f)
        with open(ast_file) as f:
            ast_data = json.load(f)
    except Exception as e:
        print(f"Exception occured while opening the files {e}\n")
        return

    lineage = defaultdict(lambda: {"type": "", "calls": set()})
    table_usage = defaultdict(lambda: defaultdict(list))

    # Use Tool 1 data
    for proc, meta in index_data.items():
        lineage[proc]["type"] = "procedure"
        for table in meta.get("tables", []):
            lineage[table]["type"] = "table"
            lineage[table]["calls"].add(proc)
        for called_proc in meta.get("calls", []):
            lineage[proc]["calls"].add(called_proc)
            lineage[called_proc]["type"] = "procedure"

    #The snippet below activates the AST based detection which can be a bit redundant
    # Use Tool 2 data (AST-based detection)
    ast_proc_map = {}
    for proc_ast in ast_data:
        proc_name = proc_ast.get("proc_name")
        if proc_name:
            ast_proc_map[proc_name] = proc_ast
            #lineage[proc_name]["type"] = "procedure"

    for proc, ast in ast_proc_map.items():
        if ast:
            process_statements(proc, ast.get("statements", []), table_usage, lineage)
    
    # --- NEW: Create a reverse map from procedures to the tables they call ---
    proc_to_tables = defaultdict(set)
    for key, value in lineage.items():
        if value["type"] == "table":
            for proc_name in value["calls"]:
                proc_to_tables[proc_name].add(key)

    # Format output
    formatted_lineage = {}
    for key, value in lineage.items():
        # Basic info for both tables and procedures
        formatted_lineage[key] = {
            "type": value["type"],
            "calls": sorted(list(value["calls"]))
        }
        
        # --- NEW: If the object is a procedure, add the tables it calls ---
        if value["type"] == "procedure":
            formatted_lineage[key]["tables"] = sorted(list(proc_to_tables[key]))

        # If the object is a table, format its usage into the "columns" array
        if value["type"] == "table":
            columns_list = []
            if key in table_usage:
                # Iterate through each procedure that uses this table
                for proc, ops_list in table_usage[key].items():
                    # For each operation recorded for the procedure (e.g., a read and a write)
                    for op_info in ops_list:
                        op = op_info['op']
                        # For each column involved in that single operation
                        for col_name in op_info['cols']:
                            entry = {
                                "name": col_name.strip(),
                                "usage": op,
                                "calling_procedure": proc
                            }
                            # Avoid adding duplicate entries
                            if entry not in columns_list:
                                columns_list.append(entry)
            
            # The schema requires the "columns" field for tables, even if it's empty.
            formatted_lineage[key]["columns"] = columns_list

    with open(output_file, "w") as f:
        json.dump(formatted_lineage, f, indent=2)

    print(f"✅ Lineage written to {output_file}")