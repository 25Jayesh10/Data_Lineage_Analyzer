
import logging
logging.basicConfig(level=logging.INFO)
import json
from antlr4 import *
from tool1.TSqlLexer import TSqlLexer
from tool1.TSqlParser import TSqlParser
from tool1.TSqlParserListener import TSqlParserListener
import os

class ProcedureIndexer(TSqlParserListener):
    def __init__(self):
        self.current_proc = None
        self.index = {}

    def enterCreate_or_alter_procedure(self, ctx):
        proc_name = ctx.func_proc_name_schema().getText().lower()
        self.current_proc = proc_name
        self.index[proc_name] = {"params": [], "calls": [], "tables": []}

        # Extract parameters
        param_list_ctx = ctx.procedure_param()
        if param_list_ctx:
            for param in param_list_ctx:
                try:
                    param_name = param.children[0].getText()
                    param_type = param.children[1].getText()
                    self.index[proc_name]["params"].append({
                        "name": param_name,
                        "type": param_type
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
                            self.index[self.current_proc]["calls"].append(text.lower())
                            return
                else:
                    # Fallback if it's a terminal node
                    text = child.getText()
                    if text.upper() not in {"EXEC", "EXECUTE"} and text.isidentifier():
                        self.index[self.current_proc]["calls"].append(text.lower())
                        return
        except Exception as e:
            logging.warning(f"Failed to extract procedure call from EXEC: {e}")


    def enterInsert_statement(self, ctx):
        if self.current_proc:
            table = ctx.ddl_object().getText().lower()
            self.index[self.current_proc]["tables"].append(table)

    def enterUpdate_statement(self, ctx):
        if self.current_proc:
            table = ctx.ddl_object().getText().lower()
            self.index[self.current_proc]["tables"].append(table)

    def enterDelete_statement(self, ctx):
        if self.current_proc:
            table = ctx.delete_statement_from().ddl_object().getText().lower()
            self.index[self.current_proc]["tables"].append(table)

    def enterSelect_statement_standalone(self, ctx):
        if self.current_proc:
            try:
                from_clause = ctx.select_statement().query_expression().query_specification().table_sources()
                if from_clause:
                    for ts in from_clause.table_source():
                        table = ts.table_source_item().full_table_name().getText().lower()
                        self.index[self.current_proc]["tables"].append(table)
            except:
                pass  # Some selects may not have full context

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






