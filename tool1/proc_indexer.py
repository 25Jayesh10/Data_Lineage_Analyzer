
import logging
logging.basicConfig(level=logging.INFO)
import json
from antlr4 import *
from tool1.TSqlLexer import TSqlLexer
from tool1.TSqlParser import TSqlParser
from tool1.TSqlParserListener import TSqlParserListener
import os
import sys

with open("tool1/type_mapping.json") as f:
    TYPE_MAPPING = json.load(f)

class ProcedureIndexer(TSqlParserListener):
    def __init__(self):
        self.current_proc = None
        self.index = {}

    def enterCreate_or_alter_procedure(self, ctx):
        proc_name = ctx.func_proc_name_schema().getText() #make this lowercase or uppercase based on your needs or keep as it is
        self.current_proc = proc_name
        self.index[proc_name] = {"params": [], "calls": [], "tables": []}

        # Extract parameters
        param_list_ctx = ctx.procedure_param()
        if param_list_ctx:
            for param in param_list_ctx:
                try:
                    param_name = param.children[0].getText()
                    import re
                    raw_type = re.match(r'^[A-Z]+', param.children[1].getText().upper()).group(0)
                     # ✅ Strict validation of types
                    if raw_type not in TYPE_MAPPING:
                        logging.error(f"Unsupported type '{raw_type}' found in procedure '{proc_name}' for parameter '{param_name}'")
                        sys.exit(1)  # ✅ Immediately exit the program     
                    
                    mapped_type = TYPE_MAPPING.get(raw_type, raw_type)  # ✅ Map type using dictionary
                    self.index[proc_name]["params"].append({
                        "name": param_name,
                        "type": mapped_type
                    })
                    
                except Exception as e:
                    logging.warning(f"Failed to extract param: {param.getText()} — {e}")

    def enterExecute_statement(self, ctx):
        if not self.current_proc:
            return

        try:
            # This will go deeper than immediate children
            for child in ctx.getChildren():
                # Recursive child may be another rule, dig into its children
                if isinstance(child, ParserRuleContext):
                    for subchild in child.getChildren():
                        text = subchild.getText()
                        if text.upper() in {"EXEC", "EXECUTE"}:
                            continue
                        if text.startswith("(") or text.startswith("@"):
                            break
                        if text.isidentifier():
                            self.index[self.current_proc]["calls"].append(text) #lowercase if needed
                            return
                else:
                    # Fallback if it's a terminal node
                    text = child.getText()
                    if text.upper() not in {"EXEC", "EXECUTE"} and text.isidentifier():
                        self.index[self.current_proc]["calls"].append(text) #lowercase if needed
                        return
        except Exception as e:
            logging.warning(f"Failed to extract procedure call from EXEC: {e}")


    def enterInsert_statement(self, ctx):
        if self.current_proc:
            table = ctx.ddl_object().getText()
            self.index[self.current_proc]["tables"].append(table)

    def enterUpdate_statement(self, ctx):
        if self.current_proc:
            table = ctx.ddl_object().getText()
            self.index[self.current_proc]["tables"].append(table)

    def enterDelete_statement(self, ctx):
        if self.current_proc:
            table = ctx.delete_statement_from().ddl_object().getText()
            self.index[self.current_proc]["tables"].append(table)

    def _extract_tables_from_select(self, select_ctx):
        """
        Recursively extract all table names from a select_statement context,
        including inside CTEs, subqueries, and derived tables.
        """
        if not select_ctx:
            return

        try:
            qe = select_ctx.query_expression()
            if qe:
                # Simple query spec (FROM ...)
                if qe.query_specification():
                    ts_ctx = qe.query_specification().table_sources()
                    if ts_ctx:
                        for ts in ts_ctx.table_source():
                            # Base table
                            tsi = ts.table_source_item()
                            if tsi and tsi.full_table_name():
                                table = tsi.full_table_name().getText()
                                self.index[self.current_proc]["tables"].append(table)

                            # Subquery in FROM
                            if tsi and tsi.derived_table():
                                sub_sel = tsi.derived_table().subquery().select_statement()
                                self._extract_tables_from_select(sub_sel)

                # UNION / compound queries
                if qe.query_expression():
                    self._extract_tables_from_select(qe.query_expression())

        except Exception as e:
            logging.warning(f"Failed recursive table extraction: {e}")

    def enterSelect_statement_standalone(self, ctx):
        if self.current_proc:
            self._extract_tables_from_select(ctx.select_statement())

    def enterCommon_table_expression(self, ctx):
        if self.current_proc:
            try:
                # Name of CTE itself
                cte_name = ctx.id_().getText()
                self.index[self.current_proc]["tables"].append(cte_name)

                # Extract tables from CTE's SELECT
                sel = ctx.select_statement()
                self._extract_tables_from_select(sel)
            except Exception as e:
                logging.warning(f"Failed to process CTE: {e}")


    def get_index(self):
    # Remove duplicates
        for proc in self.index.values():
            # Deduplicate params (dicts)
            seen_params = set()
            unique_params = []
            for p in proc["params"]:
                key = (p["name"], p["type"])
                if key not in seen_params:
                    seen_params.add(key)
                    unique_params.append(p)
            proc["params"] = unique_params

            # Deduplicate calls and tables (strings)
            proc["calls"] = list(set(proc["calls"]))
            proc["tables"] = list(set(proc["tables"]))

        return self.index



def main():
    input_file = "../test.sql"
    input_stream = FileStream(input_file, encoding='utf-8')
    lexer = TSqlLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = TSqlParser(tokens)
    tree = parser.tsql_file()
    print(tree.toStringTree(recog=parser))


    walker = ParseTreeWalker()
    listener = ProcedureIndexer()
    walker.walk(listener, tree)

    with open("../data/index.json", "w") as f:
        json.dump(listener.get_index(), f, indent=2)

if __name__ == "__main__":
    main()






