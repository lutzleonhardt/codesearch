import os

# Default settings
API_KEY = os.getenv("CODESEARCH_API_KEY")
MODEL = os.getenv("CODESEARCH_MODEL", "gpt-4o")

if not API_KEY:
    raise ValueError("CODESEARCH_API_KEY environment variable is required")
