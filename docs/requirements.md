### High-Level Overview

`codesearch` is a Python-based command-line tool designed to help users explore and understand their codebase via an LLM-backed agent. It integrates with Aider but can be used standalone. It uses Pydantic AI for agentic behavior and tool invocation. The tool operates interactively, prompting the user before tool usage and allowing them to refine queries. The LLM is instructed to always summarize tool outputs, referencing relevant files and snippets, without including raw tool results verbatim.

---

### Core Requirements

1. **Implementation Language and Framework:**

    - Written entirely in Python.
    - Use Pydantic AI for the agent implementation, including tool definition, parsing, and invocation.
2. **Interactive Experience:**

    - **User-in-the-Loop:**
        - Before executing any tool at the request of the LLM, prompt the user for approval.
        - After receiving LLM responses, the user can refine the query, add context, or continue.
3. **CLI Integration and Output Formatting:**

    - **Colors and Prefix:**
        - Output lines should be prefixed (e.g., “[codesearch]”) and use colors to differentiate from other tools or shell output.
    - **Verbosity Control:**
        - A `--verbose` parameter (boolean) controls the level of output detail.
        - Even in verbose mode, the raw LLM chain-of-thought or full tool output is not displayed, only summaries and key reasoning steps.
4. **LLM Prompting and Output Requirements:**

    - **Summarization:**
        - The LLM must always summarize the results from tool usage, including file paths and brief code snippets.
        - Summaries should be concise and contain all necessary information to continue reasoning effectively.
    - **No Raw LLM Output in Chat:**
        - The LLM’s internal reasoning and raw outputs are not directly included in `codesearch`’s chat. Only the summarized content is shown.
5. **Logging and Error Handling:**

    - **Logging:**
        - Log all interactions (queries, responses, user approvals, errors) to a logfile.
    - **Error Handling:**
        - Gracefully handle errors and inform the user.
        - Suggest alternatives or next steps if tools fail or data is unavailable.
6. **Testing and Quality Assurance:**

    - **Unit Tests:**
        - Cover core functionalities, including CLI parsing, LLM interaction logic, and tool usage flow.
    - Integration tests can be added later as the project matures.
7. **Configuration and Execution:**

    - **Configuration Sources:**
        - Environment variables, CLI parameters, and config files (similar to Aider) to specify LLM model, logging, verbosity, and other settings.
    - **LLM Model Selection:**
        - Same logic as Aider, configurable via env or config (e.g., `OPENAI_MODEL`).
    - **Project Root Directory:**
        - A parameter (e.g., `--root-dir`) to specify the root project directory to explore. Defaults to the current working directory (cwd).
8. **Tools and Capabilities (Initial Set):**

    - **CTags Tool:**
        - Use ctags to query code symbols and references.
        - Conclusion: It is generally not efficient to rebuild the ctags index on every invocation.
            - Add a boolean parameter (e.g., `--rebuild-ctags`) that defaults to False. When False, ctags data is cached and reused unless specifically changed.
            - When True, rebuild the ctags index from scratch each time the tool is used (useful if the codebase has changed).
    - **Directory Structure Tool:**
        - Lists directories and files, returning a structured format. The LLM then summarizes and references relevant files.
    - **Terminal Access Tool:**
        - Executes commands like `ls` or `grep` (with user approval) and returns the results, which the LLM summarizes.
    - File Content Retrieval Tool:
        - Ability to read the contents of a file or a snippet within it.
        - Useful for targeted exploration: once CTags or directory listings identify a candidate file, the LLM can fetch its relevant code snippet.
1. **Output Length and Summarization Constraints:**

    - If output is large, the LLM should summarize to fit within a set limit (e.g., ~100 lines).
    - If still too large, the LLM can request a more targeted approach or prompt the user to refine the query.
10. **Extensibility and Future Work:**

    - The design should easily accommodate additional tools later (e.g., file content reading, outlines).
    - The configuration, prompts, and summaries can be updated as needed.
