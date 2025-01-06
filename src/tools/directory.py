# /home/lutz/PycharmProjects/codesearch/src/tools/directory.py

import fnmatch
import json
import logging
import os
from datetime import datetime
from typing import List, Optional

from .base import BaseTool
from ..shared import colored_print

logger = logging.getLogger(__name__)

def entry_to_json(
    path: str,
    entry_type: str,
    size: int,
    modified: str
) -> str:
    """Convert entry data to JSON string format."""
    entry_dict = {
        "name": os.path.basename(path),
        "path": path,
        "type": entry_type,
        "size": size,
        "modified": modified
    }
    return json.dumps(entry_dict)


from .types import BaseToolResult

class DirectoryTool(BaseTool):
    def print_verbose_output(self, result: BaseToolResult):
        """Print detailed directory scan results in yellow color"""
        for entry_json in result['items']:
            try:
                entry = json.loads(entry_json)
                entry_type = entry['type'].ljust(10)
                path = entry['path']
                size = f"size={entry['size']}"
                modified = f"modified={entry['modified']}"
                colored_print(f"{entry_type} {path} ({size}, {modified})", color="YELLOW")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse entry JSON: {entry_json}")

    def get_tool_text_start(
        self, path: str, limit: int, max_depth: Optional[int], exclude_dirs: List[str],
        file_filter: Optional[str] = None, hide_empty_folder: bool = False, **kwargs
    ) -> List[str]:
        depth_str = f"max_depth: {max_depth}" if max_depth is not None else ""
        filter_str = f"file_filter: {file_filter}" if file_filter is not None else ""
        return [
            "Query directory",
            f"path: {path}",
            f"limit: {limit} lines (it summarizes output if above)",
            depth_str,
            f"exclude_dirs: {str(exclude_dirs)}",
            filter_str,
            f"hide_empty_folder: {hide_empty_folder}"
        ]

    def _run(
        self,
        intention_of_this_call: str,
        path: str,
        limit: int = 50,
        max_depth: Optional[int] = None,
        exclude_dirs: List[str] = None,
        file_filter: Optional[str] = None,
        hide_empty_folder: bool = False,
        **kwargs
    ) -> BaseToolResult:
        """
        Return a flattened list of directory entries starting from a given path,
        limited by a maximum traversal depth and optionally excluding certain directories.

        :param path: The root directory to start traversal from.
        :param limit: The maximum number of entries to return.
        :param max_depth: The maximum depth of directories to recurse into.
                          If None, there is no depth limit.
        :param exclude_dirs: A list of directory names to exclude.
        """

        if max_depth is None or max_depth == -1:
            # If not specified, treat as unlimited depth.
            max_depth = 999999  # effectively no limit

        logger.info(
            f"Running directory tool with path: {path}, "
            f"limit: {limit}, max_depth: {max_depth}"
        )

        all_entries = []
        self._flatten_helper(
            path,
            exclude_dirs,
            all_entries,
            current_depth=0,
            max_depth=max_depth,
            file_filter=file_filter,
            hide_empty_folder=hide_empty_folder
        )

        result = BaseToolResult(
            total_count=len(all_entries),
            items=all_entries
        )
        return result

    def _flatten_helper(
        self,
        path: str,
        exclude_dirs: List[str],
        flattened: List[str],
        current_depth: int,
        max_depth: int,
        file_filter: Optional[str] = None,
        hide_empty_folder: bool = False
    ) -> bool:
        """
        Recursively traverse the directory structure up to max_depth, adding entries to flattened list.
        Returns True if any content was added (directory or matching files), False otherwise.
        """
        # Stop if we've exceeded max depth
        if current_depth > max_depth:
            return False

        has_content = False
        dir_entry = None

        # Try listing contents of the current directory
        try:
            entries = list(os.scandir(path))
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {path}: {e}")
            return
        except OSError as e:
            logger.error(f"Error accessing {path}: {e}")
            return

        # Filter out excluded directories
        dirs = []
        files = []
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                if entry.name not in exclude_dirs:
                    dirs.append(entry)
            else:
                files.append(entry)

        # Add file entries
        for file_entry in files:
            if file_filter is None or fnmatch.fnmatch(file_entry.name, file_filter):
                try:
                    stat = file_entry.stat()
                    flattened.append(entry_to_json(
                        path=file_entry.path,
                        entry_type="file",
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
                    ))
                    has_content = True
                except (PermissionError, OSError) as e:
                    logger.warning(f"Error accessing {file_entry.path}: {e}")

        # Recurse into directories
        for dir_entry in dirs:
            has_subdir_content = self._flatten_helper(
                dir_entry.path,
                exclude_dirs,
                flattened,
                current_depth=current_depth+1,
                max_depth=max_depth,
                file_filter=file_filter,
                hide_empty_folder=hide_empty_folder
            )
            has_content = has_content or has_subdir_content

        # Add current directory entry if it has content or we're not hiding empty folders
        if not hide_empty_folder or has_content:
            try:
                dir_stat = os.stat(path)
                flattened.append(entry_to_json(
                    path=path,
                    entry_type="directory",
                    size=0,
                    modified=datetime.fromtimestamp(dir_stat.st_mtime).isoformat()
                ))
            except (PermissionError, OSError) as e:
                logger.warning(f"Error accessing {path}: {e}")
                return has_content

        return has_content
