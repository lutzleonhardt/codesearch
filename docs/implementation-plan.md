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

### Step 1: Configuration & Logging [DONE]

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

### Step 2: Tool Interface (BaseTool) and Stubs [DONE]

**Goal:**  
Define a `BaseTool` and basic Pydantic models for requests and responses.

**Files to Edit:**

- `tools/base.py`:
    - Define `BaseTool` as an abstract class with a `run(**kwargs)` method.
- `agent/schemas.py`:
    - Add `ToolRequest`, `ToolResponse` models.

**Tests:**

- `test_tools.py`: Test instantiation of a mock tool.

**Checks:**

- Everything still minimal. No colors needed in tools yet since no user output here.

### Step 3: CLI Structure (Without Real Agent) & Mock Interaction

**Goal:**  
Implement CLI argument parsing and a simple interactive loop. Start using `colored_print()` for all CLI messages.

**Files to Edit:**

- `cli.py`:
    - Parse `--verbose`, `--root-dir`, `--rebuild-ctags` using `click` or `typer`.
    - Use `colored_print()` for any CLI messages to differentiate them.
    - Have a mock interaction loop:

        ```python
        while True:
            user_input = input("Enter query (or 'q' to quit): ")
            if user_input.lower() == 'q':
                break
            # just echo back for now
            colored_print(f"You said: {user_input}", color="GREEN")
        ```


**Tests:**

- `test_cli.py`: Test CLI arguments and ensure that output contains the `[codesearch]` prefix.

**Checks:**

- Run the CLI. Confirm you see `[codesearch]` prefix and green echo messages.

### Step 4: Agent Skeleton with Pydantic AI and Mock Responses

**Goal:**  
Introduce the LLM agent structure. No actual LLM calls yet.

**Files to Edit:**

- `agent/schemas.py`:
    - Define `AgentInput(user_query: str)` and `AgentOutput(summary: str, tool_requests: list[ToolRequest] = [])`.
- `agent/prompts.py`:
    - Add placeholder strings for system, user, and assistant prompts.
- `agent/llm_agent.py`:
    - Implement an `Agent` class that uses Pydantic AI.
    - For now, return a mock `AgentOutput` (e.g., `summary="This is a mock response"`).

**Integration with CLI:**

- In `cli.py`, instead of echoing back user input, call the `Agent` with `AgentInput(user_query=user_input)` and print the `AgentOutput.summary` with `colored_print()` in a different color (e.g., `YELLOW`).

**Tests:**

- `test_agent.py`: Ensure `Agent` returns `AgentOutput` as expected.

**Checks:**

- Run CLI, input a query. You get a yellow `[codesearch] This is a mock response` line.

### Step 5: Incremental Tool Implementation

**Goal:**  
Implement tools one by one and integrate them into the Agent logic. Use colorized CLI output to summarize tool results.

**Tools:**

1. **Directory Tool (`directory.py`)**:

    - Implement `DirectoryToolRequest(path: str)` and `DirectoryToolResponse(structure: dict)`.
    - `run(path: str)` returns a dict with file/dir info.
    - Colorization happens in CLI after tool results are summarized by the Agent.
2. **File Reader Tool (`file_reader.py`)**:

    - Similar approach, no direct color printing here. The agent will summarize, and CLI prints with `colored_print()`.
3. **Terminal Tool (`terminal.py`)**:

    - User approval step:

        ```python
        colored_print("LLM wants to run a terminal command: 'ls -l'. Approve? (y/n)", color="CYAN")
        ```

    - If approved, run the command, summarize result, print summary with `colored_print()` (e.g., `color="BLUE"`).
4. **CTags Tool (`ctags.py`)**:

    - Implement caching logic.
    - No direct CLI colorization here; just ensure that CLI prints tool summaries in a unique color (e.g., `MAGENTA`) when displaying results.

**Tests:**

- `test_tools.py`: Unit test each tool independently.
- `test_agent.py`: Mock LLM to request these tools and ensure `AgentOutput` includes `tool_requests`.

**Checks:**

- Run CLI, ask a query that triggers a tool. User approves, tool runs, `Agent` summarizes.
- The final summary is printed with `colored_print()` so user can distinguish it from normal output.

### Step 6: Real LLM Integration & Summarization Logic

**Goal:**  
Use a real LLM. Ensure all chain-of-thought remains internal and only summarized outputs are printed. Colorize final summaries in a distinct color.

**Files to Edit:**

- `agent/prompts.py`:
    - Add instructions to the system prompt about always summarizing results, referencing files, and not showing raw chain-of-thought.
- `agent/llm_agent.py`:
    - Connect to OpenAI API (using `OPENAI_MODEL` from `settings.py`).
    - Ensure that when LLM responds with a `tool_request`, the CLI prints a message in `colorama` `CYAN`, prompting user approval.

**Tests:**

- `test_agent.py`: Mock OpenAI calls to verify schema compliance.
- Check large outputs are truncated and summarized. Summarized output can be printed in a neutral color, say `WHITE` or `YELLOW`.

### Step 7: Refinement, Verbosity, and Error Handling

**Goal:**  
Make sure verbosity is honored. Add error messages in `RED` so users know something went wrong.

**Files to Edit:**

- `cli.py`:
    - If `--verbose` is set, print a bit more detail (e.g., brief reasoning steps from the LLM, in a muted color like `DIM` or `WHITE`).
    - On errors, `colored_print("Error: Something went wrong!", color="RED")`.
- When user refines a query, print instructions in `color="CYAN"` and final results in `YELLOW` or `GREEN`.

**Tests:**

- `test_cli.py`: Check different verbosity levels.
- Simulate tool failure and verify correct error message color.

### Step 8: CTags and Other Advanced Tools Completion

**Goal:**  
Ensure CTags tool and caching logic is stable and well-integrated. Confirm colors are used consistently for tool invocation messages.

**Checks:**

- Ask queries that use ctags. Confirm summaries are printed and that the tool invocation steps are colored differently than final summaries.

### Step 9: Integration Testing & Polish

**Goal:**  
Write integration tests, simulate user sessions. Check that all CLI messages, including prompts, summaries, and errors, use colorization consistently.

**Files to Edit:**

- `tests/test_integration.py`:
    - Test a full scenario: user queries code, LLM invokes a tool, user approves, results summarized.
    - Check that output lines contain `[codesearch]` and appropriate color formatting (You may not test actual color codes easily, but at least test presence of the prefix).

**Final Polish:**

- Update `README.md` to mention color support and how it helps distinguish different output types.
- Ensure `colorama.init()` is called once at the start, likely in `cli.py` or a small utility file.

---

**Final Note:**  
By integrating colorization early (Step 3) in a simple helper function, all subsequent steps and outputs are easily stylized. You can refine color choices as you go. This incremental approach ensures that by the time you are testing and integrating with real LLM and tools, you already have a consistent way to present different kinds of information visually.

This plan provides a detailed roadmap and shows you how to weave colorized output into the development process from the start.
