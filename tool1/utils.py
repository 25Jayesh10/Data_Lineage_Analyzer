#---------------------------------------------------#
# This is a utility file developed to help in the
# development of the tool 1
#---------------------------------------------------#
import re
import logging
logging.basicConfig(level=logging.INFO)

#This function focuses on getting the sql text extracted
def extract_sql_text(filepath : str) -> str :
    try :
        with open(filepath,"r",encoding='utf-8') as f :
            return f.read()
    except Exception as e :
        print(f"Error reading the {filepath}: {e}")


    
#This function tries to extract the procedure name given the input of sql text
def extract_proc_name(sql_text) :

    pattern = r'(?i)create\s+(or\s+replace\s+)?procedure\s+(\[?\w+(\.\w+)?\]?)'
    match = re.search(pattern, sql_text)
    if match :
        matches = re.findall(pattern, sql_text)
        #return the matched procedure names with
        return [m[1].replace('[', '').replace(']', '') for m in matches]
    return None

#This function tries to extract the stored procedures in the sql file 1 by 1
def split_procedure_blocks(sql_text :str)-> list[str]:
    lines=sql_text.splitlines()
    blocks=[]
    currentblock=[]
    inside_proc=False

    for line in lines:

        normalized=line.strip().lower()

        #check for the start of a procedure
        if re.match(r'^\s*create\s+(or\s+replace\s+)?procedure\b', normalized):
            if inside_proc and current_block:
                # Start of a new proc before closing previous one
                blocks.append('\n'.join(current_block))
                current_block = []
            inside_proc = True
        
        if inside_proc:
            current_block.append(line)

            # Check for end of procedure (on its own line)
            if re.match(r'^\s*end\s*;?\s*$', normalized):
                blocks.append('\n'.join(current_block))
                current_block = []
                inside_proc = False
    
    # Handle case where file ends without clean END
    if inside_proc and current_block:
        logging.warning("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ The SQL file contains a procedure without a clean END, assuming End for gracefull execution ~ ~ ~ ~ ~ ~ ~ ~ ")
        blocks.append('\n'.join(current_block))

    return blocks


        
