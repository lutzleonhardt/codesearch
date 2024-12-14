from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from .prompts import SYSTEM_PROMPT, ASSISTANT_PROMPT
from .schemas import AgentOutput
from ..config.settings import API_KEY, MODEL
from ..tools.directory import DirectoryTool


@dataclass
class Deps:
    """Dependencies for the agent"""
    pass

def format_message(content: Any) -> str:
    """Format message content to ensure it's a string."""
    if isinstance(content, str):
        return content
    return str(content)

agent = Agent(
    model=OpenAIModel(
        MODEL,
        api_key=API_KEY
    ),
    system_prompt=SYSTEM_PROMPT + ASSISTANT_PROMPT,
    deps_type=Deps,
    retries=2,
    result_type=AgentOutput
)

@agent.tool
def directory(ctx: RunContext[Deps], path: str) -> dict:
    """Get the directory structure at the given path.

    Args:
        ctx: The run context with dependencies
        path: The filesystem path to analyze

    Returns:
        dict: A dictionary containing the directory structure
    """
    directory_tool = DirectoryTool()
    return directory_tool.run(path=path)

