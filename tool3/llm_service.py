
# import os
# import google.generativeai as genai
# import openai
# import anthropic
# from dotenv import load_dotenv

# # Load all environment variables from a .env file
# load_dotenv()

# def _initialize_gemini():
#     """Initializes and returns the Gemini model client."""
#     try:
#         api_key = os.environ["GEMINI_API_KEY"]
#         genai.configure(api_key=api_key)
#         return genai.GenerativeModel('gemini-1.5-flash')
#     except KeyError:
#         print("❌ Error: GEMINI_API_KEY not found in .env file.")
#         return None

# def _initialize_azure():
#     """Initializes and returns the Azure OpenAI client."""
#     try:
#         return openai.AzureOpenAI(
#             api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#             api_version="2024-02-01",
#             azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
#         )
#     except KeyError as e:
#         print(f"❌ Error: {e} not found in .env file for Azure configuration.")
#         return None

# def _initialize_anthropic():
#     """Initializes and returns the Anthropic client."""
#     try:
#         return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#     except KeyError:
#         print("❌ Error: ANTHROPIC_API_KEY not found in .env file.")
#         return None

# def _generate_with_gemini(prompt: str) -> str:
#     """Generates content using Google Gemini."""
#     model = _initialize_gemini()
#     if not model:
#         return "Description generation failed due to missing Gemini API key."
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         return f"Description could not be generated due to a Gemini API error: {e}"

# def _generate_with_azure(prompt: str) -> str:
#     """Generates content using Azure OpenAI."""
#     azure_client = _initialize_azure()
#     deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
#     if not azure_client or not deployment_name:
#         return "Description generation failed due to missing Azure configuration."
#     try:
#         response = azure_client.chat.completions.create(
#             model=deployment_name,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Description could not be generated due to an Azure API error: {e}"

# def _generate_with_anthropic(prompt: str) -> str:
#     """Generates content using Anthropic Claude."""
#     anthropic_client = _initialize_anthropic()
#     if not anthropic_client:
#         return "Description generation failed due to missing Anthropic API key."
#     try:
#         response = anthropic_client.messages.create(
#             model="claude-3-sonnet-20240229",
#             max_tokens=1024,
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return response.content[0].text.strip()
#     except Exception as e:
#         return f"Description could not be generated due to an Anthropic API error: {e}"

# def generate_business_logic(proc_name: str, params: list, tables: list, sql_code: str, llm_provider: str) -> str:
#     """
#     Crafts a prompt and gets a business logic description from the selected LLM provider.
#     This function acts as a dispatcher based on the user's runtime choice.
#     """
#     prompt = f"""
#     You are an expert SQL technical writer. Your task is to analyze the provided SQL procedure and write a concise business logic description.

#     **CONTEXT:**
#     - **Procedure Name:** {proc_name}
#     - **Parameters:** {params}
#     - **Tables Involved:** {tables}
#     - **SQL Source Code:**
#     ```sql
#     {sql_code}
#     ```

#     **INSTRUCTION:**
#     Based on all the context, write a clear, one-paragraph business logic description. Explain the procedure's purpose from a business perspective.
#     """
    
#     # Dispatch to the correct generation function based on the user's choice
#     if llm_provider == "azure":
#         return _generate_with_azure(prompt)
#     elif llm_provider == "anthropic":
#         return _generate_with_anthropic(prompt)
#     elif llm_provider == "gemini":
#         return _generate_with_gemini(prompt)
#     else:
#         return "Error: Unknown LLM provider specified."

# llm_service.py
import os
import openai
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

# Globals to store runtime configuration
_openrouter_api_key = None
_openrouter_model = None
_client_initialized = False

def _initialize_openrouter():
    """
    Initializes the OpenRouter client by asking the user for model and API key.
    Only runs once per session.
    """
    global _openrouter_api_key, _openrouter_model, _client_initialized

    if _client_initialized:
        return

    # Ask user for model
    print("\n=== OpenRouter LLM Selection ===")
    print("Examples of available models:")
    print("  anthropic/claude-3.5-sonnet")
    print("  openai/gpt-4o-mini")
    print("  mistralai/mistral-7b-instruct")
    print("  google/gemini-pro")
    _openrouter_model = input("Enter the OpenRouter model you want to use: ").strip()

    # Ask user for API key (or use from .env if exists)
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        use_env = input(f"Use API key from .env? (y/n): ").strip().lower()
        if use_env == "y":
            _openrouter_api_key = env_key
        else:
            _openrouter_api_key = input("Enter your OpenRouter API key: ").strip()
    else:
        _openrouter_api_key = input("Enter your OpenRouter API key: ").strip()

    # Configure OpenAI client to use OpenRouter endpoint
    openai.api_key = _openrouter_api_key
    openai.base_url = "https://openrouter.ai/api/v1"

    _client_initialized = True
    print(f"✅ OpenRouter initialized with model: {_openrouter_model}\n")


def _generate_with_openrouter(prompt: str) -> str:
    """
    Generates text using the selected OpenRouter model.
    """
    try:
        response = openai.chat.completions.create(
            model=_openrouter_model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenRouter generation failed: {e}"


def generate_business_logic(proc_name: str, params: list, tables: list, sql_code: str) -> str:
    """
    Crafts a prompt and gets a business logic description from the selected OpenRouter model.
    """
    _initialize_openrouter()

    prompt = f"""
    You are an expert SQL technical writer. Your task is to analyze the provided SQL procedure
    and write a concise business logic description.

    **CONTEXT:**
    - **Procedure Name:** {proc_name}
    - **Parameters:** {params}
    - **Tables Involved:** {tables}
    - **SQL Source Code:**
    ```sql
    {sql_code}

    INSTRUCTION:
    Based on all the context, write a clear, one-paragraph business logic description.
    Explain the procedure's purpose from a business perspective.
    """

    return _generate_with_openrouter(prompt)