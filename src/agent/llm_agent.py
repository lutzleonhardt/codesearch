from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, List, TypeAlias

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from .prompts import SYSTEM_PROMPT, ASSISTANT_PROMPT
from .schemas import AgentOutput, Deps, PartialContent
from ..config.settings import API_KEY, MODEL
from ..tools.directory import DirectoryTool, DirEntry, DirectoryPage

# Type alias for directory response
DirectoryResponse: TypeAlias = PartialContent[DirectoryPage]
from ..tools.base import ToolAbortedException

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

logger = logging.getLogger(__name__)

@agent.tool
def directory(ctx: RunContext[Deps], relative_path_from_project_root: str, max_depth: int, exclude_dirs = None) -> DirectoryResponse:
    """Get the directory structure at the given path.

    Args:
        ctx: The run context with dependencies
        relative_path_from_project_root: The relative path from the project root to analyze
        max_depth: Maximum depth to traverse in the directory tree
        exclude_dirs: A list of directories to exclude from the directory tree, defaults to ["node_modules", "venv", "bin", "dist", ".git", ".svn", "__pycache__"]

    Returns:
        PartialContent: A paginated response containing the directory structure
    """
    directory_tool = DirectoryTool()
    try:
        if exclude_dirs is None:
            exclude_dirs = ["node_modules", "venv", "bin", "dist", ".git", ".svn", "__pycache__"]
        full_path = os.path.normpath(os.path.join(ctx.deps.project_root, relative_path_from_project_root))
        logger.info(f"Scanning directory at {full_path} with max_depth={max_depth}")
        result = directory_tool.run(path=full_path, limit=ctx.deps.limit, max_depth=max_depth, exclude_dirs=exclude_dirs)
        logger.debug(f"Found {result['total_entries']} entries, returning {result['returned_entries']}")
        return PartialContent(
            total_length=result["total_entries"],
            returned_length=result["returned_entries"],
            content=result["entries"],
            error=False
        )
    except ToolAbortedException:
        logger.info(f"Directory scanning aborted for {relative_path_from_project_root}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=False,
            aborted=True
        )
    except Exception as e:
        logger.error(f"Error scanning directory {relative_path_from_project_root}: {str(e)}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=True,
            aborted=False
        )

