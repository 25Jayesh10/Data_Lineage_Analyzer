from src.analyze_lineage import analyze_lineage
from src.generate_mermaid import generate_mermaid
from src.convert_mmd_to_md import convert_mmd_to_md
import json
import os
from antlr4 import *
from tool1.proc_indexer import ProcedureIndexer
from tool1.TSqlLexer import TSqlLexer
from tool1.TSqlParser import TSqlParser
from logging_styles import Colours
from validation_script import validate
from tool1.index_validator import validate


def main():
    # Define file paths
    input_dir = "data"
    output_dir = "data"
    diagram_dir = "diagrams"

    #tool 1 working starts
    input_file = "./test.sql"
    try:
        input_stream = FileStream(input_file, encoding='utf-8')
    except Exception as e:
        print(f"Error Detected While Opening the input file {e} ")

    lexer = TSqlLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = TSqlParser(tokens)
    tree = parser.tsql_file()
    #print(tree.toStringTree(recog=parser))

    walker = ParseTreeWalker()
    listener = ProcedureIndexer()
    walker.walk(listener, tree)

    try :
        with open("./data/index.json", "w") as f:
            json.dump(listener.get_index(), f, indent=2)
        #tool 1 working ends
    except Exception as e:
        print(f"json file could not be opened with exeption {e}")
    
    # Validate all inputs using schema-based validator
    print(Colours.YELLOW + "Validating index.json against schema..." + Colours.RESET)
    if validate():
        print(Colours.GREEN + "Validation passed. Proceeding to Data Lineage Analysis." + Colours.RESET)
    
        index_path = os.path.join(input_dir, "index.json")   # Tool 1 output
        ast_path = os.path.join(input_dir, "ast.json")       # Tool 2 output
        output_path = os.path.join(output_dir, "lineage.json")  # Tool 4 output
        mermaid_path = os.path.join(diagram_dir, "lineage.mmd") # Mermaid diagram output
        markdown_path = os.path.join(diagram_dir, "lineage.md")    # Mermaid .md file
        
        print(Colours.GREEN+"Starting Data Lineage Analysis..."+Colours.RESET)
        analyze_lineage(index_path, ast_path, output_path)
        print(Colours.GREEN+"Data Lineage Analysis complete."+Colours.RESET)
       
        try:
            with open(output_path, 'r') as f:
                lineage_data = json.load(f)
        except Exception as e :
            print(f"Error while writing the file to json {e}")

       # Pretty print to terminal
        print(json.dumps(lineage_data, indent=2))

        print("Generating Mermaid diagram...")
        generate_mermaid(output_path, mermaid_path)
        convert_mmd_to_md(mermaid_path, markdown_path)
    else:
        print(Colours.RED + "Validation failed. Exiting tool." + Colours.RESET)
        return


if __name__ == "__main__":
    main()
