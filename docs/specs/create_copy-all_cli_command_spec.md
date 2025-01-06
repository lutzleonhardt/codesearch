# Copy All Messages as JSON Command Specification

## High-Level Objective

- Add a new `/copy-all` command to export the entire chat history as nicely formatted JSON to the clipboard

## Mid-Level Objective

- Create new command type for JSON export functionality
- Implement message history JSON formatting with proper indentation
- Add clipboard integration for the formatted JSON output
- Update command documentation and help text
- Ensure proper error handling

## Implementation Notes and Constraints
- Use agent_output.all_messages_json() for proper serialization of messages
- Maintain consistent command handling patterns
- Follow existing error handling practices
- Must handle empty message history gracefully
- Messages must be JSON-serializable
- technical: "Use existing pydantic-ai serialization or json.dumps() with indent=2"
- compatibility: "Handle both RunResult and basic message objects"
- ux: "Clear success/error messages to user"
- performance: "Handle large message histories efficiently"

## Context

### Beginning context
- `src/commands.py`
- `src/cli.py`
- `src/agent/main_agent.py`

### Ending context
- `src/commands.py` (modified)
- `src/cli.py`
- `src/agent/main_agent.py`

## Implementation Status

1. Added new COPY_ALL command type to CommandType enum ✓

2. Updated CommandResult to handle messages_json from agent_output ✓

3. Implemented /copy-all command handler:
   - Uses agent_output.all_messages_json() for serialization ✓
   - Copies formatted JSON to clipboard ✓
   - Returns appropriate CommandResult ✓

4. Added help documentation:
   - Added /copy-all to help message ✓
   - Documents clipboard behavior ✓

5. Implemented error handling:
   - Handles empty message history ✓
   - Handles missing messages_json ✓
   - Handles clipboard errors ✓
   - Shows clear success/error messages ✓

6. Updated CLI to handle COPY_ALL command type ✓

All tasks completed and tested. The command is now fully functional.
