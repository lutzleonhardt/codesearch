SYSTEM_PROMPT = """
SYSTEM: You are a helpful assistant for exploring a given codebase. Your primary objective is to answer the USER’s questions by examining the codebase. Follow these rules:

1. **Step-by-Step Plan**:
   - First, deeply analyze the USER’s question.
   - Propose potential solution approaches and assign each a confidence level.
   - Select the approach with the highest confidence.

2. **Tool Usage**:
   - It is always a good idea to show the repo map with the tool "directory" with the default max_depth=99999.
   - Before invoking any tool, briefly describe what you intend to achieve with that call.
   - Only request one tool at a time!
   - The response of tool calls could be summarized if too long
   - also take into consideration possible code-behind files 

3. **Tools Hints**
    3.1. Use ctags_readtags_tool for:
       - Finding symbol definitions (functions, classes, variables)
       - Understanding code structure
       - Symbol location queries

    3.2. Use 'rg' for:
       - Searching through file content
       - Finding text patterns
       - Searching code comments or documentation
       - When needing context around matches

4. **Stuck or Loops**:
   - If you get stuck, try a different approach. Present a revised plan to the USER and ask for confirmation before proceeding.

5. **Completeness and Clarity**:
   - Final answers should be as complete as possible: include code snippets, **FULL file paths**, and any other pertinent details.
"""

USER_PROMPT = """
USER asked: {question}.

Make a **Step-by-Step Plan**:
   - First, deeply analyze my question.
   - Propose potential solution approaches and assign each a confidence level.
   - Select the approach with the highest confidence.
"""

SPEC_PROMPT = """# Write a specification based on the chat history and return it. Do not use tools like "file_writer" to create a file!
The Low-Level Tasks describe the WHAT with providing details for the interface/scaffolding. The spec is used by an AI Code assistant and figures out the HOW.

- Use this template for it:
---
# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- [High level goal goes here - what do you want to build?]

## Mid-Level Objective

- [List of mid-level objectives - what are the steps to achieve the high-level objective?]
- [Each objective should be concrete and measurable]
- [But not too detailed - save details for implementation notes]

## Implementation Notes and Constraints
- [Important technical details - what are the important technical details?]
- [Dependencies and requirements - what are the dependencies and requirements?]
- [Coding standards to follow - what are the coding standards to follow?]
- [Other technical guidance - what are other technical guidance?]
- [Boundaries and constraints - what are the boundaries and limitations?]

## Context

### Beginning context
- [List of files that exist at start - what files exist at start?]

### Ending context  
- [List of files that will exist at end - what files will exist at end?]

## Low-Level Tasks
> Ordered from start to finish

1. [First task - what is the first task?]
```aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?
```
2. [Second task - what is the second task?]
```aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?
```
3. [Third task - what is the third task?]
```aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?
```
---

- here is a sample of the output:
---
# HTML Slider Output and Charts Feature

## High-Level Objective

- Create an interactive HTML output format with dynamic word frequency visualization

## Mid-Level Objective

- Build new HTML output format with slider-based word frequency filtering
- Add radial bar and bubble chart visualizations for word frequencies
- Extend CLI to support new output formats
- Ensure comprehensive test coverage

## Implementation Notes and Constraints
- No need to import any external libraries beyond existing dependencies
- Comment every new function
- For CLI commands add usage examples starting with `uv run main.py`
- Follow existing code patterns and type safety practices
- Add tests for all new functionality
- technical: "Only vanilla JS, no external deps",
- security: "No unsafe HTML injection",
- performance: "Must render under 100ms",
- ux: "Smooth slider interaction (60fps)"


## Context

### Beginning context
- `src/let_the_code_write_itself/output_format.py`
- `src/let_the_code_write_itself/chart.py`
- `src/let_the_code_write_itself/main.py`
- `src/let_the_code_write_itself/tests/output_format_test.py`
- `src/let_the_code_write_itself/tests/chart_test.py`

### Ending context
- `src/let_the_code_write_itself/output_format.py`
- `src/let_the_code_write_itself/chart.py`
- `src/let_the_code_write_itself/main.py`
- `src/let_the_code_write_itself/tests/output_format_test.py`
- `src/let_the_code_write_itself/tests/chart_test.py`

## Low-Level Tasks
> Ordered from start to finish

1. Add new HTML output format with slider
```aider
UPDATE src/let_the_code_write_itself/output_format.py:
    CREATE format_as_html_with_slider_filter() function:
        Add HTML template with slider control
        Add JavaScript for dynamic filtering
        MIRROR format_as_html()
```

2. Add new chart visualizations
```aider
UPDATE src/let_the_code_write_itself/chart.py:
    CREATE create_radial_bar_chart(word_counts: WordCounts), create_bubble_chart(...)
```

3. Update CLI interface
```aider
UPDATE src/let_the_code_write_itself/main.py:
    ADD support for checking .htmlsld extension and calling format_as_html_with_slider_filter()
        Be sure to use .html when saving the file, .htmlsld is just for checking
    ADD support for 'radial' and 'bubble' choices and calling respective chart functions

```

4. Add comprehensive tests
```aider
UPDATE test files:
    ADD test_format_as_html_with_slider_filter()
    ADD test_create_radial_bar_chart()
    ADD test_create_bubble_chart()
```

---

"""
