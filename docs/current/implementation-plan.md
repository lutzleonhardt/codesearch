# Implemention Plan (powerd by o1 pro)

Below is an updated version of the step-by-step plan including details on how and when to implement colorized CLI output. We’ll integrate the colorization logic using a Python library such as `colorama` or `rich` early in the CLI implementation so it’s available as we progress.

---

## Updated Final File Structure (with Colorization Considerations)

```plaintext
src/
    __init__.py
    cli.py              # CLI entry point, main user interaction loop
    agent/
        __init__.py
        llm_agent.py     # LLM agent implementation (Pydantic AI)
        prompts.py        # Prompt templates and formatting
        schemas.py        # Pydantic models for agent input/output
    tools/
        __init__.py
        base.py           # BaseTool class and common interfaces
        directory.py       # Directory listing tool
        ctags.py           # CTags tool
        terminal.py        # Terminal execution tool
        file_reader.py     # File content retrieval tool
    config/
        __init__.py
        settings.py        # Configuration (env vars, CLI args)
    logs/                 # Directory for log files (ignored by git)
    tests/
        __init__.py
        test_cli.py
        test_agent.py
        test_tools.py
        test_integration.py  # (later)
    requirements.txt
    README.md
    setup.py (optional)
```

**Note on Colorization:**

- You can use `colorama` (simple and built into many environments) or `rich` (more feature-rich).
- For simple prefix and color formatting, `colorama` is sufficient. If you want more styling (bold, italic, etc.), consider `rich`.
- We'll assume `colorama` for simplicity here.

---

## Detailed Step-by-Step Plan with Colorization

### Step 0: Initial Setup [DONE]

**Goal:**  
Create the directory structure and empty files. Add `colorama` to `requirements.txt`.

**Actions:**

- `requirements.txt`: Include `pydantic`, `click` or `typer`, `openai`, `colorama`, `pytest`, etc.
- Create empty `.py` files according to the structure.
- `venv` and `pip install -r requirements.txt`.

**Checks:**

- All files exist but are empty. No functionality yet.

### Step 1: Configuration & Logging

**Goal:**  
Implement basic configuration and logging. No colorization needed yet, but you can prepare a helper for coloring.

**Files to Edit:**

- `config/settings.py`:
    - Implement `BaseSettings` with fields like `OPENAI_MODEL`, `ROOT_DIR`, `VERBOSE`.
- `cli.py`:
    - Initialize logging.
    - Print a simple welcome message.

**Add a Helper for Colorized Output:**

- In `cli.py` or create a small utility file (e.g., `cli_output.py`), write a function `colored_print(message: str, color: str = None)` that uses `colorama`:

    ```python
    from colorama import Fore, Style, init
    init(autoreset=True)  # so colors reset after each print
    
    def colored_print(message: str, prefix: str = "[codesearch] ", color: str = None):
        colored_prefix = prefix
        if color:
            colored_prefix = getattr(Fore, color.upper(), Fore.WHITE) + prefix + Style.RESET_ALL
        print(f"{colored_prefix}{message}")
    ```

- This can be improved later, but provides a base for colorization.


**Tests:**

- `test_cli.py`: Ensure CLI runs. No complex tests yet.

**Checks:**

- Run `python -m codesearch.cli`. Should print a welcome message.
- Later, all outputs will use `colored_print()`.
