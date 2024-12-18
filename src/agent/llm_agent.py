from __future__ import annotations

import logging
import os
from typing import Any, List, TypeAlias, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from .prompts import SYSTEM_PROMPT
from .schemas import AgentOutput, Deps, PartialContent
from ..config.settings import API_KEY, MODEL
from ..tools.ctags import CtagsTool
from ..tools.directory import DirectoryTool, DirectoryPage
from ..tools.terminal import TerminalTool

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
    system_prompt=SYSTEM_PROMPT,
    deps_type=Deps,
    retries=2,
    result_type=AgentOutput
)

logger = logging.getLogger(__name__)


@agent.tool
def directory(ctx: RunContext[Deps], relative_path_from_project_root: str, max_depth: int, exclude_dirs=None,
              file_filter: Optional[str] = None) -> PartialContent[DirectoryResponse]:
    """Get the directory structure at the given path. The result could be truncated (see result_is_complete). It also returns empty folders.

    Args:
        ctx: The run context with dependencies
        relative_path_from_project_root: The relative path from the project root to analyze
        max_depth: Maximum depth to traverse in the directory tree
        exclude_dirs: A list of directories to exclude from the directory tree. Defaults to: [".git", ".hg", ".svn",
            ".DS_Store", "node_modules", "bower_components", "dist", "build", "env", "venv", ".venv", "__pycache__",
            ".pytest_cache", ".mypy_cache", ".cache", ".idea", ".vscode", "vendor", "out", "target", ".bundle",
            "coverage", "bin"]
        file_filter: Optional pattern to filter files (e.g. "*.py" for Python files). It will also return empty folders.

    Returns:
        PartialContent[List[CtagsEntry]]: A paginated response containing the directory structure. The result could be truncated (see result_is_complete).
    """
    directory_tool = DirectoryTool()
    try:
        if exclude_dirs is None:
            exclude_dirs = [
                ".git", ".hg", ".svn", ".DS_Store", "node_modules", "bower_components",
                "dist", "build", "env", "venv", ".venv", "__pycache__", ".pytest_cache",
                ".mypy_cache", ".cache", ".idea", ".vscode", "vendor", "out", "target",
                ".bundle", "coverage", "bin"
            ]
        full_path = os.path.normpath(os.path.join(ctx.deps.project_root, relative_path_from_project_root))
        logger.info(f"Scanning directory at {full_path} with max_depth={max_depth}")
        result = directory_tool.run(path=full_path, limit=ctx.deps.limit, max_depth=max_depth,
                                    exclude_dirs=exclude_dirs, verbose=ctx.deps.verbose, file_filter=file_filter)
        logger.debug(f"Found {result['total_entries']} entries, returning {result['returned_entries']}")
        result_is_complete = result["returned_entries"] == result["total_entries"]
        return PartialContent(
            total_length=result["total_entries"],
            returned_length=result["returned_entries"],
            content=result["entries"],
            error=False,
            result_is_complete=result_is_complete
        )
    except ToolAbortedException:
        logger.info(f"Directory scanning aborted for {relative_path_from_project_root}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=False,
            aborted=True,
        )
    except Exception as e:
        logger.error(f"Error scanning directory {relative_path_from_project_root}: {str(e)}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=True,
            aborted=False,
        )


@agent.tool
def terminal(ctx: RunContext[Deps], command: str) -> PartialContent[List[str]]:
    """
    Run a terminal command to explore the codebase.
    Recommended commands: rg (with context lines), find, ls, cat. Always think about narrowing down the scope of the command!

    Args:
        command (str): The command to run.

    PartialContent[List[str]]: Lines of the stdout the tool was written to. Result could be truncated!
    """
    terminal_tool = TerminalTool()
    try:
        result = terminal_tool.run(command=command, limit=ctx.deps.limit, verbose=ctx.deps.verbose)
        result_is_complete = result["returned_lines"] == result["total_lines"]
        return PartialContent(
            total_length=result["total_lines"],
            returned_length=result["returned_lines"],
            content=result["lines"],
            error=False,
            result_is_complete=result_is_complete
        )
    except ToolAbortedException:
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=False,
            aborted=True,
        )
    except Exception as e:
        logger.error(f"Error in terminal tool: {str(e)}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=True,
            aborted=False,
        )


@agent.tool
def ctags_readtags_tool(ctx: RunContext[Deps], action: str, relative_path_from_project_root: str = "", symbol: str = "",
                        kind: str = "", is_symbol_regex: bool = False) -> PartialContent[List[str]]:
    """
    Query tags using universal-ctags and readtags utilities. This tool provides access to ctags and readtags functionalities.
    You need ALWAYS to first generate the tags file using the 'generate_tags' action.
    The result could be truncated (see result_is_complete). HINT: imports are not considered as symbols!
    Actions:
        'generate_tags': Generate or update a tags file for the given path.
        'filter': Filter tags by symbol and/or kind. If neither is provided, lists all tags. Regex for symbols is supported, see is_symbol_regex

    Args:
        action (str): The action to perform.
        relative_path_from_project_root (str): The file or directory to generate tags from (required for 'generate_tags').
        symbol (str): The symbol to search for (can be a regex when is_symbol_regex).
        kind (str): The kind of symbol to filter by (c: classes, f: functions, v: variables, m: class/struct members and methods, d: macro definitions, t: typedefs, e: enumerators, g: enumerations, s: structures, u: unions, p: function prototypes).
        is_symbol_regex (bool): If True, treat the symbol parameter as a regular expression pattern.

    Returns:
        PartialContent[List[str]]: A list of raw ctags output lines. Each line contains tab-separated fields with symbol information. sample:
        _run    src/tools/base.py       /^    def _run(self, **kwargs):$/;"     kind:m  class:BaseTool
    """
    input_path = os.path.normpath(os.path.join(ctx.deps.project_root, relative_path_from_project_root))
    ctags_tool = CtagsTool()
    try:
        result = ctags_tool.run(
            action=action,
            input_path=input_path,
            symbol=symbol,
            kind=kind,
            limit=ctx.deps.limit,
            verbose=ctx.deps.verbose,
            is_symbol_regex=is_symbol_regex,
        )
        result_is_complete = result["returned_entries"] == result["total_entries"]
        return PartialContent(
            total_length=result["total_entries"],
            returned_length=result["returned_entries"],
            content=result["entries"],
            error=False,
            result_is_complete=result_is_complete
        )
    except ToolAbortedException:
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=False,
            aborted=True,
        )
    except Exception as e:
        logger.error(f"Error in ctags tool: {str(e)}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=True,
            aborted=False,
        )
