from __future__ import annotations

import logging
import os
from typing import Any, List, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel

from .prompts import SYSTEM_PROMPT
from .schemas import AgentOutput, Deps, MaybeSummarizedContent
from ..config.settings import API_KEY, MODEL
from ..tools.base import ToolAbortedException
from ..tools.ctags import CtagsTool
from ..tools.directory import DirectoryTool
from ..tools.file_reader import FileReaderTool
from ..tools.file_writer import FileWriterTool
from ..tools.terminal import TerminalTool


def format_message(content: Any) -> str:
    """Format message content to ensure it's a string."""
    if isinstance(content, str):
        return content
    return str(content)


def get_safe_path(project_root: str, relative_path: str) -> str:
    """
    Safely join and normalize paths to prevent directory traversal outside project root.

    Args:
        project_root (str): The root directory of the project
        relative_path (str): The relative path to join with the root

    Returns:
        str: A safe, normalized absolute path that is guaranteed to be within project_root

    Raises:
        ValueError: If the resulting path would be outside the project root
    """
    # Normalize both paths
    project_root = os.path.normpath(project_root)

    # Join paths and normalize
    full_path = os.path.normpath(os.path.join(project_root, relative_path))

    # Ensure the path is within project root
    if not full_path.startswith(project_root):
        raise ValueError(f"Access denied: Path '{full_path}' is outside project root '{project_root}'")

    return full_path


agent = Agent(
    model=AnthropicModel(
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
async def directory(ctx: RunContext[Deps], intention_of_this_call: str, relative_path_from_project_root: str, max_depth: int,
              additional_exclude_dirs=None,
              file_filter: Optional[str] = None,
              hide_empty_folder: bool = False) -> MaybeSummarizedContent[List[str]]:
    """Get the directory structure at the given path (also recursively). Use it for get an overview of the project structure and for filter files and folders. It also provides metadata for lastModified and fileSize.

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation: "I do this to get this information."
        relative_path_from_project_root: The relative path from the project root to analyze
        max_depth: Maximum depth to traverse in the directory tree
        additional_exclude_dirs: Additional directories to exclude beyond the default exclusions. The defaults are: [".git", ".hg", ".svn", ".DS_Store", "node_modules", "bower_components", "dist", "build", "env", "venv", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".cache", ".idea", ".vscode", "vendor", "out", "target", ".bundle", "coverage", "bin", "nuget", ".nuget"]
        file_filter: Optional pattern to filter files (e.g. "*.py" for Python files)
        hide_empty_folder: If True, folders that have no matching files (based on file_filter) and no non-empty subfolders will be hidden from the results.

    Returns:
        MaybeSummarizedContent[List[str]]: A response containing the directory structure. The result could be summarized.
    """
    directory_tool = DirectoryTool()
    try:
        default_exclude_dirs = [
                ".git", ".hg", ".svn", ".DS_Store", "node_modules", "bower_components",
                "dist", "build", "env", "venv", ".venv", "__pycache__", ".pytest_cache",
                ".mypy_cache", ".cache", ".idea", ".vscode", "vendor", "out", "target",
                ".bundle", "coverage", "bin", "nuget", ".nuget"
            ]
        exclude_dirs = default_exclude_dirs + (additional_exclude_dirs or [])
        full_path = get_safe_path(ctx.deps.project_root, relative_path_from_project_root)
        logger.info(f"Scanning directory at {full_path} with max_depth={max_depth}")
        if file_filter:
            file_filter="*."+file_filter.lstrip(".") if file_filter.startswith(".") else file_filter
        result = await directory_tool.run(
            intention_of_this_call=intention_of_this_call,
            path=full_path,
            limit=ctx.deps.limit,
            max_depth=max_depth,
            exclude_dirs=exclude_dirs,
            verbose=ctx.deps.verbose,
            file_filter=file_filter,
            hide_empty_folder=hide_empty_folder
        )
        is_summarized = result.get("is_summarized", False)
        content = result.get("summary", result["items"]) if is_summarized else result["items"]
        return MaybeSummarizedContent(
            total_length=result["total_count"],
            content=content,
            error=False,
            is_summarized=is_summarized
        )
    except ToolAbortedException:
        logger.info(f"Directory scanning aborted for {relative_path_from_project_root}")
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=False,
            aborted=True,
            is_summarized=False
        )
    except Exception as e:
        logger.error(f"Error scanning directory {relative_path_from_project_root}: {str(e)}")
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=True,
            aborted=False,
            is_summarized=False
        )

@agent.tool
async def file_writer(
    ctx: RunContext[Deps],
    intention_of_this_call: str,
    relative_path_from_project_root: str,
    content: str
) -> MaybeSummarizedContent[int]:
    """
    Overwrite or create a file with the provided content.

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation: "I do this to get this information."
        relative_path_from_project_root (str): The file path relative to the project root.
        content (str): The content to write to the file.
    Returns:
        MaybeSummarizedContent[List[str]]: Returns how many bytes were written (first element).
    """
    file_writer_tool = FileWriterTool()
    try:
        full_path = get_safe_path(ctx.deps.project_root, relative_path_from_project_root)
        result = await file_writer_tool.run(
            intention_of_this_call=intention_of_this_call,
            file_path=full_path,
            content=content,
            verbose=ctx.deps.verbose
        )
        written_bytes = result["total_count"]
        return MaybeSummarizedContent(
            total_length=written_bytes,
            content=[str(written_bytes)],
            error=False,
            is_summarized=False
        )
    except ToolAbortedException:
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=False,
            aborted=True,
            is_summarized=False
        )
    except Exception as e:
        logger.error(f"Error in file_writer tool: {str(e)}")
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=True,
            aborted=False,
            is_summarized=False
        )


