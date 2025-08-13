import json
import re
from antlr4 import *
from antlr.TSqlLexer import TSqlLexer
from antlr.TSqlParser import TSqlParser
from antlr.TSqlParserVisitor import TSqlParserVisitor
from antlr4.tree.Tree import TerminalNodeImpl

class ASTBuilder(TSqlParserVisitor):
    def __init__(self):
        self.asts = []
        self.current_ast = None
        self.statement_stack = []
        self.cursors = []
        self.variables = []

    def get_full_text(self, ctx):
        if not ctx:
            return ""
        try:
            text = ctx.start.getInputStream().getText(ctx.start.start, ctx.stop.stop)
        except Exception:
            text = ctx.getText()

        text = text.replace('@ @', '@@')

        return text.strip().rstrip(';')


    def _add_statement(self, stmt_object):
        # Fix incorrect cursor field name
        if "name" in stmt_object and stmt_object["type"].endswith("_CURSOR"):
            stmt_object["cursor_name"] = stmt_object.pop("name")
        
        if self.statement_stack:
            self.statement_stack[-1].append(stmt_object)
        else:
            self.current_ast["statements"].append(stmt_object)

    def _get_procedure_name(self, ctx):
        candidates = [
            'func_proc_name_schema',
            'full_object_name',
            'func_proc_name',
            'procedure_name',
            'func_proc_name_server_database_schema'
        ]
        for name in candidates:
            if hasattr(ctx, name) and getattr(ctx, name)():
                return self.get_full_text(getattr(ctx, name)())
        return "<unknown>"

    def visitTsql_file(self, ctx):
        self.visitChildren(ctx)
        return self.asts

    def visitBatch(self, ctx):
        return self.visitChildren(ctx)

    def visitCreate_or_alter_procedure(self, ctx: TSqlParser.Create_or_alter_procedureContext):
        self.current_ast = {
            "proc_name": self._get_procedure_name(ctx),
            "params": [],
            "return_type": "VOID", # 🛠️ Changed from "INTEGER" to "VOID" as per schema
            "variables": [], # 🛠️ Initialize variables here
            "statements": []
        }
        self.asts.append(self.current_ast)

        self.statement_stack.append(self.current_ast["statements"])
        self.visitChildren(ctx)
        self.statement_stack.pop()

        self.current_ast["variables"].extend(self.variables) # 🛠️ Add collected variables
        self.variables.clear() # 🛠️ Clear for next procedure
        # self.current_ast["cursors"].extend(self.cursors)
        # self.cursors.clear()

    def visitProcedure_param(self, ctx: TSqlParser.Procedure_paramContext):
        param = {
            "name": self.get_full_text(ctx.LOCAL_ID()),
            "type": self.get_full_text(ctx.data_type()),
            "mode": "OUT" if ctx.OUTPUT() or ctx.OUT() else "IN"
        }
        self.current_ast["params"].append(param)

    # def visitDeclare_local(self, ctx):
    #     declare_text = self.get_full_text(ctx).strip().rstrip(';')

    #     # Match multiple declarations in one line (e.g., DECLARE @a INT, @b VARCHAR(20))
    #     if declare_text.upper().startswith("DECLARE"):
    #         declarations = declare_text[7:].split(",")
    #         for decl in declarations:
    #             parts = decl.strip().split()
    #             if len(parts) >= 2:
    #                 name = parts[0]
    #                 var_type = " ".join(parts[1:])
    #                 normalized_type = var_type.upper().split('(')[0].strip() # Get base type
    #                 if normalized_type not in ["INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT", "VARCHAR", "CHAR", "NVARCHAR", "TEXT", "BOOLEAN", "DATE", "TIMESTAMP", "DATETIME", "TIME", "FLOAT", "NUMERIC", "DECIMAL"]:
    #                     # Default to VARCHAR if not directly in enum, or handle as needed
    #                     normalized_type = "VARCHAR" # Defaulting for schema compliance

    #                 self.variables.append({ # 🛠️ Append to instance variables list
    #                     "name": name.rstrip(";"),
    #                     "type": normalized_type.rstrip(";")
    #                 })
    #     return self.visitChildren(ctx)  # No need to recurse further

    # 🛠️ Refined visitDeclare_local
    def visitDeclare_local(self, ctx: TSqlParser.Declare_localContext):
        print("🔥 visiting DECLARE (refined)")
        # Iterate through declare_local_item contexts to get each variable declaration
        if hasattr(ctx, 'declare_local_body') and ctx.declare_local_body():
            for item_ctx in ctx.declare_local_body().declare_local_item():
                try:
                    # Get variable name(s)
                    # The TSqlParser rule for id_ might contain commas for multiple declarations
                    id_text = self.get_full_text(item_ctx.id_())
                    var_names = [name.strip() for name in id_text.split(',')]

                    # Get data type
                    data_type = self.get_full_text(item_ctx.data_type()).upper() # Ensure uppercase

                    # 🛠️ Basic type mapping to ensure schema compliance
                    if data_type not in ["INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT", "VARCHAR", "CHAR", "NVARCHAR", "TEXT", "BOOLEAN", "DATE", "TIMESTAMP", "DATETIME", "TIME", "FLOAT", "NUMERIC", "DECIMAL"]:
                        data_type = "VARCHAR" # Default to VARCHAR if not in enum

                    for var_name in var_names:
                        if var_name: # Ensure var_name is not empty
                            self.variables.append({
                                "name": var_name,
                                "type": data_type
                            })
                except Exception as e:
                    print(f"❌ Error parsing variable declaration in visitDeclare_local: {e}")
        return self.visitChildren(ctx) # Continue visiting children


    # def visitSet_statement(self, ctx):
    #     if ctx.LOCAL_ID():
    #         stmt = {
    #             "type": "SET",
    #             "set": {
    #                 self.get_full_text(ctx.LOCAL_ID()): self.get_full_text(ctx.expression())
    #             }
    #         }
    #     else:
    #         stmt = {
    #             "type": "SET",
    #             "expression": self.get_full_text(ctx)
    #         }
    #     self._add_statement(stmt)

    def visitSet_statement(self, ctx):
        if ctx.LOCAL_ID():
            # 🛠️ Changed to 'name' and 'value' as per schema
            stmt = {
                "type": "SET",
                "name": self.get_full_text(ctx.LOCAL_ID()),
                "value": self.get_full_text(ctx.expression())
            }
        else:
            # This case might need refinement based on actual SQL Server SET statements
            # For now, if no LOCAL_ID, capture as a general expression.
            # 🛠️ Changed to 'expression' as per schema
            stmt = {
                "type": "SET",
                "expression": self.get_full_text(ctx)
            }
        self._add_statement(stmt)


    # def visitSelect_statement(self, ctx):
    #     stmt = {"type": "SELECT", "query": self.get_full_text(ctx)}
    #     self._add_statement(stmt)
    def visitSelect_statement(self, ctx):
        stmt = {"type": "SELECT", "query": self.get_full_text(ctx)} # 🛠️ Changed 'query' to match schema
        self._add_statement(stmt)

    def visitUpdate_statement(self, ctx):
        stmt = {
            "type": "UPDATE",
            "table": self.get_full_text(ctx.ddl_object()),
            "set": {},
            "where": self.get_full_text(ctx.search_condition()) if ctx.search_condition() else ""
        }
        for elem in ctx.update_elem():
            stmt["set"][self.get_full_text(elem.full_column_name())] = self.get_full_text(elem.expression())
        self._add_statement(stmt)

    def visitReturn_statement(self, ctx):
        stmt = {"type": "RETURN", "value": self.get_full_text(ctx.expression()) if ctx.expression() else "0"}
        self._add_statement(stmt)

    def visitIf_statement(self, ctx):
        stmt = {
            "type": "IF",
            "condition": self.get_full_text(ctx.search_condition()),
            "then": [],
            "else": []
        }
        self._add_statement(stmt)

        self.statement_stack.append(stmt["then"])
        if ctx.sql_clauses(0):
            self.visit(ctx.sql_clauses(0))
        self.statement_stack.pop()

        if ctx.sql_clauses(1):
            self.statement_stack.append(stmt["else"])
            self.visit(ctx.sql_clauses(1))
            self.statement_stack.pop()
        else:
            del stmt["else"]

    def visitWhile_statement(self, ctx):
        stmt = {
            "type": "WHILE",
            "condition": self.get_full_text(ctx.search_condition()),
            "body": []
        }
        self._add_statement(stmt)

        # Extract fetch_cursor if it appears before the WHILE loop
        fetch_cursor_ctx = None
        parent = ctx.parentCtx
        if parent and hasattr(parent, 'children'):
            idx = parent.children.index(ctx)
            if idx > 0:
                prev_node = parent.children[idx - 1]
                if hasattr(prev_node, 'cursor_name') and hasattr(prev_node, 'LOCAL_ID'):
                    fetch_cursor_ctx = prev_node

        self.statement_stack.append(stmt["body"])

        # Insert FETCH_CURSOR as the first statement inside WHILE if available
        if fetch_cursor_ctx:
            cursor_name = self.get_full_text(fetch_cursor_ctx.cursor_name()).rstrip(';')
            fetch_into = [self.get_full_text(id).rstrip(';') for id in fetch_cursor_ctx.LOCAL_ID()]
            stmt["body"].append({
                "type": "FETCH_CURSOR",
                "cursor_name": cursor_name,
                "fetch_into": fetch_into
            })

        self.visit(ctx.sql_clauses())
        self.statement_stack.pop()


    def visitTry_catch_statement(self, ctx):
        stmt = {
            "type": "TRY",
            "body": [],
            "catch": [
                {
                    "exception": "@@ERROR",
                    "body": []
                }
            ]
        }
        self._add_statement(stmt)

        # Visit TRY block
        self.statement_stack.append(stmt["body"])
        self.visit(ctx.sql_clauses(0))
        self.statement_stack.pop()

        # Visit CATCH block
        self.statement_stack.append(stmt["catch"][0]["body"])
        self.visit(ctx.sql_clauses(1))
        self.statement_stack.pop()

    # def visitExecute_statement(self, ctx):
    #     exec_text = self.get_full_text(ctx)

    #     try:
    #         proc_name = None
    #         if hasattr(ctx, 'func_proc_name') and ctx.func_proc_name():
    #             proc_name = self.get_full_text(ctx.func_proc_name())
    #         elif hasattr(ctx, 'id_') and ctx.id_():
    #             proc_name = self.get_full_text(ctx.id_())

    #         args = []
    #         if hasattr(ctx, 'execute_statement_arg'):
    #             args = [self.get_full_text(arg) for arg in ctx.execute_statement_arg()]

    #         if proc_name:
    #             stmt = {
    #                 "type": "EXEC",
    #                 "procedure": proc_name,
    #                 "args": args
    #             }
    #         else:
    #             stmt = {
    #                 "type": "EXEC",
    #                 "expression": exec_text
    #             }

    #         self._add_statement(stmt)
    #     except Exception as e:
    #         print(f"❌ Error parsing EXECUTE statement: {e}")
    #         stmt = {
    #             "type": "EXEC",
    #             "expression": exec_text
    #         }
    #         self._add_statement(stmt)
    def visitExecute_statement(self, ctx):
        exec_text = self.get_full_text(ctx)

        try:
            proc_name = None
            if hasattr(ctx, 'func_proc_name') and ctx.func_proc_name():
                proc_name = self.get_full_text(ctx.func_proc_name())
            elif hasattr(ctx, 'id_') and ctx.id_():
                proc_name = self.get_full_text(ctx.id_())

            args = []
            if hasattr(ctx, 'execute_statement_arg'):
                # 🛠️ Ensure args are expressions if possible, or string for now
                args = [self.get_full_text(arg) for arg in ctx.execute_statement_arg()]

            if proc_name:
                stmt = {
                    "type": "EXECUTE_PROCEDURE", # 🛠️ Changed type
                    "procedure": proc_name,
                    "args": args
                }
            else:
                # If it's not a named procedure call, treat as RAW_SQL or similar if schema allows
                # For now, we'll keep it as EXEC with an expression, but consider schema "RAW_SQL"
                stmt = {
                    "type": "RAW_SQL", # 🛠️ Changed type for general EXEC expressions
                    "query": exec_text # 🛠️ Changed 'expression' to 'query'
                }

            self._add_statement(stmt)
        except Exception as e:
            print(f"❌ Error parsing EXECUTE statement: {e}")
            stmt = {
                "type": "RAW_SQL", # 🛠️ Changed type for error case
                "query": exec_text # 🛠️ Changed 'expression' to 'query'
            }
            self._add_statement(stmt)


    def visitBegin_transaction(self, ctx):
        self._add_statement({"type": "BEGIN_TRANSACTION"})

    def visitCommit_transaction(self, ctx):
        self._add_statement({"type": "COMMIT"}) # 🛠️ Changed type

    def visitRollback_transaction(self, ctx):
        self._add_statement({"type": "ROLLBACK"}) # 🛠️ Changed type

    # def visitClose_cursor(self, ctx):
    #     cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
    #     self._add_statement({
    #         "type": "CLOSE_CURSOR",
    #         "cursor_name": cursor_name
    #     })


    # def visitDeallocate_cursor(self, ctx):
    #     cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
    #     self._add_statement({
    #         "type": "DEALLOCATE_CURSOR",
    #         "cursor_name": cursor_name
    #     })

    # def visitOpen_cursor(self, ctx):
    #     cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
    #     self._add_statement({
    #         "type": "OPEN_CURSOR",
    #         "cursor_name": cursor_name
    #     })

    # def visitFetch_cursor(self, ctx):
    #     try:
    #         cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
    #         fetch_into = [
    #             self.get_full_text(id_).rstrip(';')
    #             for id_ in ctx.LOCAL_ID()
    #         ] if ctx.LOCAL_ID() else []

    #         # Ensure fetch_into doesn't include trailing commas or semicolons
    #         fetch_into = [val.rstrip(',') for val in fetch_into if val not in (',', ';')]

    #         self._add_statement({
    #             "type": "FETCH_CURSOR",
    #             "cursor_name": cursor_name,
    #             "fetch_into": fetch_into
    #         })
    #     except Exception as e:
    #         print(f"❌ Error parsing FETCH_CURSOR: {e}")
    #         self._add_statement({
    #             "type": "FETCH_CURSOR",
    #             "cursor_name": "<parse_error>",
    #             "fetch_into": []
    #         })


    # def visitDeclare_cursor(self, ctx):
    #     try:
    #         cursor_name = "<unknown>"
    #         if ctx.cursor_name():
    #             cursor_name = self.get_full_text(ctx.cursor_name())
    #         elif ctx.LOCAL_ID():
    #             cursor_name = self.get_full_text(ctx.LOCAL_ID(0))
    #         else:
    #             for child in ctx.children:
    #                 if hasattr(child, 'getText') and child.getText().startswith('@'):
    #                     cursor_name = child.getText()
    #                     break

    #         select_ctx = None
    #         if ctx.select_statement():
    #             select_ctx = ctx.select_statement()
    #         else:
    #             for child in ctx.children:
    #                 if isinstance(child, TSqlParser.Select_statementContext):
    #                     select_ctx = child
    #                     break

    #         query = self.get_full_text(select_ctx) if select_ctx else "<missing_query>"

    #         stmt = {
    #             "type": "DECLARE_CURSOR",
    #             "cursor_name": cursor_name,
    #             "query": query
    #         }

    #         self._add_statement(stmt)
    #     except Exception as e:
    #         print(f"❌ ERROR in DECLARE_CURSOR: {e}")

    def visitClose_cursor(self, ctx):
        cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
        self._add_statement({
            "type": "CLOSE_CURSOR",
            "cursor_name": cursor_name
        })

    def visitDeallocate_cursor(self, ctx):
        cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
        self._add_statement({
            "type": "DEALLOCATE_CURSOR",
            "cursor_name": cursor_name
        })

    def visitOpen_cursor(self, ctx):
        cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
        self._add_statement({
            "type": "OPEN_CURSOR",
            "cursor_name": cursor_name
        })

    def visitFetch_cursor(self, ctx):
        try:
            cursor_name = self.get_full_text(ctx.cursor_name()).rstrip(';')
            fetch_into = [
                self.get_full_text(id_).rstrip(';')
                for id_ in ctx.LOCAL_ID()
            ] if ctx.LOCAL_ID() else []

            fetch_into = [val.rstrip(',') for val in fetch_into if val not in (',', ';')]

            self._add_statement({
                "type": "FETCH_CURSOR",
                "cursor_name": cursor_name,
                "fetch_into": fetch_into # 🛠️ Already aligned with schema
            })
        except Exception as e:
            print(f"❌ Error parsing FETCH_CURSOR: {e}")
            self._add_statement({
                "type": "FETCH_CURSOR",
                "cursor_name": "<parse_error>",
                "fetch_into": []
            })

    # def visitDeclare_cursor(self, ctx):
    #     try:
    #         cursor_name = "<unknown>"
    #         if ctx.cursor_name():
    #             cursor_name = self.get_full_text(ctx.cursor_name())
    #         elif ctx.LOCAL_ID():
    #             cursor_name = self.get_full_text(ctx.LOCAL_ID(0))
    #         else:
    #             for child in ctx.children:
    #                 if hasattr(child, 'getText') and child.getText().startswith('@'):
    #                     cursor_name = child.getText()
    #                     break

    #         select_ctx = None
    #         if ctx.select_statement():
    #             select_ctx = ctx.select_statement()
    #         else:
    #             for child in ctx.children:
    #                 if isinstance(child, TSqlParser.Select_statementContext):
    #                     select_ctx = child
    #                     break

    #         query = self.get_full_text(select_ctx) if select_ctx else "<missing_query>"

    #         stmt = {
    #             "type": "DECLARE_CURSOR",
    #             "cursor_name": cursor_name,
    #             "query": query # 🛠️ Already aligned with schema
    #         }

    #         self._add_statement(stmt)
    #     except Exception as e:
    #         print(f"❌ ERROR in DECLARE_CURSOR: {e}")
    def visitDeclare_cursor(self, ctx: TSqlParser.Declare_cursorContext):
        try:
            cursor_name = "<unknown>"
            if ctx.cursor_name():
                cursor_name = self.get_full_text(ctx.cursor_name())
            elif ctx.LOCAL_ID(): # Check for LOCAL_ID if cursor_name is not direct
                cursor_name = self.get_full_text(ctx.LOCAL_ID(0))
            else:
                # Fallback to find any identifier if direct rules fail
                for child in ctx.children:
                    if isinstance(child, TerminalNodeImpl) and child.getSymbol().type == TSqlLexer.LOCAL_ID:
                        cursor_name = child.getText()
                        break


            # Check if select_statement() method exists before calling
            select_ctx = None
            if hasattr(ctx, 'select_statement') and ctx.select_statement():
                select_ctx = ctx.select_statement()
            else:
                # Iterate children to find a select_statement context
                for child in ctx.children:
                    if isinstance(child, TSqlParser.Select_statementContext):
                        select_ctx = child
                        break

            query = self.get_full_text(select_ctx) if select_ctx else "<missing_query>"

            stmt = {
                "type": "DECLARE_CURSOR",
                "cursor_name": cursor_name,
                "query": query
            }

            self._add_statement(stmt)
        except Exception as e:
            print(f"❌ ERROR in DECLARE_CURSOR: {e}")


    # def visitDeclare_local(self, ctx):
    #     print("🔥 visiting DECLARE")
    #     body = ctx.declare_local_body()
    #     if body:
    #         for item in body.declare_local_item():
    #             try:
    #                 var_names = self.get_full_text(item.id_()).split(',')
    #                 var_type = self.get_full_text(item.data_type())
    #                 for var_name in var_names:
    #                     var_name = var_name.strip()
    #                     if var_name:
    #                         self.variables.append({
    #                             "name": var_name,
    #                             "type": var_type
    #                         })
    #             except Exception as e:
    #                 print(f"❌ Error parsing variable declaration: {e}")
    #     return None


    # def visitRaiseerror_statement(self, ctx):
    #     stmt = {
    #         "type": "RAISERROR",
    #         "message": None,
    #         "severity": None,
    #         "state": None,
    #         "args": [],
    #         "options": []
    #     }

    #     if ctx.getChildCount() == 0:
    #         return

    #     try:
    #         tokens = [self.get_full_text(c) for c in ctx.children]
    #         print("DEBUG: RAISERROR tokens:", tokens)

    #         if tokens[0].upper() == "RAISERROR":
    #             if len(tokens) == 2 and tokens[1].startswith("'"):
    #                 # Sybase style: RAISERROR 'message'
    #                 stmt["message"] = tokens[1] if tokens[1] else "<parse_error>"
    #             elif tokens[1] == '(':
    #                 # SQL Server style: RAISERROR (msg, severity, state [, args...])
    #                 stmt["message"] = tokens[2]
    #                 stmt["severity"] = tokens[4]
    #                 stmt["state"] = tokens[6]

    #                 # Optional args
    #                 i = 7
    #                 while i < len(tokens):
    #                     if tokens[i] == ',' and i + 1 < len(tokens):
    #                         stmt["args"].append(tokens[i + 1])
    #                         i += 2
    #                     elif tokens[i] == 'WITH':
    #                         stmt["options"] = tokens[i + 1:]
    #                         break
    #                     else:
    #                         i += 1
    #             else:
    #                 # Fallback
    #                 stmt["message"] = "<unparsed>"
    #     except Exception as e:
    #         print(f"❌ Error parsing RAISERROR: {e}")
    #         stmt["message"] = "<parse_error>"

    #     if stmt["message"] is None:
    #         stmt["message"] = "<parse_error>"

    #     self._add_statement(stmt)

    # def visitRaiseerror_statement(self, ctx):
    #     stmt = {
    #         "type": "RAISE", # 🛠️ Changed type
    #         "message": None,
    #         "level": None, # 🛠️ Changed from 'severity' to 'level'
    #         "args": []
    #         # 🗑️ Removed 'state' and 'options' as they are not in schema
    #     }

    #     if ctx.getChildCount() == 0:
    #         return

    #     try:
    #         tokens = [self.get_full_text(c) for c in ctx.children]
    #         print("DEBUG: RAISERROR tokens:", tokens)

    #         if tokens[0].upper() == "RAISERROR":
    #             if len(tokens) == 2 and tokens[1].startswith("'"):
    #                 # Sybase style: RAISERROR 'message'
    #                 stmt["message"] = tokens[1] if tokens[1] else "<parse_error>"
    #                 stmt["level"] = "ERROR" # 🛠️ Default level for simple RAISERROR
    #             elif tokens[1] == '(':
    #                 # SQL Server style: RAISERROR (msg, severity, state [, args...])
    #                 stmt["message"] = tokens[2]
    #                 # 🛠️ Map severity to level. Assuming common mappings.
    #                 severity_val = tokens[4]
    #                 if severity_val in ["10", "11", "12", "13", "14", "15", "16"]: # Standard error levels
    #                     stmt["level"] = "ERROR"
    #                 elif severity_val in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]: # Less severe, treat as notice or warning
    #                     stmt["level"] = "WARNING"
    #                 else:
    #                     stmt["level"] = "ERROR" # Default to error if unknown severity

    #                 # 🗑️ Removed state
    #                 # stmt["state"] = tokens[6]

    #                 # Optional args
    #                 i = 7
    #                 while i < len(tokens):
    #                     if tokens[i] == ',' and i + 1 < len(tokens):
    #                         stmt["args"].append(tokens[i + 1])
    #                         i += 2
    #                     elif tokens[i].upper() == 'WITH': # 🗑️ Removed handling of WITH options
    #                         break
    #                     else:
    #                         i += 1
    #             else:
    #                 stmt["message"] = "<unparsed>"
    #                 stmt["level"] = "ERROR" # 🛠️ Default level for unparsed
    #     except Exception as e:
    #         print(f"❌ Error parsing RAISERROR: {e}")
    #         stmt["message"] = "<parse_error>"
    #         stmt["level"] = "ERROR" # 🛠️ Default level for error

    #     if stmt["message"] is None:
    #         stmt["message"] = "<parse_error>"
    #         stmt["level"] = "ERROR" # 🛠️ Default level if message is none

    #     self._add_statement(stmt)

    def visitRaiseerror_statement(self, ctx):
        stmt = {
            "type": "RAISE", # 🛠️ Changed type
            "message": None,
            "level": None, # 🛠️ Changed from 'severity' to 'level'
            "args": []
            # 🗑️ Removed 'state' and 'options' as they are not in schema
        }

        if ctx.getChildCount() == 0:
            return

        try:
            # 🛠️ Parse message, severity, and state from the children
            # A more robust parsing might involve checking for specific child types
            # or a more explicit AST structure from ANTLR for RAISERROR arguments.
            # This is a heuristic based on the typical RAISERROR syntax:
            # RAISERROR ( 'message', severity, state [, arguments ...] )
            # or RAISERROR 'message'
            message_node = None
            severity_node = None
            state_node = None
            arg_nodes = []

            # Find the message, severity, state, and args
            # This requires careful inspection of the ANTLR parse tree structure for RAISERROR
            # Based on the grammar, `RAISERROR ( expression , LOCAL_ID , LOCAL_ID ... )`
            # or `RAISERROR ( expression , error_severity , error_state [ , argument ... ] )`
            # Let's try to extract from known positions
            if ctx.expression() and len(ctx.expression()) > 0:
                message_node = ctx.expression(0)
                stmt["message"] = self.get_full_text(message_node)
                
                # Check for severity and state if present
                if len(ctx.LOCAL_ID()) >= 2: # For severity and state
                    severity_node = ctx.LOCAL_ID(0)
                    state_node = ctx.LOCAL_ID(1)
                    
                    severity_val = self.get_full_text(severity_node)
                    # 🛠️ Map severity to level
                    if severity_val.isdigit():
                        severity_int = int(severity_val)
                        if 1 <= severity_int <= 9:
                            stmt["level"] = "WARNING"
                        elif 10 <= severity_int <= 16:
                            stmt["level"] = "ERROR"
                        else:
                            stmt["level"] = "ERROR" # Default for unknown
                    else:
                        stmt["level"] = "ERROR" # If not a digit

                    # Args
                    for i in range(2, len(ctx.LOCAL_ID())): # Start from third LOCAL_ID for arguments
                        arg_nodes.append(ctx.LOCAL_ID(i))

                for i in range(len(ctx.expression())):
                    if i > 0: # Additional expressions might be arguments
                        arg_nodes.append(ctx.expression(i))
            elif ctx.STRING_LITERAL(): # For RAISERROR 'message'
                stmt["message"] = self.get_full_text(ctx.STRING_LITERAL())
                stmt["level"] = "ERROR" # Default level for simple RAISERROR

            for arg_node in arg_nodes:
                stmt["args"].append(self.get_full_text(arg_node))

        except Exception as e:
            print(f"❌ Error parsing RAISERROR: {e}")
            stmt["message"] = "<parse_error>"
            stmt["level"] = "ERROR" # 🛠️ Default level for error

        if stmt["message"] is None:
            stmt["message"] = "<parse_error>"
            stmt["level"] = "ERROR" # 🛠️ Default level if message is none

        self._add_statement(stmt)


    def visitSql_clauses(self, ctx):
        sql_text = self.get_full_text(ctx).strip()
        # print("🔍 DEBUG: SQL Text =", sql_text)

        # Match cursor operations manually
        if sql_text.upper().startswith("OPEN "):
            cursor_name = sql_text.split()[1]
            # print(f"🔍 DEBUG: Found OPEN_CURSOR for {cursor_name}")
            self.current_ast["statements"].append({
                "type": "OPEN_CURSOR",
                "cursor_name": cursor_name
            })

        elif sql_text.upper().startswith("FETCH NEXT FROM"):
            tokens = sql_text.replace(",", " ").split()
            try:
                cursor_name_idx = tokens.index("FROM") + 1
                cursor_name = tokens[cursor_name_idx]
                into_idx = tokens.index("INTO") + 1
                fetch_into = tokens[into_idx:]
                # print(f"🔍 DEBUG: Found FETCH_CURSOR for {cursor_name} INTO {fetch_into}")
                self.current_ast["statements"].append({
                    "type": "FETCH_CURSOR",
                    "cursor_name": cursor_name,
                    "fetch_into": fetch_into
                })
            except Exception as e:
                print(f"❌ ERROR parsing FETCH_CURSOR: {e}")

        elif sql_text.upper().startswith("CLOSE "):
            cursor_name = sql_text.split()[1]
            # print(f"🔍 DEBUG: Found CLOSE_CURSOR for {cursor_name}")
            self.current_ast["statements"].append({
                "type": "CLOSE_CURSOR",
                "cursor_name": cursor_name
            })

        elif sql_text.upper().startswith("DEALLOCATE "):
            cursor_name = sql_text.split()[1]
            # print(f"🔍 DEBUG: Found DEALLOCATE_CURSOR for {cursor_name}")
            self.current_ast["statements"].append({
                "type": "DEALLOCATE_CURSOR",
                "cursor_name": cursor_name
            })

        else:
            # Visit children and dispatch to visitDeclare_local if any
            for child in ctx.children:
                if hasattr(child, "declare_local") and child.declare_local():
                    self.visit(child.declare_local())
                else:
                    self.visit(child)

    # def visitSql_clauses(self, ctx):
    #     sql_text = self.get_full_text(ctx).strip()

    #     if sql_text.upper().startswith("DECLARE "):
    #         # 🛠️ Handle variable declarations
    #         declare_text = sql_text[7:].strip()  # Strip 'DECLARE '
    #         declarations = [d.strip() for d in declare_text.split(";") if d.strip()]
    #         for decl in declarations:
    #             match = re.match(r"@[\w]+", decl)
    #             if match:
    #                 var_name = match.group(0)
    #                 type_part = decl[len(var_name):].strip().rstrip(",")
    #                 self.current_ast["variables"].append({
    #                     "name": var_name,
    #                     "type": type_part
    #                 })

    #     elif sql_text.upper().startswith("OPEN "):
    #         cursor_name = sql_text.split()[1].rstrip(";")
    #         self.current_ast["statements"].append({
    #             "type": "OPEN_CURSOR",
    #             "cursor_name": cursor_name
    #         })

    #     elif sql_text.upper().startswith("FETCH NEXT FROM"):
    #         tokens = sql_text.replace(",", " ").split()
    #         try:
    #             cursor_name_idx = tokens.index("FROM") + 1
    #             cursor_name = tokens[cursor_name_idx].rstrip(";")
    #             into_idx = tokens.index("INTO") + 1
    #             fetch_into = tokens[into_idx:]
    #             self.current_ast["statements"].append({
    #                 "type": "FETCH_CURSOR",
    #                 "cursor_name": cursor_name,
    #                 "fetch_into": fetch_into
    #             })
    #         except Exception as e:
    #             print(f"❌ ERROR parsing FETCH_CURSOR: {e}")

    #     elif sql_text.upper().startswith("CLOSE "):
    #         cursor_name = sql_text.split()[1].rstrip(";")
    #         self.current_ast["statements"].append({
    #             "type": "CLOSE_CURSOR",
    #             "cursor_name": cursor_name
    #         })

    #     elif sql_text.upper().startswith("DEALLOCATE "):
    #         cursor_name = sql_text.split()[1].rstrip(";")
    #         self.current_ast["statements"].append({
    #             "type": "DEALLOCATE_CURSOR",
    #             "cursor_name": cursor_name
    #         })

    #     else:
    #         self.visitChildren(ctx)

    def visitSql_clauses(self, ctx):    
        # 🗑️ Remove the custom parsing for DECLARE, OPEN, FETCH, CLOSE, DEALLOCATE
        # as these should be handled by their specific visit methods (e.g., visitDeclare_local, visitOpen_cursor).
        # The general visitChildren(ctx) will ensure these are correctly dispatched if ANTLR parses them as distinct rules.

        # 🛠️ Revert to simple visitChildren to allow specific visitors to handle
        self.visitChildren(ctx)

# --- Top-level Execution ---

def generate_ast(sql_file_path: str) -> list:
    with open(sql_file_path, "r") as f:
        input_sql = f.read()

    input_stream = InputStream(input_sql)
    lexer = TSqlLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = TSqlParser(token_stream)
    tree = parser.tsql_file()

    visitor = ASTBuilder()
    asts = visitor.visit(tree)

    if not asts:
        print("❌ No procedure AST found.")
    else:
        print(f"✅ {len(asts)} procedure(s) parsed.")

    return asts

def save_ast(asts: list, output_path: str):
    print(f"📝 Writing ASTs to {output_path}")
    with open(output_path, "w") as f:
        json.dump(asts, f, indent=4)