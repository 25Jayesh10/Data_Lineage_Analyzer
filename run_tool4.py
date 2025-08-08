from src.analyze_lineage import analyze_lineage
from src.generate_mermaid import generate_mermaid
from src.convert_mmd_to_md import convert_mmd_to_md
from src.validation_script import validate
from lineage_to_index import generate_index
import json
import os
from antlr4 import *
from logging_styles import Colours
from tool1.proc_indexer import ProcedureIndexer
from tool1.TSqlLexer import TSqlLexer
from tool1.TSqlParser import TSqlParser

from tool3.doc_generator import generate_docs
from line_profiler import profile




def main():
    # Define file paths
    input_dir = "data"    
    output_dir = "data"
    diagram_dir = "diagrams"
    document_dir = "document"

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
    if validate("data/index.json","data/ast.json"):
        print(Colours.GREEN + "Validation passed. Proceeding to Data Lineage Analysis." + Colours.RESET)
    
        index_path = os.path.join(input_dir, "index.json")   # Tool 1 output
        ast_path = os.path.join(input_dir, "ast.json")       # Tool 2 output
        output_path = os.path.join(output_dir, "lineage.json")  # Tool 4 output
        mermaid_path = os.path.join(diagram_dir, "lineage.mmd") # Mermaid diagram output
        markdown_path = os.path.join(diagram_dir, "lineage.md")    # Mermaid .md file
        
         # ✅ Tool 3: Generate Markdown documentation
        try:
            print(Colours.YELLOW + "Generating Markdown documentation..." + Colours.RESET)
            index_path = os.path.join(input_dir, "index.json")
            generate_docs(index_path, output_dir=document_dir, output_file="procedures.md")
            print(Colours.GREEN + "Documentation generated in 'document/procedures.md'" + Colours.RESET)
        except Exception as e:
            print(Colours.RED + f"Error generating documentation: {e}" + Colours.RESET)
            return
        
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

        # ✅ Tool 4 Extension: Generate generated_index.json from lineage + Mermaid for revalidation
        generated_index_path = os.path.join(input_dir, "generated_index.json")
        success = generate_index(output_path, mermaid_path, generated_index_path)
        if success:
            print(Colours.GREEN + "Generated index.json successfully." + Colours.RESET)
        else:
            print(Colours.RED + "Failed to generate index.json from lineage." + Colours.RESET)

    else:
        print(Colours.RED + "Validation failed. Exiting tool." + Colours.RESET)
        return


if __name__ == "__main__":
    main()