@agent.tool
async def file_reader(ctx: RunContext[Deps], intention_of_this_call: str, relative_path_from_project_root: str) -> MaybeSummarizedContent[List[str]]:
    """
    Read the contents of a file.

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation: "I do this to get this information."
        relative_path_from_project_root (str): The file path relative to the project root.

    Returns:
        MaybeSummarizedContent[List[str]]: A list of all lines in the file. The result could be summarized.
    """
    file_reader_tool = FileReaderTool()
    try:
        full_path = get_safe_path(ctx.deps.project_root, relative_path_from_project_root)
        result = await file_reader_tool.run(
            intention_of_this_call=intention_of_this_call,
            file_path=full_path,
            limit=ctx.deps.limit,
            verbose=ctx.deps.verbose
        )
        # Handle potential summarized content
        is_summarized = result.get("is_summarized", False)
        content = result.get("summary", result["items"]) if is_summarized else result["items"]
        return MaybeSummarizedContent(
            total_length=result["total_count"],
            content=content,
            error=False,
            is_summarized=is_summarized
        )
    except ToolAbortedException:
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=False,
            aborted=True,
            is_summarized=False
        )
    except Exception as e:
        logger.error(f"Error in file_reader tool: {str(e)}")
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=True,
            aborted=False,
            is_summarized=False
        )


@agent.tool
async def terminal(ctx: RunContext[Deps], intention_of_this_call: str, command: str) -> MaybeSummarizedContent[List[str]]:
    """
    Run a terminal command to explore the codebase.
    Recommended commands: rg (with context lines), find, ls, cat. Always think about narrowing down the scope of the command (in big codebases)!

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation: "I do this to get this information."
        command (str): The command to run.

    MaybeSummarizedContent[List[str]]: Lines of the stdout the tool was written to. The result could be summarized.
    """
    terminal_tool = TerminalTool()
    try:
        result = await terminal_tool.run(
            intention_of_this_call=intention_of_this_call,
            command=command,
            limit=ctx.deps.limit,
            verbose=ctx.deps.verbose,
            root_dir=ctx.deps.project_root
        )

        # Check if result was summarized
        is_summarized = result.get("is_summarized", False)
        content = result.get("summary", result["items"]) if is_summarized else result["items"]

        return MaybeSummarizedContent(
            total_length=result["total_count"],
            content=content,
            error=False,
            is_summarized=is_summarized
        )
    except ToolAbortedException:
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=False,
            aborted=True,
            is_summarized=False
        )
    except Exception as e:
        logger.error(f"Error in terminal tool: {str(e)}")
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=True,
            aborted=False,
            is_summarized=False
        )


@agent.tool
async def ctags_readtags_tool(ctx: RunContext[Deps], intention_of_this_call: str, action: str,
                        relative_path_from_project_root: str = "", symbol: str = "",
                        kind: str = "", is_symbol_regex: bool = False) -> MaybeSummarizedContent[List[str]]:
    """
    Use this to get symbol information about the codebase(i.e. how many classes, where is this function,  method, variable, ...see kind argument).
    Query tags using universal-ctags and readtags utilities. This tool provides access to ctags and readtags functionalities.
    You need ALWAYS to first generate the tags file using the 'generate_tags' action.
    HINT: imports are not considered as symbols!
    Actions:
        'generate_tags': Generate or update a tags file for the given path.
        'filter': Filter tags by symbol and/or kind. If neither is provided, lists all tags. Regex for symbols is supported, see is_symbol_regex

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation: "I do this to get this information."
        action (str): The action to perform.
        relative_path_from_project_root (str): The file or directory to generate tags from (with action 'generate_tags'). The file or directory you want to get tag information from (with action 'filter').
        symbol (str): The symbol to search for (can be a regex when is_symbol_regex).
        kind (str): The kind of symbol to filter by (c: classes, f: functions, v: variables, m: class/struct members and methods, d: macro definitions, t: typedefs, e: enumerators, g: enumerations, s: structures, u: unions, p: function prototypes).
        is_symbol_regex (bool): If True, treat the symbol parameter as a regular expression pattern.

    Returns:
        MaybeSummarizedContent[List[str]]: A list of raw ctags output lines (The result could be summarized). Each line contains tab-separated fields with symbol information. sample:
        _run    src/tools/base.py       /^    def _run(self, **kwargs):$/;"     kind:m  class:BaseTool
    """
    try:
        input_path = get_safe_path(ctx.deps.project_root, relative_path_from_project_root)
        ctags_tool = CtagsTool()
        result = await ctags_tool.run(
            intention_of_this_call=intention_of_this_call,
            action=action,
            input_path=input_path,
            symbol=symbol,
            kind=kind,
            limit=ctx.deps.limit,
            verbose=ctx.deps.verbose,
            is_symbol_regex=is_symbol_regex,
        )
        is_summarized = result.get("is_summarized", False)
        content = result.get("summary", result["items"]) if is_summarized else result["items"]
        return MaybeSummarizedContent(
            total_length=result["total_count"],
            content=content,
            error=False,
            is_summarized=is_summarized
        )
    except ToolAbortedException:
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=False,
            aborted=True,
            is_summarized=False
        )
    except Exception as e:
        logger.error(f"Error in ctags tool: {str(e)}")
        return MaybeSummarizedContent(
            total_length=0,
            content=[],
            error=True,
            aborted=False,
            is_summarized=False
        )
