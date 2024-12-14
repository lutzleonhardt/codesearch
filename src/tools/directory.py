# /home/lutz/PycharmProjects/codesearch/src/tools/directory.py

import logging
import os
from datetime import datetime
from typing import List, TypedDict, Optional

from .base import BaseTool

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
    def get_tool_text_start(self, path: str, limit, max_depth: Optional[int], exclude_dirs: List[str], **kwargs) -> [str, str]:
        depth_str = f", max_depth: {max_depth}" if max_depth is not None else ""
        return [f"[Query directory]", f"path: {path}, limit: {limit} entries{depth_str}, exclude_dirs: {str(exclude_dirs)}"]

    def get_tool_text_end(self, result: DirectoryPage) -> str:
        return f"total_entries: {result['total_entries']}, returned_entries: {result['returned_entries']}"

    def _run(self, path: str, limit: int = 50, max_depth: Optional[int] = None, exclude_dirs: List[str] = None) -> DirectoryPage:
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

        logger.info(f"Running directory tool with path: {path}, limit: {limit}, max_depth: {max_depth}")

        all_entries = []
        self._flatten_helper(path, exclude_dirs, all_entries, current_depth=0, max_depth=max_depth)

        total = len(all_entries)
        truncated = all_entries[:limit]

        result = {
            "total_entries": total,
            "returned_entries": len(truncated),
            "entries": truncated
        }
        logger.info(f"Directory entries (truncated to {limit}): {result}")
        return result

    def _flatten_helper(self, path: str, exclude_dirs: List[str], flattened: List[DirEntry],
                        current_depth: int, max_depth: int):
        """
        Recursively traverse the directory structure up to max_depth, adding entries to flattened list.

        :param path: Current directory path.
        :param exclude_dirs: Directories to exclude.
        :param flattened: The cumulative list of directory entries.
        :param current_depth: Current traversal depth.
        :param max_depth: Maximum depth allowed.
        """
        # Add current directory entry
        try:
            dir_stat = os.stat(path)
            flattened.append({
                "type": "directory",
                "path": path,
                "size": 0,
                "modified": datetime.fromtimestamp(dir_stat.st_mtime).isoformat()
            })
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {path}: {e}")
            return
        except OSError as e:
            logger.error(f"Error accessing {path}: {e}")
            return

        # If we've reached max depth, don't go deeper
        if current_depth >= max_depth:
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
            try:
                stat = file_entry.stat()
                flattened.append({
                    "type": "file",
                    "path": file_entry.path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except PermissionError as e:
                logger.warning(f"Permission denied accessing {file_entry.path}: {e}")
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
                max_depth=max_depth
            )
