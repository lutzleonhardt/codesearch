# codesearch
codesearch is a Python-based command-line tool designed to help users explore and understand their codebase via an LLM-backed agent. 

### High-Level Overview

`codesearch` is a Python-based command-line tool designed to help users explore and understand their codebase via an LLM-backed agent. It integrates with Aider but can be used standalone. It uses Pydantic AI for agentic behavior and tool invocation. The tool operates interactively, prompting the user before tool usage and allowing them to refine queries. The LLM is instructed to always summarize tool outputs, referencing relevant files and snippets, without including raw tool results verbatim.
