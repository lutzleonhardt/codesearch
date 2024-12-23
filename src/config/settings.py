import os

# Default settings
API_KEY = os.getenv("CODESEARCH_API_KEY")
#MODEL = os.getenv("CODESEARCH_MODEL", "claude-3-5-sonnet-latest")
MODEL = os.getenv("CODESEARCH_MODEL", "claude-3-5-sonnet-latest")

if not API_KEY:
    raise ValueError("CODESEARCH_API_KEY environment variable is required")
