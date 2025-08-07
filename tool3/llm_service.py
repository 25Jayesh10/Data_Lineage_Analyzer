import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from a .env file in your project's root directory
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_business_logic(proc_name, params, tables, sql_code):
    """Crafts a prompt and gets a business logic description from the LLM."""

    prompt = f"""
    You are an expert SQL technical writer. Your task is to analyze the provided SQL procedure and write a concise business logic description.

    **CONTEXT:**
    - **Procedure Name:** {proc_name}
    - **Parameters:** {params}
    - **Tables Involved:** {tables}
    - **SQL Source Code:**
    ```sql
    {sql_code}
    ```

    **INSTRUCTION:**
    Based on all the context, write a clear, one-paragraph business logic description. Explain the procedure's purpose from a business perspective.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating description for {proc_name}: {e}")
        return "Description could not be generated due to an error."