from __future__ import annotations

import logging
from typing import List

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel

from .prompts import SYSTEM_PROMPT, USER_PROMPT
from .schemas import SummarizerDeps, SummarizerOutput
from ..config.settings import API_KEY, MODEL

logger = logging.getLogger(__name__)

summarizer = Agent(
    model=AnthropicModel(
        MODEL,
        api_key=API_KEY
    ),
    system_prompt=SYSTEM_PROMPT,
    deps_type=SummarizerDeps,
    retries=1,
    result_type=SummarizerOutput
)

async def summarize_tool_output(
    tool_output: List[str],
    intention: str,
    max_lines: int = 200,
    verbose: bool = False
) -> List[str]:
    """
    Summarize tool output based on the original intention.

    Args:
        tool_output: The raw output from a tool execution
        intention: The original intention why the tool was called
        max_lines: Maximum number of lines for the summary
        verbose: Enable verbose output

    Returns:
        List of strings containing the summarized tool output
    """
    deps = SummarizerDeps(max_lines=max_lines, verbose=verbose)

    # Truncate if more than 1000 lines
    was_truncated = False
    original_length = len(tool_output)
    if original_length > 1000:
        tool_output = tool_output[:1000]
        was_truncated = True
        if verbose:
            logger.info(f"Tool output truncated from {original_length} to 1000 lines")

    # Convert list of lines to single string
    output_text = "\n".join(tool_output)

    # Prepare prompt with actual content
    prompt = USER_PROMPT.format(
        tool_output=output_text,
        intention=intention,
        max_lines=max_lines,
        truncation_notice=f"(Note: Output was truncated from {original_length} to 1000 lines)" if was_truncated else ""
    )

    try:
        prefix = f"The tool result output was too long ({original_length} lines), here is a summarization: \n"
        result = await summarizer.run(prompt, deps=deps)
        result.data.summary = prefix + result.data.summary
        return result.data.summary.splitlines()
    except Exception as e:
        logger.error(f"Error in summarizer agent: {str(e)}")
        return f"Error summarizing output: {str(e)}"
