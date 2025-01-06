from __future__ import annotations

import logging
import os
from typing import Any, List, TypeAlias, Optional, Union

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel

from .prompts import SYSTEM_PROMPT
from .schemas import AgentOutput, Deps, PartialContent
from ..config.settings import API_KEY, MODEL
from ..tools.ctags import CtagsTool
from ..tools.directory import DirectoryTool, DirectoryPage
from ..tools.file_writer import FileWriterTool
from ..tools.terminal import TerminalTool
from ..tools.file_reader import FileReaderTool

# Type alias for directory response
DirectoryResponse: TypeAlias = PartialContent[DirectoryPage]
from ..tools.base import ToolAbortedException


def format_message(content: Any) -> str:
    """Format message content to ensure it's a string."""
    if isinstance(content, str):
        return content
    return str(content)


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
def directory(ctx: RunContext[Deps], intention_of_this_call: str, relative_path_from_project_root: str, max_depth: int,
              additional_exclude_dirs=None,
              file_filter: Optional[str] = None,
              hide_empty_folder: bool = False) -> PartialContent[List[str]]:
    """Get the directory structure at the given path (also recursively). Use it for get an overview of the project structure and for filter files and folders. It also provides metadata for lastModified and fileSize.

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation. This information will be used by a secondary AI agent to extract and summarize only the content directly relevant to your stated goal, helping reduce context and focus the response. The more precise you are about your intended outcome, the more accurately it will be filtered and compressed.
        relative_path_from_project_root: The relative path from the project root to analyze
        max_depth: Maximum depth to traverse in the directory tree
        additional_exclude_dirs: Additional directories to exclude beyond the default exclusions. The defaults are: [".git", ".hg", ".svn", ".DS_Store", "node_modules", "bower_components", "dist", "build", "env", "venv", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".cache", ".idea", ".vscode", "vendor", "out", "target", ".bundle", "coverage", "bin", "nuget", ".nuget"]
        file_filter: Optional pattern to filter files (e.g. "*.py" for Python files). It will also return empty folders.
        hide_empty_folder: If True, folders that have no matching files (based on file_filter) and no non-empty subfolders will be hidden from the results.

    Returns:
        PartialContent[List[str]]: A response containing the directory structure. The result could be truncated (see result_is_complete).
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
        full_path = os.path.normpath(os.path.join(ctx.deps.project_root, relative_path_from_project_root))
        logger.info(f"Scanning directory at {full_path} with max_depth={max_depth}")
        result: DirectoryPage = directory_tool.run(
            intention_of_this_call=intention_of_this_call,
            path=full_path,
            limit=ctx.deps.limit,
            max_depth=max_depth,
            exclude_dirs=exclude_dirs,
            verbose=ctx.deps.verbose,
            file_filter=file_filter,
            hide_empty_folder=hide_empty_folder
        )
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
def file_writer(
    ctx: RunContext[Deps],
    intention_of_this_call: str,
    relative_path_from_project_root: str,
    content: str
) -> PartialContent[int]:
    """
    Overwrite or create a file with the provided content.

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation. This information will be used by a secondary AI agent to extract and summarize only the content directly relevant to your stated goal, helping reduce context and focus the response. The more precise you are about your intended outcome, the more accurately it will be filtered and compressed.
        relative_path_from_project_root (str): The file path relative to the project root.
        content (str): The content to write to the file.
    Returns how many bytes were written.
    """
    file_writer_tool = FileWriterTool()
    full_path = os.path.normpath(
        os.path.join(ctx.deps.project_root, relative_path_from_project_root)
    )

    try:
        result = file_writer_tool.run(
            intention_of_this_call=intention_of_this_call,
            file_path=full_path,
            content=content,
            verbose=ctx.deps.verbose
        )
        written_bytes = result["written_bytes"]
        return PartialContent(
            total_length=written_bytes,
            returned_length=written_bytes,
            content=written_bytes,
            error=False,
            result_is_complete=True
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
        logger.error(f"Error in file_writer tool: {str(e)}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=True,
            aborted=False,
        )


@agent.tool
def file_reader(ctx: RunContext[Deps], intention_of_this_call: str, relative_path_from_project_root: str) -> \
PartialContent[List[str]]:
    """
    Read the contents of a file.

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation. This information will be used by a secondary AI agent to extract and summarize only the content directly relevant to your stated goal, helping reduce context and focus the response. The more precise you are about your intended outcome, the more accurately it will be filtered and compressed.
        relative_path_from_project_root (str): The file path relative to the project root.

    Returns:
        PartialContent[List[str]]: A list of all lines in the file.
    """
    file_reader_tool = FileReaderTool()
    full_path = os.path.normpath(os.path.join(ctx.deps.project_root, relative_path_from_project_root))
    try:
        result = file_reader_tool.run(intention_of_this_call=intention_of_this_call, file_path=full_path,
                                      verbose=ctx.deps.verbose)
        # Since there's no truncation, result_is_complete is always True
        return PartialContent(
            total_length=result["total_lines"],
            returned_length=result["returned_lines"],
            content=result["lines"],
            error=False,
            result_is_complete=True
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
        logger.error(f"Error in file_reader tool: {str(e)}")
        return PartialContent(
            total_length=0,
            returned_length=0,
            content=[],
            error=True,
            aborted=False,
        )


@agent.tool
def terminal(ctx: RunContext[Deps], intention_of_this_call: str, command: str) -> PartialContent[List[str]]:
    """
    Run a terminal command to explore the codebase.
    Recommended commands: rg (with context lines), find, ls, cat. Always think about narrowing down the scope of the command!

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation. This information will be used by a secondary AI agent to extract and summarize only the content directly relevant to your stated goal, helping reduce context and focus the response. The more precise you are about your intended outcome, the more accurately it will be filtered and compressed.
        command (str): The command to run.

    PartialContent[List[str]]: Lines of the stdout the tool was written to. Result could be truncated!
    """
    terminal_tool = TerminalTool()
    try:
        result = terminal_tool.run(
            intention_of_this_call=intention_of_this_call,
            command=command,
            limit=ctx.deps.limit,
            verbose=ctx.deps.verbose,
            root_dir=ctx.deps.project_root
        )
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
def ctags_readtags_tool(ctx: RunContext[Deps], intention_of_this_call: str, action: str,
                        relative_path_from_project_root: str = "", symbol: str = "",
                        kind: str = "", is_symbol_regex: bool = False) -> PartialContent[List[str]]:
    """
    Use this to get symbol information about the codebase(i.e. how many classes, where is this function,  method, variable, ...see kind argument).
    Query tags using universal-ctags and readtags utilities. This tool provides access to ctags and readtags functionalities.
    You need ALWAYS to first generate the tags file using the 'generate_tags' action.
    The result could be truncated (see result_is_complete). HINT: imports are not considered as symbols!
    Actions:
        'generate_tags': Generate or update a tags file for the given path.
        'filter': Filter tags by symbol and/or kind. If neither is provided, lists all tags. Regex for symbols is supported, see is_symbol_regex

    Args:
        ctx: The run context with dependencies
        intention_of_this_call (required): Provide a clear, specific statement of what you aim to accomplish with this tool invocation. This information will be used by a secondary AI agent to extract and summarize only the content directly relevant to your stated goal, helping reduce context and focus the response. The more precise you are about your intended outcome, the more accurately it will be filtered and compressed.
        action (str): The action to perform.
        relative_path_from_project_root (str): The file or directory to generate tags from (with action 'generate_tags'). The file or directory you want to get tag information from (with action 'filter').
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
            intention_of_this_call=intention_of_this_call,
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
