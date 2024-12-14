import logging
import os
from typing import List, Dict, Any
from .base import BaseTool

logger = logging.getLogger(__name__)

class DirectoryTool(BaseTool):
    def run(self, path: str, exclude_dirs: List[str] = None) -> Dict[str, Any]:
        """
        Recursively retrieve the directory structure starting from a given path.

        :param path: The directory path to scan.
        :param exclude_dirs: A list of directory names to exclude from scanning.
        :return: A dictionary representing the directory structure.
        """
        if exclude_dirs is None:
            # You can tweak the default excludes as needed.
            exclude_dirs = ["node_modules", "venv", "bin", "dist", ".git", ".svn", "__pycache__"]

        logger.info(f"Running directory tool with path: {path}")
        structure = self._get_structure(path, exclude_dirs)
        logger.info(f"Directory structure: {structure}")
        return structure

    def _get_structure(self, path: str, exclude_dirs: List[str]) -> Dict[str, Any]:
        """
        Recursively scan a directory structure.

        :param path: The directory path to scan.
        :param exclude_dirs: A list of directory names to exclude.
        :return: A dictionary with keys:
                    - 'type': 'directory' or 'file'
                    - 'name': directory or file name
                    - 'children': (if directory) list of nested structures
        """
        # The base structure of any directory node.
        structure = {
            "type": "directory",
            "name": os.path.basename(path),
            "children": []
        }

        try:
            entries = list(os.scandir(path))
            # Sort entries by name for consistency.
            entries.sort(key=lambda e: e.name.lower())

            for entry in entries:
                # Skip excluded directories.
                if entry.is_dir() and entry.name in exclude_dirs:
                    logger.debug(f"Excluding directory: {entry.path}")
                    continue

                if entry.is_file():
                    # If it's a file, just append a file structure.
                    structure["children"].append({
                        "type": "file",
                        "name": entry.name
                    })
                elif entry.is_dir():
                    # If it's a directory, recurse.
                    child_structure = self._get_structure(entry.path, exclude_dirs)
                    structure["children"].append(child_structure)
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {path}: {e}")
        except OSError as e:
            logger.error(f"Error accessing {path}: {e}")

        return structure
