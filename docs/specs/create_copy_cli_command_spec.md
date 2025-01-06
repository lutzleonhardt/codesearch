# Copy Latest Message Command Implementation

## High-Level Objective
- Add a new `/copy` command that copies the latest final result from the chat to the system clipboard

## Mid-Level Objective
- Add new command type for copy functionality
- Implement clipboard interaction using pyperclip
- Search backwards through message history for final_result tool calls
- Extract and copy answer content from args_dict
- Provide clear user feedback for the copy operation
- Handle edge cases (no messages, no final result found)

## Implementation Notes
- Add pyperclip as new dependency in requirements.txt
- Follow existing command pattern and code structure
- Use colored output for user feedback
- Search message history for ModelResponse with tool_name='final_result'
- Extract 'answer' field from args_dict structure
- Handle clipboard operations safely
- Provide appropriate error messages when no result found

## Technical Details
- Search backwards through messages for ModelResponse
- Check for ToolCallPart with tool_name='final_result'
- Extract answer from args_dict.args_dict['answer']
- Copy extracted content to clipboard
- Handle error cases with clear user feedback
- Handle COPY command type like CONTINUE in CLI loop

## Context

### Beginning context
- `src/commands.py`
- `requirements.txt`

### Ending context
- `src/commands.py` (modified)
- `requirements.txt` (modified to include pyperclip)

## Low-Level Tasks
> Ordered from start to finish

1. Update dependencies
```aider
UPDATE requirements.txt:
    ADD pyperclip to requirements
Make sure it's compatible with current Python version
```

2. Add new command type and import
```aider
UPDATE src/commands.py:
    ADD COPY to CommandType enum
    ADD import pyperclip at top of file
    ENSURE proper organization of imports
```

3. Implement copy command handler
```aider
UPDATE src/commands.py:
    UPDATE handle_command function:
    ADD case '/copy' implementation:
        - Check for empty messages
        - Search backwards for final_result tool call
        - Extract answer from args_dict
        - Copy to clipboard
        - Show feedback
        - Return proper CommandResult
```

4. Update help documentation
```aider
UPDATE src/commands.py:
    UPDATE where help text is defined:
    ADD documentation for /copy command:
        Include description
        Show usage example
```
