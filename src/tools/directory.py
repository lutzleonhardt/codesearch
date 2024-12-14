from .base import BaseTool
import os

class DirectoryTool(BaseTool):
    def run(self, path: str):
        return self._get_structure(path)

    def _get_structure(self, path: str):
        structure = {"path": path, "dirs": [], "files": []}
        for entry in os.scandir(path):
            if entry.is_file():
                structure["files"].append(entry.name)
            elif entry.is_dir():
                structure["dirs"].append(self._get_structure(entry.path))
        return structure
