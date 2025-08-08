import json
from collections import defaultdict


def analyze_lineage(index_file :str, ast_file :str, output_file :str):
    def extract_table_from_query(query):
        # crude extraction: look for FROM <table>
        tokens = query.replace(",", " ").split()
        for i, token in enumerate(tokens):
            if token.upper() == "FROM" and i + 1 < len(tokens):
                table = tokens[i + 1].strip(';')
                if not table.startswith("@"):
                    return table
        return None

    # def extract_table_from_insert(proc_sql):
    #     # crude extraction: look for INSERT INTO <table>
    #     tokens = proc_sql.replace(",", " ").split()
    #     if len(tokens) >= 3 and tokens[0].upper() == "INSERT" and tokens[1].upper() == "INTO":
    #         table = tokens[2].strip('();')
    #         if not table.startswith("@"):
    #             return table
    #     return None
    # what if there is something like select into (lets try to find out)

    def process_statements(proc, stmts, table_usage, lineage):
        for stmt in stmts:
            stmt_type = stmt.get("type", "").upper() #converts to uppercase if not.

            # Detect SELECT_INTO or SELECT (read)
            if stmt_type in ("SELECT_INTO", "SELECT"): # there can be possible issues here because of SELECT
                query = stmt.get("query", "")
                table = extract_table_from_query(query)
                if table:
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append("read")

            

            # Detect UPDATE (write)
            if stmt_type == "UPDATE":
                table = stmt.get("table")
                if table:
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append("write")
            
            #Detect Insert (write)
            if stmt_type=="INSERT_INTO":
                table=stmt.get("table")
                if table :
                    lineage[table]["type"]="table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append("write")
           

            # Detect DELETE (write)
            if stmt_type == "DELETE":
                table = stmt.get("table")
                if table:
                    lineage[table]["type"] = "table"
                    lineage[table]["calls"].add(proc)
                    table_usage[table][proc].append("write")
            
            #curude extraction of reads and writes info (this is a fallback in case the AST does not present nested queries in a structured format)
            if stmt_type not in ["INSERT_INTO","DELETE","UPDATE","SELECT_INTO","SELECT"]: # ie the statement is RAW_SQL type or some other type
                #crude extraction
                query = stmt.get("query", "") #converts to uppercase if not.
                if stmt_type and query:
                    tokens = query.replace(",", " ").replace(";", " ").split()
                    for i, token in enumerate(tokens):
                        # UPDATE <table>
                        if token.upper() == "UPDATE" and i + 1 < len(tokens):
                            table = tokens[i + 1]
                            lineage[table]["type"] = "table"
                            lineage[table]["calls"].add(proc)
                            table_usage[table][proc].append("write")
                        # INSERT INTO <table>
                        if token.upper() == "INSERT" and i + 1 < len(tokens) and tokens[i + 1].upper() == "INTO" and i + 2 < len(tokens):
                            table = tokens[i + 2]
                            lineage[table]["type"] = "table"
                            lineage[table]["calls"].add(proc)
                            table_usage[table][proc].append("write")
                        # SELECT ... FROM <table>
                        if token.upper() == "FROM" and i + 1 < len(tokens):
                            table = tokens[i + 1]
                            lineage[table]["type"] = "table"
                            lineage[table]["calls"].add(proc)
                            table_usage[table][proc].append("read")
                        # SELECT INTO <table>
                        if token.upper() == "INTO" and i > 0 and tokens[i - 1].upper() == "SELECT" and i + 1 < len(tokens):
                            table = tokens[i + 1]
                            lineage[table]["type"] = "table"
                            lineage[table]["calls"].add(proc)
                            table_usage[table][proc].append("write")


                

## Next snippet has to be examined if actually needed as its relevance depends on how well the AST presents the output while formatting
            # Recursively process nested statements in control flow
            for key in ["then", "else", "body", "catch"]:
                if key in stmt and isinstance(stmt[key], list):
                    process_statements(proc, stmt[key], table_usage, lineage)

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
        process_statements(proc, ast.get("statements", []), table_usage, lineage)

    # Format output
    formatted_lineage = {}
    for key, value in lineage.items():
        formatted_lineage[key] = {
            "type": value["type"],
            "calls": sorted(value["calls"])
        }
        if value["type"] == "table" and key in table_usage:
            formatted_lineage[key]["usage"] = {proc: sorted(set(ops)) for proc, ops in table_usage[key].items()}

    with open(output_file, "w") as f:
        json.dump(formatted_lineage, f, indent=2)

    print(f"✅ Lineage written to {output_file}")
#as of now we are doing crude extraction it can be made better in the future if the ast tool has table as a required field for SELECT and SELECT INTO statements