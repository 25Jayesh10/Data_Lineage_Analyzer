#This is a validation script that checks if the AST is consistent with the index.json file

import os
import json

def validate(index_path :str,ast_path :str ):
   
    try:
        with open(index_path,"r") as f:
            index_data=json.load(f)
        with open(ast_path,"r") as f:
            ast_data=json.load(f)
    except Exception as e:
        print(f"Error while opening the file- {e}")
    
    #most naive proc_name based validation
    index_proc_set=set(index_data.keys()) # set of all proc_names in the index
    ast_proc_set=set()
    # set of all procs in ast
    for item in ast_data:
        ast_proc_set.add(item.get("proc_name","not_defined"))
    if "not_defined" in index_proc_set or "not_defined" in ast_proc_set:
        print('\033[91m'+ "Inconsistency between AST and Index file detected! Please Check your Inputs\n Error Type- one of the procedure names has not been defined in either of the files"+'\033[0m') #These escape sequence characters have been added to colour the text on the terminal and can be removed.
        return False
    
    if index_proc_set == ast_proc_set:
        print('\033[92m'+"Naive Validation Done"+'\033[0m')
        return True
    else:
        print('\033[91m'+ "Inconsistency between AST and Index file detected! Please Check your Inputs\n Error Type- Some procedures have been found which are present in the one of the files but not in the other"+'\033[0m')
        return False
    




