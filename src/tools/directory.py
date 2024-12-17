# /home/lutz/PycharmProjects/codesearch/src/tools/directory.py

import fnmatch
import logging
import os
from datetime import datetime
from typing import List, TypedDict, Optional

from .base import BaseTool
from ..shared import colored_print

logger = logging.getLogger(__name__)


class DirEntry(TypedDict):
    """Represents either a file or directory entry in a flattened structure."""
    type: str  # "file" or "directory"
    path: str
    size: int
    modified: str



class DirectoryPage(TypedDict):
    """Page of directory entries."""
    total_entries: int
    returned_entries: int
    entries: List[DirEntry]


class DirectoryTool(BaseTool):
    def print_verbose_output(self, result: DirectoryPage):
        """Print detailed directory scan results in yellow color"""
        for entry in result['entries']:
            entry_type = entry['type'].ljust(10)
            path = entry['path']
            size = f"size={entry['size']}"
            modified = f"modified={entry['modified']}"
            colored_print(f"{entry_type} {path} ({size}, {modified})", color="YELLOW")

    def get_tool_text_start(
        self, path: str, limit: int, max_depth: Optional[int], exclude_dirs: List[str], file_filter: Optional[str] = None, **kwargs
    ) -> List[str]:
        depth_str = f"max_depth: {max_depth}" if max_depth is not None else ""
        filter_str = f"file_filter: {file_filter}" if file_filter is not None else ""
        return [
            "Query directory",
            f"path: {path}",
            f"limit: {limit} entries",
            depth_str,
            f"exclude_dirs: {str(exclude_dirs)}",
            filter_str
        ]

    def get_tool_text_end(self, result: DirectoryPage) -> str:
        return f"total_entries: {result['total_entries']}, returned_entries: {result['returned_entries']}"

    def _run(
        self,
        path: str,
        limit: int = 50,
        max_depth: Optional[int] = None,
        exclude_dirs: List[str] = None,
        file_filter: Optional[str] = None,
        **kwargs
    ) -> DirectoryPage:
        """
        Return a flattened list of directory entries starting from a given path,
        limited by a maximum traversal depth and optionally excluding certain directories.

        :param path: The root directory to start traversal from.
        :param limit: The maximum number of entries to return.
        :param max_depth: The maximum depth of directories to recurse into.
                          If None, there is no depth limit.
        :param exclude_dirs: A list of directory names to exclude.
        """

        if max_depth is None:
            # If not specified, treat as unlimited depth.
            max_depth = 999999  # effectively no limit

        logger.info(
            f"Running directory tool with path: {path}, "
            f"limit: {limit}, max_depth: {max_depth}"
        )

        all_entries = []
        self._flatten_helper(path, exclude_dirs, all_entries, current_depth=0, max_depth=max_depth, file_filter=file_filter)

        total = len(all_entries)
        truncated = all_entries[:limit]

        result = {
            "total_entries": total,
            "returned_entries": len(truncated),
            "entries": truncated
        }
        logger.info(f"Directory entries (truncated to {limit}): {result}")
        return result

    def _flatten_helper(
        self,
        path: str,
        exclude_dirs: List[str],
        flattened: List[DirEntry],
        current_depth: int,
        max_depth: int,
        file_filter: Optional[str] = None
    ):
        """
        Recursively traverse the directory structure up to max_depth, adding entries to flattened list.

        :param path: Current directory path.
        :param exclude_dirs: Directories to exclude.
        :param flattened: The cumulative list of directory entries.
        :param current_depth: Current traversal depth.
        :param max_depth: Maximum depth allowed.
        """
        # Stop if we've exceeded max depth
        if current_depth > max_depth:
            return

        # Add current directory entry
        try:
            dir_stat = os.stat(path)
            flattened.append({
                "type": "directory",
                "path": path,
                "size": 0,
                "modified": datetime.fromtimestamp(dir_stat.st_mtime).isoformat()
            })
        except (PermissionError, OSError) as e:
            logger.warning(f"Error accessing {path}: {e}")
            return

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
                    flattened.append({
                        "type": "file",
                        "path": file_entry.path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except PermissionError as e:
                    logger.warning(
                        f"Permission denied accessing {file_entry.path}: {e}"
                    )
                    # Skip this file
                except OSError as e:
                    logger.error(f"Error accessing {file_entry.path}: {e}")
                    # Skip this file

        # Recurse into directories
        for dir_entry in dirs:
            self._flatten_helper(
                dir_entry.path,
                exclude_dirs,
                flattened,
                current_depth=current_depth+1,
                max_depth=max_depth,
                file_filter=file_filter
            )
