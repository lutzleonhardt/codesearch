import os

# Default settings
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")
ROOT_DIR = os.getenv("ROOT_DIR", os.getcwd())
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
